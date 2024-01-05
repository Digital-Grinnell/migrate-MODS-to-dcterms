
# common functions ---------------------------------------------------------------------

def clean_empty(d):
  if not isinstance(d, (dict, list)):
    return d
  if isinstance(d, list):
    return [v for v in (clean_empty(v) for v in d) if v]
  return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}


def cleanup(tmp):
  return

  # import constant, my_data, my_colorama, tempfile, json
  # rem = my_data.Data.object_log_path.replace('.log', '.remainder')

  # try:
  #   tmp.seek(0)
  #   with tmp as input, tempfile.TemporaryFile('w+') as temp:
  #     temp.write('{\n')
  #     for line in input:
  #       if len(line.strip()) == 0 or line == '{\n' or line == '}\n' or line == '}':
  #         continue
  #       keep = True
  #       for needle in constant.NEEDLES:
  #         if needle in line:
  #           keep = False
  #           break
  #       if keep:
  #         temp.write(line)
  #     temp.write('}\n')

  #     input.close()

  #     # rewind the temporary file and remove all empty keys
  #     temp.seek(0)
  #     try:
  #       dict_from_file = eval(temp.read( ))
  #       empty_keys = [k for k,v in dict_from_file.items() if not v]
  #       for k in empty_keys:
  #         del dict_from_file[k]

  #       # write the data back into the directory as .remainder
  #       with open(rem, 'w+') as file:
  #         file.write(json.dumps(dict_from_file, sort_keys=True, indent=2))

  #     except Exception as e:
  #       my_colorama.red("-- Processing: %s" % my_data.Data.object_log_path)
  #       my_colorama.red("  Exception: %s" % e)
  #       raise

  # except Exception as e:
  #   pass                         # don't kill the messenger (the .remainder file) here!


def prt(tag):
  # import inspect  # https://stackoverflow.com/questions/251464/how-to-get-a-function-name-as-a-string
  # print("%s.%s has been called: " % (__name__, inspect.currentframe().f_code.co_name))
  import json
  print(json.dumps(tag, sort_keys=True, indent=2))


def column(heading):
  import my_data, my_colorama
  try:
    col = my_data.Data.csv_headings.index(heading)
  except Exception as e:
    my_colorama.red("---- Exception in mods.column(): " + str(e))
    my_colorama.yellow("------ heading: " + heading )
    my_data.Data.collection_log_file.write("  ---- Exception in mods.column(): " + str(e))
    my_data.Data.collection_log_file.write("  ------ heading: " + heading)
  return col


def exception(e, tag):
  import json, my_colorama, my_data, constant

  # import traceback, logging
  # logging.error(traceback.format_exc())

  msg = "Exception!!! " + str(e)
  if constant.DEBUG:
    my_colorama.red('---- ' + msg)
  my_data.Data.object_log_file.write(msg + '\n')
  my_data.Data.collection_log_file.write('  ' + msg + '\n')
  skip(tag)


def skip(tag):
  import json, my_colorama, my_data, constant

  # import traceback, logging
  # logging.error(traceback.format_exc())

  msg = "Warning: Unexpected structure detected in the data. The element could not be processed."
  if constant.DEBUG:
    my_colorama.red('------ ' + msg)
  my_data.Data.object_log_file.write(msg + '\n')
  my_data.Data.collection_log_file.write('  ' + msg + '\n')

  msg = "Unexpected Element: " + json.dumps(tag)
  if constant.DEBUG:
    my_colorama.yellow('-------- ' + msg)
  my_data.Data.object_log_file.write('  ' + msg + '\n')
  my_data.Data.collection_log_file.write('    ' + msg + '\n')

  # col = column('WORKSPACE')
  # target = my_data.Data.csv_row[col]
  # my_data.Data.csv_row[col] += msg + ', '
  
  return False            # always returns False !


