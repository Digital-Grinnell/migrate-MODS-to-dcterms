# This script will export a collection's worksheet/tab from our constant.GOOGLE_SHEET
# to an "expanded" 'values.csv' file in the local working directory.  That CSV, with multi-valued
# (using our | seperator convention) is then ready for ingest into Alma-Digital.
# 
## Google Docs API obtained using
#  https://developers.google.com/docs/api/quickstart/python?authuser=3
#
# See https://docs.python-guide.org/scenarios/xml/

# import community packages
import csv, time, os, argparse, gspread
from almapipy import AlmaCnxn as AlmaAPIConn

# import my packages
import my_data, my_colorama, constant

## createAlmaCollection( )
## Create a new sub-collection
# 
# https://developers.exlibrisgroup.com/alma/apis/bibs/

def createAlmaCollection(parent_collection_id, collection_name, collection_description):
  # Build a new collection in json 
  collection_json = {
                      "parent_pid": { 
                        "value": parent_collection_id
                      },
                      "name": collection_name,
                      "description": collection_description,
                      "sort_by": "desc",
                      "order": 1
                    }

  try:
    # collection_info = my_data.Data.alma_api.bibs.collections.get(collection_id)
    # print(collection_info, sep=' ', end='\n', flush=False)
    new_collection = my_data.Data.alma_api.bibs.collections.post(collection_json, record_format='dc')
    print(new_collection, sep=' ', end='\n', flush=False)
  except IOError as e:
    print('Operation failed: %s' % e.strerror)
    exit( )


# This function analyzes the mods.csv, looking for columns that need expansion
def analyze_csv(collection, csv_file, log_file):
  my_data.Data.collection_log_file.write("analyze_csv: Beginning analysis of collection '%s'\n" % collection)

  # setup to read from the CSV
  reader = csv.reader(csv_file)

  # Iterate over each row in the csv file using reader object
  for idx, row in enumerate(reader):
    # print(idx, row)

    # read the csv header and build dict keys using the headings
    if idx == 0:
      heading_list = row
      heading_counter = {key: 0 for key in row}
      # print(heading_counter)

    # for all other rows, count the number of bar (|) delimiters 
    # and set corresponding heading_counter key to that max number 
    else:
      for col, value in enumerate(row):
        if len(value) > 0:
          key = heading_list[col]
          parts = value.count('|') + 1
          if (parts > heading_counter[key]):
            heading_counter[key] = parts  
            my_data.Data.collection_log_file.write("Max width of column '%s' is now %s.\n" % (key, parts))

  sum = 0
  for c in heading_counter:
    sum = sum + max(heading_counter[c], 1)

  # print(heading_counter)
  my_data.Data.collection_log_file.write("analyze_csv: Done. Total number of column headings in expanded CSV will be %s\n" % sum)
  return heading_counter
    
  # ## The Google Sheet stuff...

  # sa = gspread.service_account()
  # sh = sa.open_by_url('https://docs.google.com/spreadsheets/d/1JzW8TGU8qJlBAlyoMyDS1mkLTGoaLrsCzVtwQo-4JlU/edit#gid=0')

  # try:
  #   wks = sh.worksheet(collection)
  # except:
  #   log_file.write('WorksheetOperation failed, collection worksheet "%s" does not exist.' % collection)
  #   wks = sh.add_worksheet(title=collection, rows=10, cols=20)
  #   log_file.write('  A new collection worksheet "%s" has been created.' % collection)

  # # read the CSV contents
  # csvContents = csv_file.read( )

  # # clear the sheet before importing the CSV contents
  # wks.clear( )

  # # write the CSV to the open worksheet per 
  # # https://stackoverflow.com/questions/73381107/how-to-append-a-new-worksheet-and-upload-a-local-csv-in-gspread
  
  # try:

  #   body = {
  #     "requests": [
  #       {
  #           "pasteData": {
  #               "coordinate": {
  #                   "sheetId": wks.id,
  #               },
  #               "data": csvContents,
  #               "type": "PASTE_NORMAL",
  #               "delimiter": "\t",
  #           }
  #       },
  #     ]
  #   }

  #   sh.batch_update(body)

  # except Exception as e:
  #   print('Operation failed: %s' % e.strerror)
  #   log_file.write('CSV write to collection worksheet "%s" failed.' % collection)

  # # some examples of fetching data 
  # print('Rows: ', wks.row_count)
  # print('Cols: ', wks.col_count)

  # print(wks.acell('A9').value)
  # print(wks.cell(3, 4).value)
  # print(wks.get('A7:E9'))

  # close the log_file and the csv
  log_file.close( )
  csv_file.close( )

## === MAIN ======================================================================================

# Get the runtime args...
parser = argparse.ArgumentParser( )
parser.add_argument('--collection_path', '-cp', nargs=1,
  help="The local path of the collection to be processed", required=False, default="/collection_xml")
args = parser.parse_args( )

# Move (cd) to the collection_path directory and go
cwd = os.getcwd( )
collection_path = args.collection_path
try:
  os.chdir(collection_path[0])
except IOError as e:
  print('Operation failed: %s' % e.strerror)
  exit( )

collection = os.getcwd( ).rsplit('/', 1)[-1]

