
# common functions ---------------------------------------------------------------------

def clean_empty(d):
  if not isinstance(d, (dict, list)):
    return d
  if isinstance(d, list):
    return [v for v in (clean_empty(v) for v in d) if v]
  return {k: v for k, v in ((k, clean_empty(v)) for k, v in d.items()) if v}


def cleanup(tmp):
  import constant, my_data, my_colorama, xmltodict, tempfile, json
  rem = my_data.Data.object_log_filename.replace('.log', '.remainder')

  try:
    tmp.seek(0)
    with tmp as input, tempfile.TemporaryFile('w+') as temp:
      temp.write('{\n')
      for line in input:
        if len(line.strip()) == 0 or line == '{\n' or line == '}\n' or line == '}':
          continue
        keep = True
        for needle in constant.NEEDLES:
          if needle in line:
            keep = False
            break
        if keep:
          temp.write(line)
      temp.write('}\n')

      input.close()

      # rewind the temporary file and remove all empty keys
      temp.seek(0)
      try:
        dict_from_file = eval(temp.read())
        empty_keys = [k for k,v in dict_from_file.items() if not v]
        for k in empty_keys:
          del dict_from_file[k]

        # write the data back into the directory as .remainder
        with open(rem, 'w+') as file:
          file.write(json.dumps(dict_from_file, sort_keys=True, indent=2))

      except Exception as e:
        my_colorama.red("-- Processing: %s" % my_data.Data.object_log_filename)
        my_colorama.red("  Exception: %s" % e)
        raise

  except Exception as e:
    pass                         # don't kill the messenger (the .remainder file) here!


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
#   - If "value" does not match... the function returs False where
#       "genre: <value>" is appended to dc:desciption (it becomes a "note")
#
def check_DCMITypes(value):
  import constant, my_colorama
  from fuzzywuzzy import fuzz, process
  DCMI = process.extractOne(value, constant.DCMITypes, score_cutoff=constant.TARGET_LEVEHSHTEIN_RATIO)
  if not DCMI or DCMI == "None":
    my_colorama.red("No DCMIType match found for '%s'" % value)
    return False
  else:
    return DCMI



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
def single(key, value):
  import my_data, my_colorama, constant
  col = column(key)
  if type(value) is not str:
    value = value['#text']
  nc = len(my_data.Data.csv_row[col])
  if nc > 0:
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

def process_simple(thing, heading):         # use for simple key:value things like 'abstract'
  try:
    ok = single(heading, thing)
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
def classification_action(c):
  try:
    ok = multi('dc:identifier', c)      ### !Map
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
    if '@type' in id:
      if id['@type'] == 'local':
        heading = 'dc:identifier'                     ### !Map
      elif id['@type'] == 'hdl':
        heading = 'dcterms:identifier.dcterms:URI'    ### !Map
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
        c = term['#text']
      if term['@type'] == 'text':
        t = term['#text']
    if t:
      ok = multi('dc:language', t)        ### !Map   Saving #text is preferable
    elif c:
      ok = multi('dc:language', c)        ### !Map   Save the #code if that's all we have
    if ok:
      return ok
    return skip(lang)
  except Exception as e:
    exception(e, lang)

# location  Verified: 29-Sep-2023
def location_action(loc):
  import my_colorama
  try:
    if 'shelfLocator' in loc:
      ok = multi('dc:identifier', loc['shelfLocator'])  ### !Map
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
          v = v['#text']
        if v.lower( ) in constant.CREATORS:
          ok = multi('dc:creator', name['namePart'])    ### !Map
          if ok:
            return ok
      ok = multi('dc:contributor', name['namePart'])    ### !Map
      if ok:
        return ok
    return skip(name)
  except Exception as e:
    exception(e, name)