# check_DCMITypes(value)
# The /mods/genre and /mods/typeOfResource elements may need special handling, do it here.
# https://www.loc.gov/standards/mods/mods-dcsimple.html indicates that both of these MODS terms should
# map to dc:type, and https://www.dublincore.org/specifications/dublin-core/usageguide/qualifiers/ suggests 
# that dcterms:type.dcterms:DCMIType can be used for terms that are compliant with DCMI 
# vocabulary (see https://www.dublincore.org/specifications/dublin-core/dcmi-type-vocabulary/). 
#
# This function will check the genre or typeOfResource input "value" and...
#   - If "value" matches (fuzzy) a valid dcterms:DCMIType vocabulary element, that DCMIType term is returned.
#   - If "value" does not match... the function returs False such that 
#       "value" is mapped to "dc:type"
#
def check_DCMITypes(value):
  import constant, my_colorama, my_data
  from fuzzywuzzy import fuzz, process
  DCMI = process.extractOne(value, constant.DCMITypes, score_cutoff=constant.TARGET_LEVEHSHTEIN_RATIO)
  if not DCMI or DCMI == "None":
    msg = "No DCMIType match found for '%s'" % value
    my_colorama.red(msg)
    my_data.Data.collection_log_file.write('  ' + msg + '\n')
    my_data.Data.object_log_file.write('  ' + msg + '\n')


    return False
  else:
    return DCMI

# map_resource_type(value)
# The /mods/genre or /mods/typeOfResource may need to map into the 'dc:type' field to
# control Alma resource typing. 
#  
# https://www.loc.gov/standards/mods/mods-dcsimple.html indicates that both of these MODS terms should
# map to dc:type, and https://www.dublincore.org/specifications/dublin-core/usageguide/qualifiers/ suggests 
# that dcterms:type.dcterms:DCMIType can be used for terms that are compliant with DCMI 
# vocabulary (see https://www.dublincore.org/specifications/dublin-core/dcmi-type-vocabulary/). 
#
# This function will check the genre or typeOfResource input "value" and...
#   - If "value" matches (fuzzy) a valid dcterms:DCMIType vocabulary element, that DCMIType term is returned.
#   - If "value" does not match... the function returs False such that 
#       "value" is mapped to "dc:type"
#
def map_resource_type(value):
  import constant, my_colorama, my_data
  from fuzzywuzzy import fuzz, process
  type = process.extractOne(value, constant.RESOURCETypes.keys(), score_cutoff=constant.TARGET_LEVEHSHTEIN_RATIO)
  if not type or type == "None":
    msg = "No Resource Type match found for '%s'" % value
    my_colorama.red(msg)
    my_data.Data.collection_log_file.write('  ' + msg + '\n')
    my_data.Data.object_log_file.write('  ' + msg + '\n')
    return False
  else:
    return type


# multi(key,value)
# Called when adding 'value' to a multi-valued target column 'key'
def multi(key, value):
  import constant, my_data

  col = column(key)
  if type(value) is list:
    for idx, v in enumerate(value):
      if type(v) is not str:
        v = v['#text']
      nc = len(my_data.Data.csv_row[col])
      if nc > 0:
        my_data.Data.csv_row[col] += ' | ' + v
      else:
        my_data.Data.csv_row[col] = v
    return v + constant.DONE + key
  else:
    if type(value) is not str:
      value = value['#text']
    nc = len(my_data.Data.csv_row[col])
    if nc > 0:
      my_data.Data.csv_row[col] += ' | ' +  value
    else:
      my_data.Data.csv_row[col] = value
  return value + constant.DONE + key


# single(key,value)
# Called when adding 'value' to a single-valued target column 'key'
def single(key, value, replace=False):
  import my_data, my_colorama, constant
  col = column(key)

  # if value is NULL or None, write to the log file but DO NOT ATTEMPT TO SAVE the field
  if value is None:
    if constant.DEBUG:
      my_colorama.red("------ single() for key '%s' but value is None (empty).  Nothing to save!" % key)
    my_data.Data.collection_log_file.write("------ single() for key '%s' but value is None (empty).  Nothing to save!" % key)
    return False

  if type(value) is not str:
    value = value['#text']

  nc = len(my_data.Data.csv_row[col])
  if nc > 0 and not replace:
    if constant.DEBUG:
      my_colorama.red("------ single() called but the target cell in column(%s) is already filled!" % key)
    my_data.Data.collection_log_file.write("------ single() called but the target cell in column(%s) is already filled!" % key)
    return False
  else:
    my_data.Data.csv_row[col] = value
  return value + constant.DONE + key


