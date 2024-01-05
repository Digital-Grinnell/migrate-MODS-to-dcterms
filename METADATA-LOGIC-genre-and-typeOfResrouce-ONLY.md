if there's no mods:genre:
  REPLACE ME warning -> dc:type

if mods:genre fuzzy match with valid DCMIType term:
  mods:genre -> dcterms:type.dcterms:DCMIType

if typeOfResource fuzzy match with valid DCMIType term:
  mods:typeOfResource -> dcterms:type.dcterms:DCMIType

if item has valid Alma Resource Type: 
  Alma Resource Type -> dc:type

if no mods:genre AND no dc:type:
  mods:typeOfResource -> dc:type  
