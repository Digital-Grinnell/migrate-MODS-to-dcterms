class Data:

  ## empty ordered dict of csv column headings from Digital_Grinnell_MODS_Master
  csv_row_structure = {
    'PID': '',
    'WORKSPACE': '',
    'Import_Index': '',
    'PARENT': '',
    'CMODEL': '',
    'SEQUENCE': '',
    'OBJ': '',
    'TRANSCRPT': '',
    'THUMBNAIL': '',
    'Title': '',
    'Alternative_Titles': '',
    'Personal_Names~Roles': '',
    'Corporate_Names~Roles': '',
    'Abstract': '',
    'Index_Date': '',
    'Date_Issued': '',
    'Date_Captured': '',
    'Other_Date~Display_Label': '',
    'Publisher': '',
    'Place_Of_Publication': '',
    'Public_Notes~Types': '',
    'Notes~Display_Label': '',
    'Dates_as_Notes~Display_Label': '',
    'Citations': '',
    'Table_of_Contents': '',
    'LCSH_Subjects': '',
    'Subjects_Names~Types': '',
    'Subjects_Geographic': '',
    'Subjects_Temporal': '',
    'Keywords': '',
    'Coordinate': '',
    'Related_Items~Types': '',
    'Type_of_Resource~AuthorityURI': '',
    'Genre~AuthorityURI': '',
    'Extent': '',
    'Form~AuthorityURI': '',
    'MIME_Type': '',
    'Digital_Origin': '',
    'Classifications~Authorities': '',
    'Language_Names~Codes': '',
    'Local_Identifier': '',
    'Handle': '',
    'Physical_Location': '',
    'Shelf_Locator': '',
    'Access_Condition': '',
    'Import_Source': '',
    'Primary_Sort': '',
    'Hidden_Creator': '',
    'Pull_Quotes': '',
    'Private_Notes~Types': ''
  }

  ## ordered list of csv column headings from Digital_Grinnell_MODS_Master
  csv_headings = [
    'PID',
    'WORKSPACE',
    'Import_Index',
    'PARENT',
    'CMODEL',
    'SEQUENCE',
    'OBJ',
    'TRANSCRPT',
    'THUMBNAIL',
    'Title',
    'Alternative_Titles',
    'Personal_Names~Roles',
    'Corporate_Names~Roles',
    'Abstract',
    'Index_Date',
    'Date_Issued',
    'Date_Captured',
    'Other_Date~Display_Label',
    'Publisher',
    'Place_Of_Publication',
    'Public_Notes~Types',
    'Notes~Display_Label',
    'Dates_as_Notes~Display_Label',
    'Citations',
    'Table_of_Contents',
    'LCSH_Subjects',
    'Subjects_Names~Types',
    'Subjects_Geographic',
    'Subjects_Temporal',
    'Keywords',
    'Coordinate',
    'Related_Items~Types',
    'Type_of_Resource~AuthorityURI',
    'Genre~AuthorityURI',
    'Extent',
    'Form~AuthorityURI',
    'MIME_Type',
    'Digital_Origin',
    'Classifications~Authorities',
    'Language_Names~Codes',
    'Local_Identifier',
    'Handle',
    'Physical_Location',
    'Shelf_Locator',
    'Access_Condition',
    'Import_Source',
    'Primary_Sort',
    'Hidden_Creator',
    'Pull_Quotes',
    'Private_Notes~Types'
  ]


  ## global csv_row
  csv_row = ['']*len(csv_headings)

  ## global filenames and files

  collection_log_filename = ''
  collection_log_file = None

  object_log_filename = ''
  object_log_file = None