def append(key, value):
  import constant, my_data, my_colorama
  col = column(key)
  if type(value) is not str:
    value = value['#text']
  nc = len(my_data.Data.csv_row[col])
  if nc > 0:
    my_data.Data.csv_row[col] += ' ~ ' + value
    return value + constant.DONE + key
  else:
    if constant.DEBUG:
      my_colorama.red("------ append() called but the target cell in column(%s) is empty!" % key)
    my_data.Data.collection_log_file.write("------ append() called but the target cell in column(%s) is empty!" % key)
    return False


def getMIME(m):
  import mimetypes
  if '/' in m:
    parts = m.split('/', 2)
    f = 'test.' + parts[1]
  else:
    f = 'test.' + m
  (guess, enc) = mimetypes.guess_type(f)
  return guess


# process one thing ...as a single dict

def process_dict(thing, action):         # given one thing, a dict, and a specific action...
  ok = action(thing)                     # execute the action and return it's replacement value if valid
  if ok:                                 # if the action worked...
    thing = ok                           # replace thing's value with whatever the action returned
    return ok                            # ...and return the same from this function
  else:
    return skip(thing)                          # do NOT skip this...that should have happened in the action function!


# process many things ...as a list of dicts

def process_list_dict(things, action):    # same as above, but given a list of thing dicts, and a specific action...
  for idx, thing in enumerate(things):    # loop on all the things
    ok = process_dict(thing, action)      # call the function above
    if ok:                                # if the action worked...
      things[idx] = ok                    # replace this thing's value with whatever the action returned


# process dict of list ...as a single dict that holds a list

def process_dict_list(thing, action):      # so far only used for 'language'
  if 'languageTerm' in thing:
    thing['languageTerm'] = process_dict(thing['languageTerm'], action)
  else:
    return skip(thing)
  return False


# process one simple thing destined for a single-value field

def process_simple(thing, heading, replace=False):       # use for simple key:value things like 'abstract'
  try:
    ok = single(heading, thing, replace)
    if ok:
      thing = ok
      return ok
    return skip(thing)
  except Exception as e:
    exception(e, thing)


# process one simple thing destined for a multi-valued field

def process_multi(thing, heading):         # use for simple key:value things like 'abstract'
  try:
    ok = multi(heading, thing)
    if ok:
      thing = ok
      return ok
    return skip(thing)
  except Exception as e:
    exception(e, thing)


# tag-specific actions ----------------------------------------------------------------


# classification
#Map: classification_action(x):
#Map:   x -> dc:identifier
#
def classification_action(c):
  try:                                  
    ok = multi('dc:identifier', c)       
      # if '@authority' in c:           
      #   ok = append('dc:identifier', c['@authority'])
    if ok:
      return ok
    return skip(c)
  except Exception as e:
    exception(e, c)

# identifier    Verified: 29-Sep-2023
def identifier_action(id):
  try:
    if '@type' in id:                                 #Map: identifier_action(x):
      if id['@type'] == 'local':                      #Map:   if x[@type='local']:
        heading = 'dc:identifier'                     #Map:     x -> dc:identifier 
      elif id['@type'] == 'hdl':                      #Map:   if: x[@type='hdl']:
        heading = 'dcterms:identifier.dcterms:URI'    #Map:     x -> dcterms:identifier.dcterms:URI
      else:                                           
        return skip(id)
      return multi(heading, id)
    return skip(id)
  except Exception as e:
    exception(e, id)

