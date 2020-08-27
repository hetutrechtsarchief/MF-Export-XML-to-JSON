#!/usr/bin/env python3

import xml.parsers.expat
import json,sys,os,argparse,time,re
import mysql.connector
from html.parser import HTMLParser
import logging
  
# def relatieMapping(rel):
#     return dict(relatiesoort=rel['rel_rst_id'], item=getGUIDById(rel['ahd_id_rel']))
#   # try:
#   #   return '<' + getRelatieSoort(rel['rel_rst_id']) + '> ' + getGUIDById(rel['ahd_id_rel'])  
#   # except ValueError as e:
#   #   log.warning('Warning: cannot find GUID of 'related' item for '+item['GUID']+ ': ' + repr(e)) 

# def trefwoordMapping(twd):
#   return dict(trefwoordsoort=twd['tst_id'], trefwoord=twd['trefwoord'])

def getGUIDById(id):
  if id in GUIDsById: # local lookup-table
    return GUIDsById[id]
  
  # if not found in local lookup-table, try database
  sql = 'SELECT GUID FROM {} where adt_id="{}" and id="{}"'.format(tbl,adt_id,id)
  dbcur.execute(sql)
  row = dbcur.fetchone()
  if row:
    return row[0];

  log.warning('getGUIDById: Cannot find GUID for id='+id)

  return adt_id + '/' + id
  #raise ValueError('getGUIDById: Cannot find GUID for id='+id);

def setGUIDById(id,GUID):
  GUIDsById[id] = GUID # store in local lookup-table

  # also store in database
  sql = 'INSERT IGNORE INTO {} (id,adt_id,GUID) VALUES ("{}","{}","{}")'.format(tbl,id,adt_id,GUID)

  dbcur.execute(sql)
  db.commit()

def makeSafeURIPart(s):
  # spreadsheet: [–’&|,\.() ""$/':;]"; "-") ;"-+";"-"); "[.-]$"; ""))
  s = re.sub(r"[–’+?&=|,\.() \"$/']", "-", s) # replace different characters by a dash
  s = re.sub(r"-+", "-", s) # replace multiple dashes by 1 dash
  s = re.sub(r"[^a-zA-Z0-9\-]", "", s) # strip anything else now that is not a alpha or numeric character or a dash
  s = re.sub(r"^-|-$", "", s) # prevent starting or ending with . or -
  if len(s)==0:
    #raise ValueError("makeSafeURIPart results in empty string")
    log.warning("makeSafeURIPart results in empty string")
    # fix this by replacing by 'x' for example
    s="x"
  return s

def saveItem(item):  # 'saves' and prints the object as JSON
  if not item:
    return

  global prevItem

  # log.warning(repr(item))

  setGUIDById(item['id'], item['GUID'])

  if 'ahd_id' in item:
    try:
      item['parentItem'] = getGUIDById(item['ahd_id'])
    except ValueError as e:
      log.warning('Warning: cannot find GUID of parentItem for '+item['GUID'] + ': ' + repr(e)) 

  # Trefwoorden
  if 'twd' in item:
    for twd in item['twd']:
      itemId = 'twd'+twd['tst_id']
      if itemId in item:
        item[itemId] = [ item[itemId] ]
        item[itemId].append(twd['trefwoord'])
      else:
        item[itemId] = twd['trefwoord']
    item.pop('twd')

  # Relaties
  if 'rel' in item:
    for rel in item['rel']:
      key = 'rel'+rel['rel_rst_id']

      #CHECKME
      try:
        value = getGUIDById(rel['ahd_id_rel'])
      except ValueError as e:
        value = adt_id + "/" + rel['ahd_id_rel']


      if key in item:
        if not type(item[key]) is list:
          item[key] = [ item[key] ]
        item[key].append(value)
      else:
        item[key] = value
    item.pop('rel')

  # combine adt_id and id to one identifier
  if 'adt_id' in item and 'id' in item:
    item['id'] = item['adt_id'] + '/' + item['id']


  # if previous item and current item share the same parent connect them
  if (prevItem 
    and ('parentItem' in prevItem) 
    and ('parentItem' in item) 
    and (prevItem['parentItem']==item['parentItem']) 
    and ('GUID' in prevItem) 
    and not 'followsItem' in item):
      item['followsItem'] = prevItem['GUID']
  prevItem = item

  # skip item if needed
  if 'skipoutput' in item:  
    if item['skipoutput']=='Ja':
      return

  # remove properties from dict that are on the skipfields list
  for line in skipfields:
    if line in item:
      item.pop(line)


  # print item
  # print(dir(item))
  print(json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False))

