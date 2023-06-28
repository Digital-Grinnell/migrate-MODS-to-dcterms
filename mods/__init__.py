import constant

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
          file.write(json.dumps(dict_from_file))
      except Exception as e:
        my_colorama.red("-- Processing: %s" % my_data.Data.object_log_filename)
        my_colorama.red("  Exception: %s" % e)


  except Exception as e:
    my_colorama.red("Exception: %s" % e)
    raise




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


def multi(key, value):
  import my_data
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
    return constant.DONE + key
  else:
    if type(value) is not str:
      value = value['#text']
    nc = len(my_data.Data.csv_row[col])
    if nc > 0:
      my_data.Data.csv_row[col] += ' | ' +  value
    else:
      my_data.Data.csv_row[col] = value
  return constant.DONE + key


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
  return constant.DONE + key


def append(key, value):
  import my_data, my_colorama
  col = column(key)
  if type(value) is not str:
    value = value['#text']
  nc = len(my_data.Data.csv_row[col])
  if nc > 0:
    my_data.Data.csv_row[col] += ' ~ ' + value
    return constant.DONE + key
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


# process one simple thing

def process_simple(thing, heading):         # use for simple key:value things like 'abstract'
  try:
    ok = single(heading, thing)
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
    if multi('Classifications~Authorities', c):
      if '@authority' in c:
        ok = append('Classifications~Authorities', c['@authority'])
        if ok:
          return ok
    return skip(c)
  except Exception as e:
    exception(e, c)


# identifier
def identifier_action(id):
  try:
    if '@type' in id:
      if id['@type'] == 'local':
        heading = 'Local_Identifier'
      elif id['@type'] == 'hdl':
        heading = 'Handle'
      else:
        return skip(id)
      return single(heading, id)
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


# language
def language_action(lang):
  try:
    c = t = ok = False
    for term in lang:
      if term['@type'] == 'code':
        c = term['#text']
      if term['@type'] == 'text':
        t = term['#text']
    if c and t:
      if multi('Language_Names~Codes', t):
        ok = append('Language_Names~Codes', c)
        if ok:
          return ok
    return skip(lang)
  except Exception as e:
    exception(e, lang)


# name
def name_action(name):
  try:
    if 'namePart' in name:
      if name['@type'] == 'corporate':
        heading = 'Corporate_Names~Roles'
      elif name['@type'] == 'personal':
        heading = 'Personal_Names~Roles'
      else:
        return False
      ok = multi(heading, name['namePart'])
      if ok and 'roleTerm' in name['role']:
        return append(heading, name['role']['roleTerm'])
      return ok
    return skip(name)
  except Exception as e:
    exception(e, name)


# note
def note_action(note):
  try:
    if '@displayLabel' in note:
      if 'DATE' in note['@displayLabel'].upper():
        if single('Other_Date~Display_Label', note):
          return append('Other_Date~Display_Label', note['@displayLabel'])
    elif '@type' in note:
      if note['@type'] == 'citation':
        if multi('Citations', note):
          return append('Citations', note['@type'])
      elif multi('Public_Notes~Types', note):
        return append('Public_Notes~Types', note['@type'])
    return skip(note)
  except Exception as e:
    exception(e, note)


# originInfo
def originInfo_action(info):
  c = len(info)
  try:
    if 'dateCreated' in info:
      ok = single('Index_Date', info['dateCreated'])
      if ok:
        info['dateCreated'] = ok
        c = c - 1
      else:
        skip(info['dateCreated'])
    if 'dateIssued' in info:
      ok = single('Date_Issued', info['dateIssued'])
      if ok:
        info['dateIssued'] = ok
        c = c - 1
      else:
        skip(info['dateIssued'])
    if 'publisher' in info:
      ok = single('Publisher', info['publisher'])
      if ok:
        info['publisher'] = ok
        c = c - 1
      else:
        skip(info['publisher'])
    if 'dateOther' in info:
      ok = single('Other_Date~Display_Label', info['dateOther'])
      if ok:
        info['dateOther'] = ok
        c = c - 1
        if '@displayLabel' in info['dateOther']:
          ok = append('Other_Date~Display_Label', info['dateOther']['@displayLabel'])
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
      ok = single('Digital_Origin', desc['digitalOrigin'])
      if ok:
        desc['digitalOrigin'] = ok
      else:
        skip(desc['digitalOrigin'])
    if 'extent' in desc:
      ok = single('Extent', desc['extent'])
      if ok:
        desc['extent'] = ok
      else:
        skip(desc['extent'])
    if 'form' in desc:
      ok = single('Form~AuthorityURI', desc['form'])
      if ok:
        desc['form'] = ok
      else:
        skip(desc['form'])
    if 'internetMediaType' in desc:
      mime = getMIME(desc['internetMediaType'])
      if (desc['internetMediaType'] == 'text/plain'):
        mime = 'text/plain';
      if mime:
        ok = single('MIME_Type', mime)
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
      if 'titleInfo' in item:
        if multi('Related_Items~Types', item['titleInfo']['title']):
          if item['@type'] == 'isPartOf':
            return append('Related_Items~Types', 'host')
          else:
            return append('Related_Items~Types', item['@type'])
      elif multi('Related_Items~Types', item):
        return append('Related_Items~Types', item['@type'])
    return skip(item)
  except Exception as e:
    exception(e, item)


# subject
def subject_action(s):
  c = len(s)
  try:
    if 'geographic' in s:
      ok = multi('Subjects_Geographic', s['geographic'])
      if ok:
        s['geographic'] = ok
        c = c - 1
      else:
        skip(s['geographic'])
    if 'hierarchicalGeographic' in s:
      ok = multi('Subjects_Geographic', s['hierarchicalGeographic'])
      if ok:
        s['hierarchicalGeographic'] = ok
        c = c - 1
      else:
        skip(s['hierarchicalGeographic'])
    if 'temporal' in s:
      ok = multi('Subjects_Temporal', s['temporal'])
      if ok:
        s['temporal'] = ok
        c = c - 1
      else:
        skip(s['temporal'])
    if 'cartographics' in s and 'coordinates' in s['cartographics']:
      ok = single('Coordinate', s['cartographics']['coordinates'])
      if ok:
        s['cartographics']['coordinates'] = ok
        c = c - 1
      else:
        skip(['cartographics'])
    if 'topic' in s:                                          # unfortunately, s['topic'] could be a dict or a list
      if '@authority' in s and s['@authority'] == 'lcsh':
        heading = 'LCSH_Subjects'
        c = c - 1
        s['@authority'] = constant.DONE + heading
      else:
        heading = 'Keywords'
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
        ok = multi('Alternative_Titles', title['title'])
    else:
      ok = single('Title', title['title'])
    if ok:
      return ok
    else:
      return skip(title)
  except Exception as e:
    exception(e, title)