# note
def note_action(note):
  ok = False
  try:
    if '@displayLabel' in note:
      if 'DATE' in note['@displayLabel'].upper( ):
        return multi('dc:date', note)                   ### !Map
    elif '@type' in note:
      if 'citation'.lower() in note['@type']:
        return multi('dcterms:bibliographicCitation', note)     ### !Map
      else: 
        return multi('dc:description', note)        ### !Map
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
def originInfo_action(info):
  c = len(info)
  try:
    if 'dateCreated' in info:
      ok = single('dcterms:created', info['dateCreated'])     ### !Map
      if ok:
        info['dateCreated'] = ok
        c = c - 1
      else:
        skip(info['dateCreated'])
    if 'dateIssued' in info:
      ok = single('dcterms:issued', info['dateIssued'])     ### !Map
      if ok:
        info['dateIssued'] = ok
        c = c - 1
      else:
        skip(info['dateIssued'])
    if 'publisher' in info:
      ok = multi('dcterms:publisher', info['publisher'])     ### !Map
      if ok:
        info['publisher'] = ok
        c = c - 1
      else:
        skip(info['publisher'])
    if 'dateOther' in info:
      ok = single('dcterms:date_accepted', info['dateOther'])    ### !Map
      if ok:
        info['dateOther'] = ok
        c = c - 1
        # if '@displayLabel' in info['dateOther']:
        #   ok = append('Other_Date~Display_Label', info['dateOther']['@displayLabel'])
      else:
        skip(info['dateOther'])
    if 'dateCaptured' in info:
      # ok = single('dcterms:dateSubmitted', info['dateCaptured'])    ### !Map
      ok = single('rep_note', "dateCaptured: " + info['dateCaptured'])    ### !Map
      if ok:
        info['dateCaptured'] = ok
        c = c - 1
      else:
        skip(info['dateOther'])
    if c > 0:
      return skip(info)
  except Exception as e:
    exception(e, info)


# physicalDescription
def physicalDescription_action(desc):
  import my_colorama
  try:
    if 'digitalOrigin' in desc:
      ok = single('dc:format', desc['digitalOrigin'])    ### !Map
      if ok:
        desc['digitalOrigin'] = ok
      else:
        skip(desc['digitalOrigin'])
    if 'extent' in desc:
      ok = single('dcterms:extent', desc['extent'])      ### !Map
      if ok:
        desc['extent'] = ok
      else:
        skip(desc['extent'])
    if 'form' in desc:                                   ### !Map
      ok = single('dcterms:medium', desc['form'])
      if ok:
        desc['form'] = ok
      else:
        skip(desc['form'])
    if 'internetMediaType' in desc:
      mime = getMIME(desc['internetMediaType'])
      if (desc['internetMediaType'] == 'text/plain'):
        mime = 'text/plain';
      if mime:
        ok = single('dcterms:format.dcterms:IMT', mime)      ### !Map
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
  try:
    if '@type' in item:
      if item['@type'] == 'isPartOf':
        ok = multi('dcterms:isPartOf', item['titleInfo']['title'])    ### !Map
    else:
      ok = multi('dc:relation', item['titleInfo']['title'])      ### !Map
    if ok:
      item['titleInfo']['title'] = ok
      return ok  
    return skip(item)
  except Exception as e:
    exception(e, item)


# subject
def subject_action(s):
  import constant

  c = len(s)
  try:
    if 'geographic' in s:
      ok = multi('dcterms:spatial', s['geographic'])     ### !Map
      if ok:
        s['geographic'] = ok
        c = c - 1
      else:
        skip(s['geographic'])
    if 'hierarchicalGeographic' in s:
      ok = multi('dcterms:spatial', s['hierarchicalGeographic'])   ### !Map
      if ok:
        s['hierarchicalGeographic'] = ok
        c = c - 1
      else:
        skip(s['hierarchicalGeographic'])
    if 'temporal' in s:
      ok = multi('dcterms:temporal', s['temporal'])     ### !Map
      if ok:
        s['temporal'] = ok
        c = c - 1
      else:
        skip(s['temporal'])
    if 'cartographics' in s:
      if 'coordinates' in s['cartographics']:
        ok = single('dcterms:spatial.dcterms:Point', s['cartographics']['coordinates'])    ###!Map
        if ok:
          c = c - 1
          s['cartographics']['coordinates'] = ok
          return ok
      else:
        ok = multi('dcterms:spatial', s['cartographics'])    ###!Map
        if ok:
          c = c - 1
          s['cartographics'] = ok
          return ok
      skip(['cartographics'])
    if 'topic' in s:                                          # unfortunately, s['topic'] could be a dict or a list
      if '@authority' in s and s['@authority'] == 'lcsh':
        heading = 'dcterms:subject.dcterms:LCSH'             ### !Map
        c = c - 1
        s['@authority'] = constant.DONE + heading
      else:
        heading = 'dc:subject'                               ### !Map
      ok = multi(heading, s['topic'])
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
    if '@type' in title:
      if title['@type'] == 'alternative':
        ok = multi('dcterms:alternative', title['title'])   ### !Map
    else:
      ok = single('dc:title', title['title'])             ### !Map
    if ok:
      return ok
    else:
      return skip(title)
  except Exception as e:
    exception(e, title)


