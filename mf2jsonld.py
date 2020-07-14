#!/usr/bin/env python3

import xml.parsers.expat
import json,sys,os,argparse,time,re
import mysql.connector
from html.parser import HTMLParser
import logging
  
def relatieMapping(rel):
    return dict(relatiesoort=rel['rel_rst_id'], item=getGUIDById(rel['ahd_id_rel']))
  # try:
  #   return '<' + getRelatieSoort(rel['rel_rst_id']) + '> ' + getGUIDById(rel['ahd_id_rel'])  
  # except ValueError as e:
  #   log.warning('Warning: cannot find GUID of 'related' item for '+item['GUID']+ ': ' + repr(e)) 

def trefwoordMapping(twd):
  return dict(trefwoordsoort=twd['tst_id'], trefwoord=twd['trefwoord'])

def getGUIDById(id):
  if id in GUIDsById: # local lookup-table
    return GUIDsById[id]
  
  # if not found in local lookup-table, try database
  dbcur.execute('SELECT GUID FROM {} where adt_id="{}" and id="{}"'.format(tbl,adt_id,id))
  row = dbcur.fetchone()
  if row:
    return row[0];

  raise ValueError('getGUIDById: Cannot find GUID for id='+id);

def setGUIDById(id,GUID):
  GUIDsById[id] = GUID # store in local lookup-table

  # also store in database
  dbcur.execute('INSERT IGNORE INTO {} (id,adt_id,GUID) VALUES ("{}","{}","{}")'.format(tbl,id,adt_id,GUID))
  db.commit()

def getRelatieSoort(rst_id):
  dbcur.execute('SELECT Code,Omschrijving_Links,Omschrijving_Rechts FROM relatiesoorten where id={}'.format(rst_id))
  row = dbcur.fetchone()
  if row:
    return row[0]+'/'+row[1]+'/'+row[2];

def saveItem(item):  # 'saves' and prints the object as JSON
  global prevItem

  setGUIDById(item['id'], item['GUID'])

  if 'ahd_id' in item:
    try:
      item['parentItem'] = getGUIDById(item['ahd_id'])
    except ValueError as e:
      log.warning('Warning: cannot find GUID of parentItem for '+item['GUID'] + ': ' + repr(e)) 

  # Relaties
  if 'relaties' in item:
    item['relaties'] = list(map(relatieMapping, item['relaties']))

  # Trefwoorden
  if 'trefwoorden' in item:
    item['trefwoorden'] = list(map(trefwoordMapping, item['trefwoorden']))

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
  print(json.dumps(item, indent=4, sort_keys=True, ensure_ascii=False),',')

class Parse(HTMLParser):
   
  def handle_starttag(self, name, attrs):
    global tag, item, sub_tag, sub_item, is_sub
    tag = name  # HTMLParser converts all tagnames to lower();
    if name=='ahd':
      if item:
        saveItem(item)

      # start a new item
      item = { 'GUID': '' };

    elif re.match(r'<awe>|<abd>|<rel>|<twd>|<twe>|<fvd>|<agr>|<sos>|<sbk>', '<'+name+'>'): 
      # er volgt nu een sub_item in de XML. sub_items staan in de XML meestal buiten/na de AHD behalve bij AWE.
      # toch horen ze bij de AHD waar ze direct na komen.
      is_sub = True;
      sub_tag = name;
      sub_item = {};

      if item and (name == 'rel'):
        if not 'relaties' in item:
          item['relaties'] = [];
        item['relaties'].append(sub_item)

      if item and (name == 'twd'):
        if not 'trefwoorden' in item:
          item['trefwoorden'] = [];
        item['trefwoorden'].append(sub_item)
    
  def handle_data(self, txt):
    global text
    text = text + txt.strip()

  def handle_endtag(self, name):
    global text, is_sub, tag, sub_tag, veldnaam

    if not item:
      return

    # vaste velden
    elif tag and not is_sub:
      if tag == 'guid':
        tag = 'GUID';
      elif tag == 'aet':
        text = text.lower(); # make aet code lowercase 

      item[tag] = text; #is property binnen een AHD

    # flexvelden
    elif sub_tag == 'awe':
      if tag == 'naam':
        veldnaam = text.lower()
      elif tag == 'waarde':
        if veldnaam:
          item[veldnaam] = text
        veldnaam = ''
    
    # bestanden
    elif sub_tag == 'abd':
      item['bestand_' + tag] = text
    
    # trefwoorden en relaties
    elif re.match(r'twd|rel',sub_tag):
      if name!=sub_tag:
        sub_item[name] = text; 

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
argparser.add_argument('--rst',help='relatiesoorten csv file', required=True)
argparser.add_argument('--skipfields',help='text file with fields to skip', required=True)
argparser.add_argument('--db',help='use database for lookup. requires 4 params: user password host dbname', required=True, nargs=4)
args = argparser.parse_args()

### globals
tbl = 'idguid' # name of lookup table in database for id vs GUID
adt_id = args.adt_id  # this is set in main by args.adt_id
tag = ''
sub_tag = ''
text = ''
item = None
prevItem = None
is_sub = False
GUIDsById = {}; # local lookup table in RAM for id vs GUID

# connect to database containing lookup-table for id vs GUID
db = mysql.connector.connect(user=args.db[0],password=args.db[1],host=args.db[2],database=args.db[3])
dbcur = db.cursor()

# load skip fields text file
skipfields = []
with open(args.skipfields, 'r') as file:
  for line in file:
    skipfields.append(line.strip())

# open xml file and read lines
with open(args.xml, 'r') as file:
  print('[')
  for line in file:
    line = line.replace('<ZR>', '\n')
    xml = Parse()
    xml.feed(line)
  saveItem(item)
  print(']')