# extension
def extension_action(ext):
  c = len(ext)
  try:
    if 'CModel' in ext:
      ok = single('CMODEL', ext['CModel'])
      if ok:
        ext['CModel'] = ok
        c = c - 1
      else:
        skip(ext['CModel'])
    if 'primarySort' in ext:
      ok = single('Primary_Sort', ext['primarySort'])
      if ok:
        ext['primarySort'] = ok
        c = c - 1
      else:
        skip(ext['primarySort'])
    if 'dg_importSource' in ext:
      ok = single('Import_Source', ext['dg_importSource'])
      if ok:
        ext['dg_importSource'] = ok
        c = c - 1
      else:
        skip(ext['dg_importSource'])
    if 'dg_importIndex' in ext:
      ok = single('Import_Index', ext['dg_importIndex'])
      if ok:
        ext['dg_importIndex'] = ok
        c = c - 1
      else:
        skip(ext['dg_importIndex'])
    if 'hidden_creator' in ext:
      ok = single('Hidden_Creator', ext['hidden_creator'])
      if ok:
        ext['hidden_creator'] = ok
        c = c - 1
      else:
        skip(ext['hidden_creator'])
    if 'hidden_creators' in ext:                               # this structure is WRONG, but common!
      ok = single('Hidden_Creator', ext['hidden_creators'])
      if ok:
        ext['hidden_creators'] = ok
        c = c - 1
      else:
        skip(ext['hidden_creators'])
    if 'pull_quote' in ext:
      ok = multi('Pull_Quotes', ext['pull_quote'])
      if ok:
        ext['pull_quote'] = ok
        c = c - 1
      else:
        skip(ext['pull_quote'])
    if c > 0:
      return skip(ext)

  except Exception as e:
    exception(e, ext)


# language  Verified: 29-Sep-2023
def language_action(lang):
  try:
    c = t = ok = False
    for term in lang:
      if term['@type'] == 'code':
        c = term['#text']           # Save the #code if that's all we have
      if term['@type'] == 'text':
        t = term['#text']           # Saving #text is preferable

    if t:                                 #Map: language_action(x):
      ok = multi('dc:language', t)        #Map:   if x[@type='text']:
    elif c:                               #Map:     x[text] -> dc:language             
      ok = multi('dc:language', c)        #Map:   else: 
    if ok:                                #Map:     x[code] -> dc:language
      return ok
    return skip(lang)
  except Exception as e:
    exception(e, lang)

# location  Verified: 29-Sep-2023
def location_action(loc):
  import my_colorama
  try:                                                  #Map: location_action(x):
    if 'shelfLocator' in loc:                           #Map:   if 'shelfLocator' in x: 
      ok = multi('dc:identifier', loc['shelfLocator'])  #Map:      x -> dc:identifier
      if ok:                                            
        loc['shelfLocator'] = ok
        return ok
      else:
        return skip(loc['shelfLocator'])
  except Exception as e:
    exception(e, loc)

# name   Verified 29-Sep-2023
def name_action(name):
  import constant
  try:
    if 'namePart' in name:
      if 'roleTerm' in name['role']:
        v = name['role']['roleTerm']
        if type(v) is not str:                          
          v = v['#text']                                #Map: name_action(x):
        if v.lower( ) in constant.CREATORS:             #Map:   if x/role/roleTerm in CREATORS:
          ok = multi('dc:creator', name['namePart'])    #Map:     x -> dc:creator
          if ok:                                        #Map:   else:
            return ok                                   #Map:     x -> dc:contributor
      ok = multi('dc:contributor', name['namePart'])    
      if ok:                                            
        return ok
    return skip(name)
  except Exception as e:
    exception(e, name)

# note
def note_action(note):
  ok = False
  try:
    if '@displayLabel' in note:                              #Map: note_action(x):
      if 'DATE' in note['@displayLabel'].upper( ):           #Map:   if x[@displayLabel='date']:
        return multi('dc:date', note)                        #Map:     x -> dc:date 
    elif '@type' in note:                                    #Map:   elif x[@type]:
      if 'provenance'.lower() in note['@type']:              #Map:     if x[@type='provenance']:
        return multi('dcterms:provenance', note)             #Map:       x -> dcterms:provenance 
      elif 'citation'.lower() in note['@type']:              #Map:     if x[@type='citation']:
        return multi('dcterms:bibliographicCitation', note)  #Map:       x -> dcterms:bibliographicCitation 
      else:                                                  #Map:     else:
        return multi('dc:description', note)                 #Map:       x -> dc:description
    return skip(note)
  except Exception as e:
    exception(e, note)

  # try:
  #   if '@displayLabel' in note:
  #     if 'DATE' in note['@displayLabel'].upper( ):
  #       if single('Other_Date~Display_Label', note):
  #         return append('Other_Date~Display_Label', note['@displayLabel'])
  #   elif '@type' in note:
  #     if note['@type'] == 'citation':
  #       if multi('Citations', note):
  #         return append('Citations', note['@type'])
  #     elif multi('Public_Notes~Types', note):
  #       return append('Public_Notes~Types', note['@type'])
  #   return skip(note)
  # except Exception as e:
  #   exception(e, note)


