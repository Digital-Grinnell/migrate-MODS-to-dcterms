# Run this script and specify a '--collection_path' argument pointing to a directory that contains 
# a collection's '<object>_MODS.xml' files, one for each object in the collection.  The script will
# examine each '<object>_MODS.xml' within, generating a '.log' and '.remainder' pair of files for each. 
# The principal function of the script is to create a new 'mods.csv' file which forms the basis for creation
# of a 'values.csv' (see the 'to-google-sheet.py' and 'expand-csv.py' scripts) file for import into Alma-D.  
# 
# If the '--collection_path' directory has an `OBJ` subdirectory the script will look for 'OBJ' and 'TN' 
# content files (also exported from Digital.Grinnell).  Each '<object>_TN.*' file will be renamed per the
# Alma-D convention to match the name of the corresponding `OBJ` file, but with a '.clientThumb' extension 
# added.  The script will also generate an 'aws s3...' command suitable for copying the 'OBJ' subdirectory
# contents to our appropriate Amazon S3 ingest storage.   

## Google Docs API obtained using
#  https://developers.google.com/docs/api/quickstart/python?authuser=3

# See https://docs.python-guide.org/scenarios/xml/

# import community packages
import os, glob, xmltodict, mimetypes, argparse, pandas

# import my packages
import my_data, my_colorama, mods, constant

# initialize the mimetypes package
mimetypes.init( )

## --- Functions ---------------------------------------------------------------------------------


## getPID( ) ---------------------------------------------------------------
## Turn an XML filename/path into a PID

def getPID(path):
  import os
  [ head, tail ] = os.path.split(path)
  parts = tail.split('_')
  pid = parts[0] + ":" + parts[1]
  return pid


## getCollectionPID( ) ---------------------------------------------------------------
## Turn an XML filename/path into a collection PID

def getCollectionPID(path):
  import os
  [ head, tail ] = os.path.split(path)
  pid = 'grinnell:' + tail
  return pid


## pretty_xml ------------------------------------------------------
## Based on https://codeblogmoney.com/xml-pretty-print-using-python-with-examples/

def pretty_xml(filename):
  import xml.dom.minidom
  with open(filename) as xmldata:
    xml = xml.dom.minidom.parseString(xmldata.read())  # or xml.dom.minidom.parseString(xml_string)
    xml_pretty_str = xml.toprettyxml()
  return xml_pretty_str


def clean(x):
  x1 = x.replace('mods:', '')
  x2 = x1.replace(':href', '')
  return x2

## is_mapped(field) ---------------------------------------------------------------
## Checks if field is or is "not_mapped" and returns True or False

def is_mapped(field):
  if field in my_data.Data.not_mapped:
    mods.skip(field)
    return False
  else:
    return True

## check_special(collection, field) ---------------------------------------------------------------
## Checks if field is "not_mapped" or returns any special handling target for a particular collection and field

def check_special(collection, field):
  if is_mapped(field):
    if collection in my_data.Data.special_handling.keys():
      rules = my_data.Data.special_handling[collection]
      if field in rules.keys():
        return rules[field]
  return False  


# Ok, this is where the rubber meets the road!  Modified in Fall 2023 for output to an Alma-D dcterms 
# compatible .csv export !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# See https://docs.google.com/spreadsheets/d/1rw9osrvGSg9fIQnQzCCILn-66mDOMD2VttT-yYkQH4E/ for mapping details.
# Lines below that reflect mapping are tagged with '### !Map'

