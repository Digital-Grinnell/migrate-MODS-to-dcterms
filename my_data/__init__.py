class Data:

  ## special handling per collection - informs the script about special handling
  ## situations on a collection-by-collection basis   NOT USED!

  special_handling = {
    'postcards': [{ 'classification': 'dc:identifier' }]
  }

  ## list of MODS types that are not yet mapped to Alma
  not_mapped = [
    'classification',
    'extension'
  ]

  ## ordered list of csv column headings for Alma-D
  csv_headings = [
    'import-index',
    'group_id',
    'collection_id',
    'mms_id',
    'originating_system_id',
    'link-to-DG',
    'log-file-link',
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
    'dcterms:rights',
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
    'file_label_'
  ]

  ## empty ordered dict of csv column headings for Alma-D -- I don't think this is used anymore?
  csv_row_structure = {
    'group_id': '',
    'collection_id': '',
    'mms_id': '',
    'originating_system_id': '',
    'not_used': '',
    'dc:title': '',
    'dcterms:alternative': '',
    'dc:creator': '',
    'dc:contributor': '',
    'dc:subject': '',
    'dcterms:subject.dcterms:LCSH': '',
    'dc:description': '',
    'dcterms:abstract': '',
    'dc:publisher': '',
    'dc:date': '',
    'dcterms:created': '',
    'dcterms:issued': '',
    'dc:type': '',
    'dc:format': '',
    'dcterms:extent': '',
    'dc:identifier': '',
    'dcterms:identifier.dcterms:URI': '',
    'dc:language': '',
    'dc:relation': '',
    'dcterms:isPartOf': '',
    'dc:coverage': '',
    'dcterms:spatial': '',
    'dcterms:spatial.dcterms:Point': '',
    'dcterms:temporal': '',
    'dcterms:rights': '',
    'dc:source': '',
    'bib custom field': '',
    'rep_label': '',
    'rep_public_note': '',
    'rep_access_rights': '',
    'rep_usage_type': '',
    'rep_library': '',
    'rep_note': '',
    'rep_custom field': '',
    'file_name_1': '',
    'file_label_1': '',
    'file_name_2': '',
    'file_label_2': ''
  }


  ## global csv_row
  csv_row = ['']*len(csv_headings)

  ## global filenames and files

  collection_log_filename = ''
  collection_log_file = None

  object_log_filename = ''
  object_log_file = None


