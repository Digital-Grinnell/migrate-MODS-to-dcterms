
pid -> originating_system_id

if (is child of compound parent... has a fedora:isConstituentOf value):   
  compound parent PID -> collection_id  

if (not child of compound):
  user-specified collection ID -> collection_id

if there's no mods:genre:
  REPLACE ME warning -> dc:type

mods:titleInfo => mods.titleInfo_action( )

if object is compound child:
  dc:title -> rep_label  
  dc:title -> file_label_1 
  dc:title -> REMOVED  

mods:abstract -> dcterms:abstract

mods:accessCondition -> dc:rights

mods:classification => mods.classification_action( )

mods:extension => mods.extension_action( )

if genre maps to valid DCMIType term:
  mods:genre -> dcterms:type.     dcterms:DCMIType

if item has valid Alma Resource Type: 
  Alma Resource Type -> dc:type

mods:identifier => mods.identifier_action( )

mods:language => mods.language_action( )

mods:location => mods.location_action( )

mods:name => mods.name_action( )

mods:note => mods.note_action( )

mods:originInfo => mods.originInfo_action( )

mods:physicalDescription => mods.physicalDescription_action( )

mods:relatedItem => mods.relatedItem_action( )

mods:subject => mods.subject_action( )

if typeOfResource has fuzzy match with DCMIType:
  mods:typeOfResource -> dcterms:type.dcterms:DCMIType

if no mods:genre and we have no dc:type:
  mods:typeOfResource -> dc:type  

if (object is child of compound):
  compound parent PID -> group_id

elif not a child of a compound:
  object PID -> group_id  

if object has an OBJ file:
  OBJ filename -> file_name_1

if object has NO OBJ file and is not a compound parent:  
  WARNING MESSAGE -> file_name_1

classification_action(x):
  x -> dc:identifier

identifier_action(x):
  if x[@type='local']:
    x -> dc:identifier 
  if: x[@type='hdl']:
    x -> dcterms:identifier.dcterms:URI

language_action(x):
  if x[@type='text']:
    x[text] -> dc:language             
  else: 
    x[code] -> dc:language

location_action(x):
  if 'shelfLocator' in x: 
     x -> dc:identifier

name_action(x):
  if x/role/roleTerm in CREATORS:
    x -> dc:creator
  else:
    x -> dc:contributor

note_action(x):
  if x[@displayLabel='date']:
    x -> dc:date 
  elif x[@type]:
    if x[@type='citation']:
      x -> dcterms:bibliographicCitation 
    else:
      x -> dc:description

originInfo_action(x):
  if 'dateCreated' in x:
    x/mods:dateCreated -> dcterms:created
  if 'dateIssued' in x:
    x/mods:dateIssued -> dcterms:issued
  if 'publisher' in x: 
    x/mods:publisher -> dcterms:publisher
  if 'dateOther' in x:
    x/mods:dateOther -> dcterms:dateAccepted
  if 'dateCaptured' in x: 
    x/mods:dateCaptured -> rep_note with 'dateCaptured:' prefix

physicalDescription_action(x):
  if 'mods:digitalOrigin' in x: 
    x/mods:digitalOrigin -> dc:format
  if 'mods:extent' in x:
    x/mods:extent -> dcterms:extent
  if 'mods:form' in x:
    x/mods:form -> dcterms:medium
  if 'mods:internetMediaType' in x and it maps to valid MIME type:
    x/mods:internetMediaType -> dcterms:format.dcterms:IMT    

relatedItem_action(x):
  if x[@type='isPartOf']: 
    x -> dcterms:isPartOf 
  else: mods:relatedItem -> dc:relation
    x -> dc:relation

subject_action(x):
  if /mods:geographic in x:
    x/mods:geographic -> dcterms:spatial
  if /mods:hierarchicalGeographic in x:
    x/mods:hierarchicalGeographic -> dcterms:spatial
  if /mods:temporal in x:
    x/mods:temporal -> dcterms:temporal
  if /mods:cartographics in x: 
    if /mods:coordinates in y:
      x/y/mods:coordinates -> dcterms:spatial.dcterms:Point
    else:         
      x/mods:cartograhpics -> dcterms:spatial
  if mods:topic in x:
    y[@authority='lcsh'] -> dcterms:subject.dcterms:LCSH
  else: 
    y -> dc:subject

titleInfo_action(x):
  if x[@type]: 
    if x[@type='alternative']:
      x -> dcterms:alternative
    else:
      x -> dc:title