def process_collection(collection, collection_id, csv_file, collection_log_file):  # do everything for specified collection
  import csv, my_data, mods, json, time, tempfile
  
  import_index = 0;

  csv_writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_MINIMAL)
  csv_writer.writerow(my_data.Data.csv_headings)

  # Grab a glob of all the *.xml files in the collection directory; each .xml file will become one row in the csv
  xml_files = glob.glob('*.xml')

  # loop on each glob'd file...
  for xml_filename in xml_files:
    my_data.Data.object_log_filename = xml_filename.replace('.xml', '.log')
    my_data.Data.csv_row = ['']*len(my_data.Data.csv_headings)   # initialize the global csv_row to an empty list

    pid = getPID(xml_filename)          # get the object PID
    mods.process_simple(pid, 'originating_system_id')       # write it to csv_row ### !Map

    user_collection = collection_id[0]                        # save the user specified ID of the parent collection

    my_data.Data.object_log_file = open(my_data.Data.object_log_filename, 'w')
    current_time = time.strftime("%d-%b-%Y %H:%M", time.localtime( ))
    my_data.Data.object_log_file.write("Object PID: %s   %s \n\n" % (pid, current_time))

    # Look for the object's corresponding *_RELS-EXT.rdf file.  
    # If found, fetch any hasModel and isConstituentOf elements so we know if we need to do
    # any compound/child object handling
    rdf_filename = xml_filename.replace('.xml', '.rdf').replace('MODS', 'RELS-EXT')
    found = False

    # Open the RELS-EXT file and parse it looking for key information
    with open(rdf_filename, 'r') as rdf_file:
      my_data.Data.object_log_file.write("Found RELS-EXT file: %s \n" % rdf_filename)
      found = True
      rdf_string = clean(rdf_file.read())
      doc = xmltodict.parse(rdf_string)

      if 'fedora:isConstituentOf' in doc['rdf:RDF']['rdf:Description']:
        has_compound_parent = doc['rdf:RDF']['rdf:Description']['fedora:isConstituentOf']['@rdf:resource']
        has_compound_parent_parts = has_compound_parent.split("/")
        has_compound_parent = has_compound_parent_parts[-1]
        mods.process_simple(has_compound_parent, 'collection_id')     # write it to csv_row  ### !Map
      else:
        has_compound_parent = False  
        mods.process_simple(user_collection, 'collection_id')     # write it to csv_row  ### !Map

      if 'fedora-model:hasModel' in doc['rdf:RDF']['rdf:Description']:
        cModel = doc['rdf:RDF']['rdf:Description']['fedora-model:hasModel']['@rdf:resource']
        cModel_parts = cModel.split(":")
        cModel = cModel_parts[-1]
      else: 
        cModel = False  

    if not found:
      my_data.Data.object_log_file.write("NO %s RELS-EXT file found!\n" % rdf_file)

    #------------------------------------------------------------------
    # Open the MODS .xml and begin processing the metadata
    with open(xml_filename, 'r') as xml_file:
      current_time = time.strftime("%d-%b-%Y %H:%M", time.localtime())
      msg = "Processing file: %s" % xml_filename
      if constant.DEBUG:
        my_colorama.blue('---- ' + msg)
      collection_log_file.write('%s    %s \n' % (msg, current_time))

      xml_string = clean(xml_file.read())
      doc = xmltodict.parse(xml_string)
          # process_namespaces=True,
          # namespaces=[ {'http://www.loc.gov/mods/v3':None},
          #              {'http://www.w3.org/1999/xlink':None} ])  # parse the xml into a 'doc' nested OrderedDict

      if constant.DEBUG:
        import json
        print(json.dumps(doc['mods'], sort_keys=True, indent=2))

      # Assume we have NO mods:genre OR mods:typeOfResource
      has_genre = False    # assume we have no mods:genre element
      ok = mods.process_simple(constant.REPLACE_ME, 'dc:type', replace=True)          ### !Map

      # Processing for specific MODS fields begins here... 
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      # 'title' and 'abstract' are buffered for later use so they MUST COME FIRST in this block of code!
      # Initialize their buffers to False
      my_data.Data.title = False
      my_data.Data.description = False

      # titleInfo: process all top-level 'titleInfo' elements.  May be a dict of elements, or a list of dicts
      if 'titleInfo' in doc['mods']:
        if is_mapped('titleInfo'):
          if type(doc['mods']['titleInfo']) is list:
            ok = mods.process_list_dict(doc['mods']['titleInfo'], mods.titleInfo_action)
          else:
            ok = mods.process_dict(doc['mods']['titleInfo'], mods.titleInfo_action)
          if ok:
            doc['mods']['titleInfo'] = ok
            tcol = mods.column('dc:title')
            my_data.Data.title = my_data.Data.csv_row[tcol]

          # If this object is a compound child, move the dc:title to rep_label AND file_label_1, 
          # and blank out the dc:title
          if has_compound_parent:
            tcol = mods.column('dc:title')
            mods.process_simple(my_data.Data.csv_row[tcol], 'rep_label')        ### !Map
            mods.process_simple(my_data.Data.csv_row[tcol], 'file_label_1')     ### !Map
            mods.single('dc:title', '', replace=True)                           ### !Map

      # abstract: process simple, single top-level element
      if 'abstract' in doc['mods']:
        if is_mapped('abstract'):
          ok = mods.process_simple(doc['mods']['abstract'], 'dcterms:abstract')  ### !Map
          if ok:
            doc['mods']['abstract'] = ok
            dcol = mods.column('dc:description')
            my_data.Data.description = my_data.Data.csv_row[dcol]

      ## Order of remaining MODS elements here is NOT significant

      # accessCondition: process simple, single top-level element
      if 'accessCondition' in doc['mods']:
        if is_mapped('accessCondition'):
          ok = mods.process_simple(doc['mods']['accessCondition'], 'dc:rights')  ### !Map
          if ok:
            doc['mods']['accessCondition'] = ok

      # classification: process one or more top-level 'classification' elements
      if 'classification' in doc['mods']:
        if is_mapped('classification'):
          if type(doc['mods']['classification']) is list:
            ok = mods.process_list_dict(doc['mods']['classification'], mods.classification_action)
          else:
            ok = mods.process_dict(doc['mods']['classification'], mods.classification_action)
          if ok:
            doc['mods']['classification'] = ok

      # extension: process one or more top-level 'extension' elements
      if 'extension' in doc['mods']:
        if is_mapped('extension'):
          if type(doc['mods']['extension']) is list:
            ok = mods.process_list_dict(doc['mods']['extension'], mods.extension_action)
          else:
            ok = mods.process_dict(doc['mods']['extension'], mods.extension_action)
          if ok:
            doc['mods']['extension'] = ok

      # genre: process simple, single top-level element
      if 'genre' in doc['mods']:
        ok = False
        g = doc['mods']['genre']
        if is_mapped('genre'):
          if type(doc['mods']['genre']) is dict:
            term = g['#text']
            DCMI = mods.check_DCMITypes(term)
          else:
            term = g
            DCMI = mods.check_DCMITypes(g['#text'])
          if DCMI:
            (term, score) = DCMI
            ok = mods.process_multi(term, 'dcterms:type.dcterms:DCMIType')    ### !Map
          resource_type = mods.map_resource_type(term)
          if resource_type:
            ok = mods.process_simple(resource_type[0], 'dc:type', replace=True)           ### !Map

        if ok:
          doc['mods']['genre'] = ok
          has_genre = True

      # identifier: process one or more top-level 'identifier' elements
      if 'identifier' in doc['mods']:
        if is_mapped('identifier'):
          if type(doc['mods']['identifier']) is list:
            ok = mods.process_list_dict(doc['mods']['identifier'], mods.identifier_action)
          else:
            ok = mods.process_dict(doc['mods']['identifier'], mods.identifier_action)
          if ok:
            doc['mods']['identifier'] = ok

      # language: process all top-level 'language' elements
      if 'language' in doc['mods']:
        if is_mapped('language'):
          ok = mods.process_dict_list(doc['mods']['language'], mods.language_action)
        if ok:
          doc['mods']['identifier'] = ok

      # location: process one or more top-level 'location' elements
      if 'location' in doc['mods']:
        if is_mapped('location'):
          if type(doc['mods']['location']) is list:
            ok = mods.process_list_dict(doc['mods']['location'], mods.location_action)
          else:
            ok = mods.process_dict(doc['mods']['location'], mods.location_action)
          if ok:
            doc['mods']['location'] = ok

      # name: process one or more top-level 'name' elements
      if 'name' in doc['mods']:
        if is_mapped('name'):
          if type(doc['mods']['name']) is list:
            ok = mods.process_list_dict(doc['mods']['name'], mods.name_action)
          else:
            ok = mods.process_dict(doc['mods']['name'], mods.name_action)
          if ok:
            doc['mods']['name'] = ok

      # note: process one or more top-level 'note' elements
      if 'note' in doc['mods']:
        if is_mapped('note'):
          if type(doc['mods']['note']) is list:
            ok = mods.process_list_dict(doc['mods']['note'], mods.note_action)
          else:
            ok = mods.process_dict(doc['mods']['note'], mods.note_action)
            if ok:
              doc['mods']['note'] = ok

      # originInfo: process all top-level 'originInfo' elements
      if 'originInfo' in doc['mods']:
        if is_mapped('originInfo'):
          mods.process_dict(doc['mods']['originInfo'], mods.originInfo_action)

      # physicalDescription: process all top-level 'physicalDescription' elements
      if 'physicalDescription' in doc['mods']:
        if is_mapped('physicalDescription'):
          if type(doc['mods']['physicalDescription']) is list:
            ok = mods.process_list_dict(doc['mods']['physicalDescription'], mods.physicalDescription_action)
          else:
            ok = mods.process_dict(doc['mods']['physicalDescription'], mods.physicalDescription_action)
          if ok:
            doc['mods']['physicalDescription'] = ok

      # relatedItem: process one or more top-level 'relatedItem' elements
      if 'relatedItem' in doc['mods']:
        if is_mapped('relatedItem'):
          if type(doc['mods']['relatedItem']) is list:
            ok = mods.process_list_dict(doc['mods']['relatedItem'], mods.relatedItem_action)
          else:
            ok = mods.process_dict(doc['mods']['relatedItem'], mods.relatedItem_action)
          if ok:
            doc['mods']['relatedItem'] = ok

      # subject: process one or more top-level 'subject' elements
      if 'subject' in doc['mods']:
        if is_mapped('subject'):
          if type(doc['mods']['subject']) is list:
            ok = mods.process_list_dict(doc['mods']['subject'], mods.subject_action)
          else:
            ok = mods.process_dict(doc['mods']['subject'], mods.subject_action)
          if ok:
            doc['mods']['subject'] = ok

      # typeOfResource: process simple, single top-level element
      if 'typeOfResource' in doc['mods']:
        t = doc['mods']['typeOfResource']
        if is_mapped('typeOfResource'):
          DCMI = mods.check_DCMITypes(t)
          if DCMI:
            (term, score) = DCMI
            ok = mods.process_multi(term, 'dcterms:type.dcterms:DCMIType')    ### !Map
          if ok:
            doc['mods']['typeOfResource'] = ok
          else:
            my_data.Data.object_log_file.write("No fuzzy match found in DCMITypes for '%s' \n" % t)

          if not has_genre:     # If we did not map mods:genre to dc:type, we must map this value to dc:type
            resource_type = mods.map_resource_type(term)
            if resource_type:
              ok = mods.process_simple(resource_type[0], 'dc:type', replace=True)        ### !Map
  
      # # add a link to this object's .log file into log-file-link   !! This breaks the import!  Don't do it.
      # col = mods.column('log-file-link')
      # my_data.Data.csv_row[col] = my_data.Data.object_log_filename
      
      #-----------------------------------------------
      # Compound children as reps logic follows.
 
      # If the object has a compound parent, write that PID to the group_id.  Otherwise, if 
      # the object is a compound parent write the object's PID as the group_id.
      if has_compound_parent:
        mods.process_simple(has_compound_parent, 'group_id')        # write it to csv_row  ### !Map
      elif ('compound' in cModel): 
        mods.process_simple(pid, 'group_id')        # write it to csv_row  ### !Map

      # Look for the object's corresponding *_OBJ.<extension> file.  
      # If found, write the OBJ filename into the 'file_name_1' column
      obj_filename = xml_filename.replace('.xml', '.*').replace('MODS', 'OBJ')
      obj_path = "./OBJ/" + xml_filename.replace('.xml', '.*').replace('MODS', 'OBJ')
      found = False

      # Fetch and write the content filename to the .csv
      for obj_file in glob.glob(obj_path):
        if ".clientThumb" not in obj_file: 
          filename = os.path.basename(obj_file)
          found = True
          my_data.Data.object_log_file.write("Found OBJ file: %s   %s \n" % (obj_file, current_time))
          mods.process_simple(filename, 'file_name_1')     # write it to csv_row    ### !Map
    
      # If no OBJ is found AND this is not a compound parent... warn the user via the .csv file
      if not found and "compound" not in cModel:
        my_data.Data.object_log_file.write("NO %s OBJ file found!\n" % obj_path)
        mods.process_simple(constant.NO_FILE_ERROR, 'file_name_1')     # alert the CSV file    ### !Map

      # All done with processing... write out the csv_row[]
      csv_writer.writerow(my_data.Data.csv_row)

      # Print what's left of 'doc'
      msg = "Transform results are: "
      if constant.DEBUG:
        my_colorama.cyan('------ ' + msg)
      my_data.Data.object_log_file.write( '\n' + msg + '\n')

      if constant.DEBUG:
        my_colorama.code(True)
        mods.prt(doc)
        my_colorama.code(False)

      my_data.Data.object_log_file.write(json.dumps(doc, sort_keys=True, indent=2))

      # Print what's left of doc['mods'] to a temporary tmp file
      tmp = tempfile.TemporaryFile('w+')
      tmp.write(json.dumps(doc['mods'], sort_keys=True, indent=2))

    ## That is the end of the MODS field processing, now focus on the object's OBJ and TN files, if any.
    found = False
    for obj_file in glob.glob("./OBJ/*"):
      if "TN" in obj_file: 
        found = True
        tn_name = obj_file.replace('TN','OBJ') + ".clientThumb"
        os.rename(obj_file, tn_name)
        my_data.Data.object_log_file.write("\n\nFound TN file '%s' and renamed to '%s' \n" % (filename, tn_name))

    if not found:
      my_data.Data.object_log_file.write("\n\nNO TN file found for %s! \n" % pid)
      
    # Close the object_log_file
    my_data.Data.object_log_file.close()

    # Produce a .clean file from the object's tmp file
    mods.cleanup(tmp)

  ##### End of: for xml_filename in xml_files:

  # Close the CSV file, then sort it by group_id/collection_id. 
  csv_file.close( )
  dataFrame = pandas.read_csv("mods.csv")
  # Sort according to multiple columns
  dataFrame.sort_values(["group_id","collection_id"], axis=0, ascending=True, inplace=True, na_position='first')
  dataFrame.reset_index( )

  # Index the sorted sheet and write Google Sheet index/link to googlesheetsource column
  for index, row in dataFrame.iterrows( ):
    dataFrame.at[index, 'googlesheetsource'] = str(index) + str("  " + constant.GOOGLE_SHEET)

  # Save the modified dataframe to `mods.csv`
  dataFrame.to_csv('mods.csv', index=False)