# originInfo
def originInfo_action(info):                                  #Map: originInfo_action(x):
  c = len(info)
  try:
    if 'dateCreated' in info:                                 #Map:   if 'dateCreated' in x:
      ok = single('dcterms:created', info['dateCreated'])     #Map:     x/mods:dateCreated -> dcterms:created
      if ok:
        info['dateCreated'] = ok
        c = c - 1
      else:
        skip(info['dateCreated'])
    if 'dateIssued' in info:                                  #Map:   if 'dateIssued' in x:
      ok = single('dcterms:issued', info['dateIssued'])       #Map:     x/mods:dateIssued -> dcterms:issued
      if ok:
        info['dateIssued'] = ok
        c = c - 1
      else:
        skip(info['dateIssued'])
    if 'publisher' in info:                                   #Map:   if 'publisher' in x: 
      ok = multi('dcterms:publisher', info['publisher'])      #Map:     x/mods:publisher -> dcterms:publisher
      if ok:
        info['publisher'] = ok
        c = c - 1
      else:
        skip(info['publisher'])
    if 'dateOther' in info:                                   #Map:   if 'dateOther' in x:
      ok = single('dcterms:dateAccepted', info['dateOther'])  #Map:     x/mods:dateOther -> dcterms:dateAccepted
      if ok:
        info['dateOther'] = ok
        c = c - 1
        # if '@displayLabel' in info['dateOther']:
        #   ok = append('Other_Date~Display_Label', info['dateOther']['@displayLabel'])
      else:
        skip(info['dateOther'])
    if 'dateCaptured' in info:                                            #Map:   if 'dateCaptured' in x: 
      # ok = single('dcterms:dateSubmitted', info['dateCaptured'])    
      ok = append('rep_note', "dateCaptured: " + info['dateCaptured'])    #Map:     x/mods:dateCaptured -> rep_note with 'dateCaptured:' prefix
      if ok:                                                             
        info['dateCaptured'] = ok
        c = c - 1
      else:
        skip(info['dateCaptured'])
    if c > 0:
      return skip(info) 
  except Exception as e:
    exception(e, info)


# physicalDescription
def physicalDescription_action(desc):
  import my_colorama
  try:                                                   #Map: physicalDescription_action(x):
    if 'digitalOrigin' in desc:                          #Map:   if 'mods:digitalOrigin' in x: 
      ok = single('dc:format', desc['digitalOrigin'])    #Map:     x/mods:digitalOrigin -> dc:format
      if ok:
        desc['digitalOrigin'] = ok
      else:
        skip(desc['digitalOrigin'])
    if 'extent' in desc:                                 #Map:   if 'mods:extent' in x:
      ok = single('dcterms:extent', desc['extent'])      #Map:     x/mods:extent -> dcterms:extent
      if ok:
        desc['extent'] = ok
      else:
        skip(desc['extent'])                             #Map:   if 'mods:form' in x:
    if 'form' in desc:                                   #Map:     x/mods:form -> dcterms:medium
      ok = single('dcterms:medium', desc['form'])
      if ok:
        desc['form'] = ok
      else:
        skip(desc['form'])
    if 'internetMediaType' in desc:                      #Map:   if 'mods:internetMediaType' in x and it maps to valid MIME type:
      mime = getMIME(desc['internetMediaType'])          #Map:     x/mods:internetMediaType -> dcterms:format.dcterms:IMT    
      if (desc['internetMediaType'] == 'text/plain'):
        mime = 'text/plain';
      if mime:
        ok = single('dcterms:format.dcterms:IMT', mime)    
        if ok:
          desc['internetMediaType'] = ok
        else:
          skip(desc['internetMediaType'])               
      else:
        my_colorama.red("Could not guess MIME type from '%s'." % desc['internetMediaType'])
        skip(desc['internetMediaType'])
    return False
  except Exception as e:
    exception(e, desc)


