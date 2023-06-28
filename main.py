# Run this script from a working directory that contains a collection's exported MODS.xml files.
# 
## Google Docs API obtained using
#  https://developers.google.com/docs/api/quickstart/python?authuser=3

# See https://docs.python-guide.org/scenarios/xml/

# import community packages
import os, glob, xmltodict, mimetypes

# import my packages
import my_data, my_colorama, mods, constant

# initialize the mimetypes pacakge
mimetypes.init()

## --- Functions ---------------------------------------------------------------------------------

## getPID( ) ---------------------------------------------------------------
## Turn an XML filename/path into a PID

def getPID(path):
  import os
  [ head, tail ] = os.path.split(path)
  parts = tail.split('_')
  pid = parts[0] + ":" + parts[1]
  return pid


## getCollectoinPID( ) ---------------------------------------------------------------
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


def process_collection(collection, csv_file, collection_log_file):  # do everything related to a specified collection
  import csv, my_data, mods, json, time, tempfile
  
  import_index = 0;

  csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
  csv_writer.writerow(my_data.Data.csv_headings)

  # loop on each .xml file in this collection directory; each .xml file represents one row in the csv
  for xml_filename in glob.glob('*.xml'):
    my_data.Data.object_log_filename = xml_filename.replace('.xml', '.log')
    my_data.Data.csv_row = ['']*len(my_data.Data.csv_headings)   # initialize the global csv_row to an empty list

    pid = getPID(xml_filename)          # get the object PID
    mods.process_simple(pid, 'PID')     # write it to csv_row
    mods.process_simple(constant.HREF + pid, 'OBJ')        # write active link to Digital.Grinnell in the 'OBJ' column

    # this code does not work...nearly impossible to open a local file from a Google Sheet
    # log_file_link = './' + pid.replace(':','_') + '_MODS.log'
    # mods.process_simple(log_file_link, 'SEQUENCE')        # write file: link to the object log file into 'SEQUENCE'

    parent = getCollectionPID(collection)     # build the parent collection PID
    mods.process_simple(parent, 'PARENT')     # write it to csv_row

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

      # abstract: process simple, single top-level element
      if 'abstract' in doc['mods']:
        ok = mods.process_simple(doc['mods']['abstract'], 'Abstract')
        if ok:
          doc['mods']['abstract'] = ok

      # accessCondition: process simple, single top-level element
      if 'accessCondition' in doc['mods']:
        ok = mods.process_simple(doc['mods']['accessCondition'], 'Access_Condition')
        if ok:
          doc['mods']['accessCondition'] = ok

      # classification: process one or more top-level 'classification' elements
      if 'classification' in doc['mods']:
        if type(doc['mods']['classification']) is list:
          ok = mods.process_list_dict(doc['mods']['classification'], mods.classification_action)
        else:
          ok = mods.process_dict(doc['mods']['classification'], mods.classification_action)
          if ok:
           doc['mods']['classification'] = ok

      # extension: process one or more top-level 'extension' elements
      if 'extension' in doc['mods']:
        if type(doc['mods']['extension']) is list:
          ok = mods.process_list_dict(doc['mods']['extension'], mods.extension_action)
        else:
          ok = mods.process_dict(doc['mods']['extension'], mods.extension_action)
          if ok:
           doc['mods']['extension'] = ok

      # genre: process simple, single top-level element
      if 'genre' in doc['mods']:
        ok = mods.process_simple(doc['mods']['genre'], 'Genre~AuthorityURI')
        if ok:
          doc['mods']['genre'] = ok

      # identifier: process one or more top-level 'identifier' elements
      if 'identifier' in doc['mods']:
        if type(doc['mods']['identifier']) is list:
          ok = mods.process_list_dict(doc['mods']['identifier'], mods.identifier_action)
        else:
          ok = mods.process_dict(doc['mods']['identifier'], mods.identifier_action)
          if ok:
           doc['mods']['identifier'] = ok

      # language: process all top-level 'language' elements
      if 'language' in doc['mods']:
        mods.process_dict_list(doc['mods']['language'], mods.language_action)

      # name: process one or more top-level 'name' elements
      if 'name' in doc['mods']:
        if type(doc['mods']['name']) is list:
          ok = mods.process_list_dict(doc['mods']['name'], mods.name_action)
        else:
          ok = mods.process_dict(doc['mods']['name'], mods.name_action)
          if ok:
            doc['mods']['name'] = ok

      # note: process one or more top-level 'note' elements
      if 'note' in doc['mods']:
        if type(doc['mods']['note']) is list:
          ok = mods.process_list_dict(doc['mods']['note'], mods.note_action)
        else:
          ok = mods.process_dict(doc['mods']['note'], mods.note_action)
          if ok:
            doc['mods']['note'] = ok

      # originInfo: process all top-level 'originInfo' elements
      if 'originInfo' in doc['mods']:
        mods.process_dict(doc['mods']['originInfo'], mods.originInfo_action)

      # physicalDescription: process all top-level 'physicalDescription' elements
      if 'physicalDescription' in doc['mods']:
        mods.process_dict(doc['mods']['physicalDescription'], mods.physicalDescription_action)

      # relatedItem: process one or more top-level 'relatedItem' elements
      if 'relatedItem' in doc['mods']:
        if type(doc['mods']['relatedItem']) is list:
          ok = mods.process_list_dict(doc['mods']['relatedItem'], mods.relatedItem_action)
        else:
          ok = mods.process_dict(doc['mods']['relatedItem'], mods.relatedItem_action)
          if ok:
           doc['mods']['relatedItem'] = ok

      # subject: process one or more top-level 'subject' elements
      if 'subject' in doc['mods']:
        if type(doc['mods']['subject']) is list:
          ok = mods.process_list_dict(doc['mods']['subject'], mods.subject_action)
        else:
          ok = mods.process_dict(doc['mods']['subject'], mods.subject_action)
          if ok:
            doc['mods']['subject'] = ok

      # titleInfo: process all top-level 'titleInfo' elements.  May be a dict of elements, or a list of dicts
      if 'titleInfo' in doc['mods']:
        if type(doc['mods']['titleInfo']) is list:
          ok = mods.process_list_dict(doc['mods']['titleInfo'], mods.titleInfo_action)
        else:
          ok = mods.process_dict(doc['mods']['titleInfo'], mods.titleInfo_action)
        if ok:
          doc['mods']['titleInfo'] = ok

      # typeOfResource: process simple, single top-level element
      if 'typeOfResource' in doc['mods']:
        ok = mods.process_simple(doc['mods']['typeOfResource'], 'Type_of_Resource~AuthorityURI')
        if ok:
          doc['mods']['typeOfResource'] = ok

      # add a link to this object's .log file into WORKSPACE
      col = mods.column('WORKSPACE')
      my_data.Data.csv_row[col] = my_data.Data.object_log_filename
      
      # increment and add import_index to Import_Index column
      col = mods.column('Import_Index')
      import_index += 1
      my_data.Data.csv_row[col] = import_index

      # all done with processing... write out the csv_row[]
      csv_writer.writerow(my_data.Data.csv_row)

      # print what's left of 'doc'
      msg = "Remaining elements are: "
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

# Run this script from a working directory that contains a collection's exported MODS.xml files.

collection = os.getcwd().rsplit('/', 1)[-1]

if constant.DEBUG:
  msg = "-- Now working in collection directory: %s" % collection
  my_colorama.blue(msg)

# declare new files to be written
csv_filename = 'mods.csv'
my_data.Data.collection_log_filename = 'collection.log'

# open files for this collection and GO!
try:
  with open(csv_filename, 'w', newline='') as csv_file, open(my_data.Data.collection_log_filename, 'w') as my_data.Data.collection_log_file:
    process_collection(collection, csv_file, my_data.Data.collection_log_file)
except IOError as e:
  print('Operation failed: %s' % e.strerror)