class Parse(HTMLParser):
   
  def handle_starttag(self, name, attrs):
    global tag, item, sub_tag, sub_item, is_sub, sbk_items, sbk_item, fvd_item, itemIndex
    tag = name  # HTMLParser converts all tagnames to lower();
    if name=='ahd':
      if item:
        if itemIndex>0:
          print(',')
        itemIndex = itemIndex + 1
        saveItem(item)

      # start a new item
      item = { 'GUID': '' };

    elif re.match(r'<awe>|<abd>|<rel>|<twd>|<twe>|<fvd>|<agr>|<sos>|<sbk>', '<'+name+'>'): 
      # er volgt nu een sub_item in de XML. sub_items staan in de XML meestal buiten/na de AHD behalve bij AWE.
      # toch horen ze bij de AHD waar ze direct na komen.
      is_sub = True;
      sub_tag = name;
      sub_item = {};

      if name=='sbk':
        sbk_item = {}
        sbk_item['fvd'] = []
        # sbk_items.append(sbk_item)

      if name=='fvd':
        fvd_item = {}
        sbk_item['fvd'].append(fvd_item)
     
      if item and (name == 'rel'):
        if not name in item:
          item[name] = [];
        item[name].append(sub_item)

      if item and (name == 'twd'):
        if not name in item:
          item[name] = [];
        item[name].append(sub_item)
    
  def handle_data(self, txt):
    global text
    text = text + txt.strip()

  def handle_endtag(self, name):
    global text, is_sub, tag, sub_tag, veldnaam, fvd_item, aet

    if not item:
      return

    # vaste velden
    elif tag and not is_sub:
      if tag == 'guid':
        tag = 'GUID';
      elif tag == 'aet':
        text = text.lower(); # make aet code lowercase
        aet = text

      item[tag] = text; #is property binnen een AHD

    # flexvelden
    elif sub_tag == 'awe':
      if tag == 'naam':
        veldnaam = text.lower()
      elif tag == 'waarde':
        if veldnaam:
          item[veldnaam] = text

          if aet and aet in sbk_items and veldnaam in sbk_items[aet]:
            item[veldnaam] = "lst" + sbk_items[aet][veldnaam] + "/" + makeSafeURIPart(item[veldnaam])

        veldnaam = ''
    
    # bestanden
    elif sub_tag == 'abd':
      item['bestand_' + tag] = text
    
    # trefwoorden en relaties
    elif re.match(r'twd|rel',sub_tag):
      if name!=sub_tag:
        sub_item[name] = makeSafeURIPart(text); 

    # bewaar tekstwaarde van element in sbk (soorten per blok)
    elif sub_tag == 'sbk':   # let op: if sub_tag==sbk (wanneer een sub_item binnen de sbk sluit)
      sbk_item[name] = text

    # wanneer een sbk klaar is dan de data per FVD mappen/reduceren tot NAAM:LOV_METHODE
    # hiermee kan vervolgens gemakkelijk worden opgevraagd of een waarde van een flexveld uit een lijst komt of vrije tekst is
    elif name == 'sbk':      # let op: if name==sbk (wanneer de sbk zelf echt sluit)
      sbk_items[sbk_item["code"].lower()] = {}
      for fvd in sbk_item["fvd"]:
        if fvd["lov_methode"]!="0":
          sbk_items[sbk_item["code"].lower()][fvd["naam"].lower()] = fvd["lov_methode"]

    elif sub_tag == 'fvd':
      fvd_item[name] = text

    # elif sub_tag == 

    # elif sub_tag == 'fvd':
    #   sbk_item[name] = "X:"+text

    # elif sub_tag == 'fvd':
    #   # fvd_item[name] = text
    #   if name!=sub_tag:
    #     sub_item[name] = text; 

    text = ''

    if name == sub_tag:
      tag = ''
      is_sub = False;
      
#######################################################
## MAIN 
#######################################################

# prepare for logging warnings and errors
logging.basicConfig(format='%(message)s')
log = logging.getLogger(__name__)

# parse command line parameters/arguments
argparser = argparse.ArgumentParser(description='MF Export XML to JSONLD')
argparser.add_argument('--xml',help='input xml file', required=True)
argparser.add_argument('--adt_id',help='organisation id', required=True)
# argparser.add_argument('--rst',help='relatiesoorten csv file', required=True)
argparser.add_argument('--skipfields',help='text file with fields to skip') #, required=True)
argparser.add_argument('--db',help='use database for lookup. requires 4 params: user password host dbname', required=True, nargs=4)
args = argparser.parse_args()

### globals
tbl = 'idguid' # name of lookup table in database for id vs GUID
adt_id = args.adt_id  # this is set in main by args.adt_id
tag = ''
sub_tag = ''
text = ''
aet = ''
item = None
prevItem = None
is_sub = False
lijsten = []
GUIDsById = {} # local lookup table in RAM for id vs GUID
# sbk_item = {}
sbk_items = {} # dict instead of list
fvd_item = {}
itemIndex = 0

# connect to database containing lookup-table for id vs GUID
db = mysql.connector.connect(user=args.db[0],password=args.db[1],host=args.db[2],database=args.db[3])
dbcur = db.cursor()

# load skip fields text file
skipfields = []
if args.skipfields:
  with open(args.skipfields, 'r') as file:
    for line in file:
      skipfields.append(line.strip())

# open xml file and read lines
with open(args.xml, 'r') as file:
  print('{ "@context": "context.json", "@graph": [')
  for line in file:
    line = line.replace('<ZR>', '\n')
    xml = Parse()
    xml.feed(line)
  print(',')
  saveItem(item) # last one
  print(']}')

  # print(json.dumps(sbk_items, indent=4, sort_keys=True, ensure_ascii=False),',')