# relatedItem
def relatedItem_action(item):
  ok = False
  try:                                                                #Map: relatedItem_action(x):
    if '@type' in item:                                               #Map:   if x[@type='isPartOf']: 
      if item['@type'] == 'isPartOf':                                 #Map:     x -> dcterms:isPartOf 
        ok = multi('dcterms:isPartOf', item['titleInfo']['title'])    
    else:
      ok = multi('dc:relation', item['titleInfo']['title'])           #Map:   else: mods:relatedItem -> dc:relation
    if ok:                                                            #Map:     x -> dc:relation
      item['titleInfo']['title'] = ok
      return ok  
    return skip(item)
  except Exception as e:
    exception(e, item)


# subject
def subject_action(s):
  import constant

  c = len(s)                                                      #Map: subject_action(x):
  try:                                                            #Map:   if /mods:geographic in x:
    if 'geographic' in s:                                         #Map:     x/mods:geographic -> dcterms:spatial
      ok = multi('dcterms:spatial', s['geographic'])     
      if ok:
        s['geographic'] = ok
        c = c - 1
      else:
        skip(s['geographic'])
    if 'hierarchicalGeographic' in s:                              #Map:   if /mods:hierarchicalGeographic in x:
      ok = multi('dcterms:spatial', s['hierarchicalGeographic'])   #Map:     x/mods:hierarchicalGeographic -> dcterms:spatial
      if ok:
        s['hierarchicalGeographic'] = ok
        c = c - 1
      else:
        skip(s['hierarchicalGeographic'])
    if 'temporal' in s:                                            #Map:   if /mods:temporal in x:
      ok = multi('dcterms:temporal', s['temporal'])                #Map:     x/mods:temporal -> dcterms:temporal
      if ok:
        s['temporal'] = ok
        c = c - 1
      else:
        skip(s['temporal'])
    if 'cartographics' in s:                                                              #Map:   if /mods:cartographics in x: 
      if 'coordinates' in s['cartographics']:                                             #Map:     if /mods:coordinates in y:
        ok = single('dcterms:spatial.dcterms:Point', s['cartographics']['coordinates'])   #Map:       x/y/mods:coordinates -> dcterms:spatial.dcterms:Point
        if ok:
          c = c - 1
          s['cartographics']['coordinates'] = ok
          return ok
      else:                                                 
        ok = multi('dcterms:spatial', s['cartographics'])         #Map:     else:         
        if ok:                                                    #Map:       x/mods:cartograhpics -> dcterms:spatial
          c = c - 1
          s['cartographics'] = ok
          return ok
      skip(['cartographics'])
    if 'topic' in s:                                          # unfortunately, s['topic'] could be a dict or a list
      if '@authority' in s and s['@authority'] == 'lcsh':
        heading = 'dcterms:subject.dcterms:LCSH'             #Map:   if mods:topic in x:
        c = c - 1                                            #Map:     y[@authority='lcsh'] -> dcterms:subject.dcterms:LCSH
        s['@authority'] = constant.DONE + heading
      else:
        heading = 'dc:subject'                               #Map:   else: 
      ok = multi(heading, s['topic'])                        #Map:     y -> dc:subject
      if ok:
        s['topic'] = ok
        c = c - 1
      else:
        skip(s['topic'])
    if c > 0:
      return skip(s)
    else:
      return ok                     
  except Exception as e:
    exception(e, s)


# titleInfo
def titleInfo_action(title):
  try:
    ok = False
    if '@type' in title:                                      #Map: titleInfo_action(x):
      if title['@type'] == 'alternative':                     #Map:   if x[@type]: 
        ok = multi('dcterms:alternative', title['title'])     #Map:     if x[@type='alternative']:
                                                              #Map:       x -> dcterms:alternative
    else:                                                     #Map:     else:
      ok = single('dc:title', title['title'])                 #Map:       x -> dc:title
    if ok:                                                    
      return ok
    else:
      return skip(title)
  except Exception as e:
    exception(e, title)


