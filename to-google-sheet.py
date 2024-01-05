# Run this script from a working directory that contains a collection's mods.csv file, 
# really a TSV (tab-delimited file) presumably exported from Digital.Grinnell.  The script will
# populate or create a worksheet/tab, with the same name as the collection, in our 
# constant.GOOGLE_SHEET.  Stakeholders should use that worksheet to review AND edit any data 
# that needs attention.  
# 
## Google Docs API obtained using
#  https://developers.google.com/docs/api/quickstart/python?authuser=3
#
# The target Google Sheet is specified in constant.GOOGLE_SHEET, currently: 
# https://docs.google.com/spreadsheets/d/1JzW8TGU8qJlBAlyoMyDS1mkLTGoaLrsCzVtwQo-4JlU
#
# import community packages
import gspread, gspread_formatting, time, os, argparse, pandas
import gspread_formatting as gsf

# import my packages
import my_data, my_colorama, constant

# Return integer if string is a valid integer
def is_int(t):
  text = str(t)
  if text.isalpha():
    return False
  try:
    return int(text)
  except ValueError:
    return False

# apply_special_rules( )
def apply_special_rules(collection, csv_filename, log_file):
  df = pandas.read_csv(csv_filename)

  # Iterate through the Pandas dataframe
  for index, row in df.iterrows( ):

    # Rule: Remove values from `dc:identifier` that exactly match `originating_system_id`
    osi = str(row['originating_system_id'])
    dci = str(row['dc:identifier'])
    if osi in dci:
      new_id = dci.replace(osi, "")
      df.at[index, "dc:identifier"] = new_id

  df.to_csv(csv_filename, index=False)    


# This function does nearly everything...
def collection_to_google(collection, csv_file, log_file):
  
  ## The Google Sheet stuff...
  sa = gspread.service_account()
  sh = sa.open_by_url(constant.GOOGLE_SHEET)

  try:
    wks = sh.worksheet(collection)
  except:
    log_file.write('WorksheetOperation failed, collection worksheet "%s" does not exist.' % collection)
    wks = sh.add_worksheet(title=collection, rows=10, cols=20)
    log_file.write('  A new collection worksheet "%s" has been created.' % collection)

  # Read the CSV contents
  csvContents = csv_file.read( )

  # Clear the sheet before importing the CSV contents
  wks.clear( )

  # Write the CSV to the open worksheet per 
  # https://stackoverflow.com/questions/73381107/how-to-append-a-new-worksheet-and-upload-a-local-csv-in-gspread
  
  try:

    body = {
      "requests": [
        {
            "pasteData": {
                "coordinate": {
                    "sheetId": wks.id,
                },
                "data": csvContents,
                "type": "PASTE_NORMAL",
                "delimiter": ","
            }
        },
      ]
    }

    sh.batch_update(body)

  except Exception as e:
    print('Operation failed: %s' % e.strerror)
    log_file.write('CSV write to collection worksheet "%s" failed.' % collection)

  # Some examples of fetching data 
  # print('Rows: ', wks.row_count)
  # print('Cols: ', wks.col_count)

  color = 'yellow'
  
  # Fill our Pandas dataframe so we don't have to keep reading from the Google Sheet
  df = pandas.read_csv(csv_filename)
  row_count = df.shape[0]
  all_rows_range = f"[(2:{row_count})]"

  # Format the heading row
  fmt = gsf.cellFormat(
    backgroundColor=gsf.color(0.8, 0.8, 0.8),
    textFormat=gsf.textFormat(bold=True)
    )
  gsf.format_cell_range(wks, '1', fmt)

  # Add a conditional formatting rule to highlight any cells containing "REPLACE ME"
  rule = gsf.ConditionalFormatRule(
    ranges=[gsf.GridRange.from_a1_range('2:*', wks)],
    booleanRule=gsf.BooleanRule(
      condition=gsf.BooleanCondition('TEXT_CONTAINS', ['REPLACE ME']),
      format=gsf.CellFormat(textFormat=gsf.textFormat(bold=True), backgroundColor=gsf.Color(0.8,0,0))
    )
  )

  rules = gsf.get_conditional_format_rules(wks)
  rules.clear( )
  rules.append(rule)
  
  # Add a conditional formatting rule to highlight any rows marked as "*PARENT*"
  rule = gsf.ConditionalFormatRule(
    ranges=[gsf.GridRange.from_a1_range('2:*', wks)],
    booleanRule=gsf.BooleanRule(
      condition=gsf.BooleanCondition('TEXT_EQ', ['*PARENT*']),
      format=gsf.CellFormat(textFormat=gsf.textFormat(bold=True), backgroundColor=gsf.Color(0.137,0.922,0.165))
    )
  )

  rules.append(rule)

  # Add a conditional formatting rule to highlight any rows marked as "*CHILD*"  
  rule = gsf.ConditionalFormatRule(
    ranges=[gsf.GridRange.from_a1_range('2:*', wks)],
    booleanRule=gsf.BooleanRule(
      condition=gsf.BooleanCondition('TEXT_EQ', ['*CHILD*']),
      format=gsf.CellFormat(textFormat=gsf.textFormat(bold=False), backgroundColor=gsf.Color(0.443,0.969,0.463))
    )
  )

  rules.append(rule)
  rules.save( )

  # # Let's format some of the rows to highlight compound objects
  # for r in range(2, row_count):
  #   row = df.iloc[r]
  #   if not pandas.isna(row.group_id):  # item's group_id is NOT NAN, it's part of a compound
  #     cid = is_int(row.collection_id)
  #     if cid:          # collection_id is an integer, this is a compound parent 
  #       color = 'yellow' if color == 'green' else 'green'
  #       wks.format(str(r), constant.ALTERNATING_COLORS[color][0])
  #     else:            # not a parent, must be a child of previous parent
  #       wks.format(str(r), constant.ALTERNATING_COLORS[color][1])

  # print(wks.acell('A9').value)
  # print(wks.cell(3, 4).value)
  # print(wks.get('A7:E9'))

  # Close the log_file and the csv
  log_file.close( )
  csv_file.close( )



