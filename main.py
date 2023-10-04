# Run this script from a working directory that contains a collection's exported MODS.xml files.
# 
## Google Docs API obtained using
#  https://developers.google.com/docs/api/quickstart/python?authuser=3

# See https://docs.python-guide.org/scenarios/xml/

# import community packages
import os, glob, xmltodict, mimetypes, argparse

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

def process_collection(collection, collection_id, csv_file, collection_log_file):  # do everything related to a specified collection
  import csv, my_data, mods, json, time, tempfile
  
  import_index = 0;

  csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  csv_writer.writerow(my_data.Data.csv_headings)

  # loop on each .xml file in this collection directory; each .xml file represents one row in the csv
  for xml_filename in glob.glob('*.xml'):
    my_data.Data.object_log_filename = xml_filename.replace('.xml', '.log')
    my_data.Data.csv_row = ['']*len(my_data.Data.csv_headings)   # initialize the global csv_row to an empty list

    pid = getPID(xml_filename)          # get the object PID
    mods.process_simple(pid, 'originating_system_id')       # write it to csv_row ### !Map
    mods.process_simple(constant.HREF + pid, 'link-to-DG')  # write active link to Digital.Grinnell 

    # this code does not work...nearly impossible to open a local file from a Google Sheet
    # log_file_link = './' + pid.replace(':','_') + '_MODS.log'
    # mods.process_simple(log_file_link, 'SEQUENCE')        # write file: link to the object log file into 'SEQUENCE'

    parent = collection_id                           # save the parent collection id
    mods.process_simple(parent, 'collection_id')     # write it to csv_row  ### !Map

    my_data.Data.object_log_file = open(my_data.Data.object_log_filename, 'w')
    current_time = time.strftime("%d-%b-%Y %H:%M", time.localtime( ))
    my_data.Data.object_log_file.write("Object PID: %s   %s \n\n" % (pid, current_time))

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

      


      # Processing for specific MODS fields begins here... 
      # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

      # abstract: process simple, single top-level element
      if 'abstract' in doc['mods']:
        if is_mapped('abstract'):
          ok = mods.process_simple(doc['mods']['abstract'], 'dcterms:abstract')  ### !Map
          if ok:
            doc['mods']['abstract'] = ok

      # accessCondition: process simple, single top-level element
      if 'accessCondition' in doc['mods']:
        if is_mapped('accessCondition'):
          ok = mods.process_simple(doc['mods']['accessCondition'], 'dcterms:rights')  ### !Map
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
        if is_mapped('genre'):
          ok = mods.process_multi(doc['mods']['genre'],'dc:type')
          if ok:
            doc['mods']['genre'] = ok

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

      # titleInfo: process all top-level 'titleInfo' elements.  May be a dict of elements, or a list of dicts
      if 'titleInfo' in doc['mods']:
        if is_mapped('titleInfo'):
          if type(doc['mods']['titleInfo']) is list:
            ok = mods.process_list_dict(doc['mods']['titleInfo'], mods.titleInfo_action)
          else:
            ok = mods.process_dict(doc['mods']['titleInfo'], mods.titleInfo_action)
          if ok:
            doc['mods']['titleInfo'] = ok

      # typeOfResource: process simple, single top-level element
      if 'typeOfResource' in doc['mods']:
        if is_mapped('typeOfResource'):
          DCMI = mods.make_DCMIType(doc['mods']['typeOfResource'])
          if DCMI:
            ok = mods.process_simple(DCMI, 'dcterms:type.dcterms:DCMIType')    ### !Map
          if ok:
            doc['mods']['typeOfResource'] = ok
  
      # add a link to this object's .log file into log-file-link
      col = mods.column('log-file-link')
      my_data.Data.csv_row[col] = my_data.Data.object_log_filename
      
      # increment and add import_index to import-index column
      col = mods.column('import-index')
      import_index += 1
      my_data.Data.csv_row[col] = import_index

      # all done with processing... write out the csv_row[]
      csv_writer.writerow(my_data.Data.csv_row)

      # print what's left of 'doc'
      msg = "Transform results are: "
      if constant.DEBUG:
        my_colorama.cyan('------ ' + msg)
      my_data.Data.object_log_file.write( '\n' + msg + '\n')

      if constant.DEBUG:
        my_colorama.code(True)
        mods.prt(doc)
        my_colorama.code(False)

      my_data.Data.object_log_file.write(json.dumps(doc, sort_keys=True, indent=2))

      # print what's left of doc['mods'] to a temporary tmp file
      tmp = tempfile.TemporaryFile('w+')
      tmp.write(json.dumps(doc['mods'], sort_keys=True, indent=2))
      
    # close the object_log_file
    my_data.Data.object_log_file.close()

    # produce a .clean file from the object's tmp file
    mods.cleanup(tmp)

  # close the CSV file
  csv_file.close( )



## === MAIN ======================================================================================

# Get the runtime args...
parser = argparse.ArgumentParser( )
parser.add_argument('--collection_path', '-cp', nargs=1,
  help="The path to the collection's exported MODS .xml files", required=False, default="/collection_xml")
parser.add_argument('--collection_id', '-id', nargs=1,
  help="The numeric Alma (MMS) id of the parent collection", required=False, default="81294713150004641")
args = parser.parse_args( )

# cd to the collection_path directory and go
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

# declare new files to be written
csv_filename = 'mods.csv'
my_data.Data.collection_log_filename = 'collection.log'

# open files for this collection and GO!
try:
  with open(csv_filename, 'w', newline='') as csv_file, open(my_data.Data.collection_log_filename, 'w') as my_data.Data.collection_log_file:
    process_collection(collection, collection_id, csv_file, my_data.Data.collection_log_file)
except IOError as e:
  print('Operation failed: %s' % e.strerror)

# cd back to the original working directory 
os.chdir(cwd)