if constant.DEBUG:
  msg = "-- Now working in collection directory: %s" % collection
  my_colorama.blue(msg)

# csv_filename = 'mods.csv'
log_filename = collection + '-expansion.log'

# Open the Alma API
try: 
  my_data.Data.alma_api = AlmaAPIConn(constant.ALMA_API_KEY, data_format='json')
  if constant.DEBUG:
    msg = "\nAlma API connection is now open for collection: %s" % collection
    my_colorama.blue(msg)
except IOError as e:
  print('Operation failed: %s' % e.strerror)

# Open files for this collection and GO!
try:
  with open(log_filename, 'w') as my_data.Data.collection_log_file:
    current_time = time.strftime("%d-%b-%Y %H:%M", time.localtime( ))
    my_data.Data.collection_log_file.write("%s \n\n" % current_time)

    # Open the GOOGLE_SHEET's collection worksheet and dump it into a temporary CSV file 
    sa = gspread.service_account()
    sh = sa.open_by_url(constant.GOOGLE_SHEET)

    try:
      wks = sh.worksheet(collection)
    except:
      my_data.Data.collection_log_file.write('WorksheetOperation failed, collection worksheet "%s" does not exist or cannot be opened.' % collection)

    # Dump the open GOOGLE_SHEET collection worksheet to a temporary CSV file and open that
    # file to be analyzed
    with open(constant.TEMP_CSV, 'w+') as f:
      writer = csv.writer(f)
      writer.writerows(wks.get_all_values( ))
    f.close( )

    # Reopen our temporary CSV and GO!
    try:
      with open(constant.TEMP_CSV, 'r') as temp_file:
        my_data.Data.collection_log_file.write("Temporary CSV for collection '%s' has been reopened for reading \n" % collection)

        #------------------------------------------------------------------
        # Compound object post-processing... 
        # Turn a compound parent into a new collection with children as items within
        if "compound" in cModel:
          createAlmaCollection(user_collection, my_data.Data.title, my_data.Data.description)    # just testing

        # Analyze the CSV contents 
        counter = analyze_csv(collection, temp_file, my_data.Data.collection_log_file)
        temp_file.close( )
        my_data.Data.collection_log_file.write("%s is now closed.\n" % constant.TEMP_CSV)

    except IOError as e:
      print('Operation failed: %s' % e.strerror)

    headings = []
    
    # Open a new expanded CSV for writing
    expanded_filename = 'values.csv'   ## Alma-sense insists on using this name!
    with open(expanded_filename, 'w') as expanded_csv:
      csv_writer = csv.writer(expanded_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

      # Build a list of expanded columns, duplicating those with counter > 1
      for col in counter:
        k = counter[col]
        headings.append(col)   # Append one instance of EVERY column, empty or not!
        while k > 1:
          headings.append(col)
          k = k - 1

      my_data.Data.collection_log_file.write("New CSV file '%s' is open.\n" % expanded_filename)

      csv_writer.writerow(headings)
      new_num_columns = len(headings)
      my_data.Data.collection_log_file.write("%s headings written to the new CSV file.\n" % new_num_columns)

      # Convert the counter dict to hold first column positions for each csv heading
      first_col = [0]
      for c, col in enumerate(counter):
        k = max(counter[col], 1)
        first_col.append(first_col[c] + k)

      # csv_writer.writerow(first_col)

      # Reopen the temporary CSV file for reading
      with open(constant.TEMP_CSV, 'r') as csv_file:
        my_data.Data.collection_log_file.write("%s has been reopened.\n" % constant.TEMP_CSV)
        reader = csv.reader(csv_file)

        # Iterate over each row in the csv file using reader object
        # process each row of the csv, expanding cells that contain bar delimeters
        # and ignoring any columns that are completely empty

        for r, row in enumerate(reader):
          if r > 0:                       # skip the heading row, no longer needed
            new_row = [None] * (new_num_columns + 1)
            # iterate over columns in the row...
            for c, cell in enumerate(row):
              values = cell.split('|')
              f = first_col[c]
              for x, v in enumerate(values):
                new_row[f + x] = v

            csv_writer.writerow(new_row)

      csv_file.close( )
      expanded_csv.close( )      
      my_data.Data.collection_log_file.write("Done!\n")

      # Finish by suggesting the `aws s3...` commands that should be used 
      # as part of the Alma-D upload operation.
      cp = "aws s3 cp %s/OBJ/ s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5776525300004641/REPLACE-WITH-PROCESS-ID/ --recursive" % collection_path[0]
      ls = "aws s3 ls s3://na-test-st01.ext.exlibrisgroup.com/01GCL_INST/upload/5776525300004641/ --recursive"

      print( )
      msg = "Edit and use this 'aws s3...' copy command, in concert with the Alma Digital Uploader, to copy files to AWS storage for ingest: \n %s" % cp
      print(msg)
      my_data.Data.collection_log_file.write(msg + "\n")

      print( )
      msg = "Use this 'aws ls...' list command to check the status of files in AWS storage for ingest: \n %s" % ls
      print(msg)
      my_data.Data.collection_log_file.write(msg + "\n")

except IOError as e:
  print('Operation failed: %s' % e.strerror)

# Move (cd) back to the original working directory 
os.chdir(cwd)