## === MAIN ======================================================================================

# Get the runtime args...
parser = argparse.ArgumentParser( )
parser.add_argument('--collection_name', '-cn', nargs=1,
  help="The name of the collection to be processed and copied to the Google Sheet.", required=False, default=constant.COLLECTION_NAME)
args = parser.parse_args( )

collection = args.collection_name[0]

# Move (cd) to the local collection directory and go
cwd = os.getcwd( )
path = constant.OUTPUT_PATH + collection
try:
  os.chdir(path)
except IOError as e:
  print('Operation failed: %s' % e.strerror)
  exit( )

msg = "-- Now working in collection directory: %s" % collection
my_colorama.blue(msg)

# Open the mods.csv file 
csv_filename = 'mods.csv'
log_filename = collection + '-google.log'

# Open the collection log file
try:
  with open(log_filename, 'w') as my_data.Data.collection_log_file:
    current_time = time.strftime("%d-%b-%Y %H:%M", time.localtime( ))
    my_data.Data.collection_log_file.write("Collection: %s    Time: %s \n\n" % (collection, current_time))
    
    # Apply special rules!
    try:
      current_time = time.strftime("%d-%b-%Y %H:%M", time.localtime( ))
      my_data.Data.collection_log_file.write("Calling apply_special_rules at %s \n\n" % current_time)
      apply_special_rules(collection, csv_filename, my_data.Data.collection_log_file)
    except IOError as e:
      print('Operation failed: %s' % e.strerror)

    # Open files for this collection and GO!
    try:
      with open(csv_filename, 'r') as csv_file:
        current_time = time.strftime("%d-%b-%Y %H:%M", time.localtime( ))
        my_data.Data.collection_log_file.write("Calling collection_to_google at %s \n\n" % current_time)
        collection_to_google(collection, csv_file, my_data.Data.collection_log_file)
    except IOError as e:
      print('Operation failed: %s' % e.strerror)

except IOError as e:
  print('Operation failed: %s' % e.strerror)

# Move (cd) back to the original working directory 
os.chdir(cwd)