## === MAIN ======================================================================================

# Get the runtime args...
parser = argparse.ArgumentParser( )
parser.add_argument('--collection_path', '-cp', nargs=1,
  help="The path to the collection's exported MODS .xml files", required=False, default="/Volumes/mcfatem/Migration-to-Alma/postcards")
parser.add_argument('--collection_id', '-id', nargs=1,
  help="The numeric Alma ID (NOT the MMS_ID) of the parent collection", required=False, default="81294713150004641")
args = parser.parse_args( )

# Move (cd) to the collection_path directory and go
cwd = os.getcwd( )
path = args.collection_path
try:
  os.chdir(path[0])
except IOError as e:
  print('Operation failed: %s' % e.strerror)
  exit( )

collection = os.getcwd( ).rsplit('/', 1)[-1]
collection_id = args.collection_id

if constant.DEBUG:
  msg = "-- Now working in collection directory: %s" % collection
  my_colorama.blue(msg)

# Declare new files to be written
csv_filename = 'mods.csv'
my_data.Data.collection_log_filename = 'collection.log'

# Open files for this collection and GO!
try:
  with open(csv_filename, 'w', newline='') as csv_file, open(my_data.Data.collection_log_filename, 'w') as my_data.Data.collection_log_file:
    process_collection(collection, collection_id, csv_file, my_data.Data.collection_log_file)
except IOError as e:
  print('Operation failed: %s' % e.strerror)

# cd back to the original working directory 
os.chdir(cwd)
