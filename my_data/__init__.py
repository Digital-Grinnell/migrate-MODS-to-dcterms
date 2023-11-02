class Data:

  ## Special handling per collection - informs the script about special handling
  ## situations on a collection-by-collection basis   NOT CURRENTLY USED!

  special_handling = {
    'postcards': [{ 'classification': 'dc:identifier' }]
  }

  ## List of MODS types that are not yet mapped to Alma
  not_mapped = [
    'classification',
    'extension'
  ]

  ## Ordered list of csv column headings for Alma-D   These MUST ALL BE IN OUR PROFILE otherwise
  ## we will be plagued with validation errors!
  csv_headings = [
    'group_id',
    'collection_id',
    'mms_id',
    'originating_system_id',
    'dc:title',
    'dcterms:alternative',
    'dc:creator',
    'dc:contributor',
    'dc:subject',
    'dcterms:subject.dcterms:LCSH',
    'dc:description',
    'dcterms:bibliographicCitation',
    'dcterms:abstract',
    'dcterms:publisher',
    'dc:date',
    'dcterms:created',
    'dcterms:issued',
    'dcterms:dateSubmitted',
    'dcterms:dateAccepted',
    'dc:type',
    'dc:format',
    'dcterms:extent',
    'dcterms:medium',
    'dcterms:format.dcterms:IMT',
    'dcterms:type.dcterms:DCMIType',
    'dc:identifier',
    'dcterms:identifier.dcterms:URI',
    'dc:language',
    'dc:relation',
    'dcterms:isPartOf',
    'dc:coverage',
    'dcterms:spatial',
    'dcterms:spatial.dcterms:Point',
    'dcterms:temporal',
    'dc:rights',
    'dc:source',
    'bib custom field',
    'rep_label',
    'rep_public_note',
    'rep_access_rights',
    'rep_usage_type',
    'rep_library',
    'rep_note',
    'rep_custom field',
    'file_name_1',
    'file_label_1',
    'file_name_2',
    'file_label_2',
    'googlesheetsource'
  ]

  ## Object data populated during loops... may be necessary for object post-processing
  title = None
  description = None

  ## Global csv_row
  csv_row = ['']*len(csv_headings)

  ## Global filenames, files and API connections

  collection_log_filename = ''
  collection_log_file = None

  object_log_filename = ''
  object_log_file = None

  alma_api = None


