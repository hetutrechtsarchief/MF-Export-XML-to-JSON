#!/usr/bin/env node
//usage: $ ./index.js INPUT.xml

// const args = require('args');
const fs = require('fs');
const path = require('path');
const replaceStream = require('replacestream');
const node_xml_stream = require('node-xml-stream');
const parser = new node_xml_stream();
const filename = process.argv[2];

if (!filename) return console.log('usage: ./index.js input_xml_file');
if (!fs.existsSync(filename)) return console.log('File not found: ' + filename);

const isContextToegang = path.basename(filename).indexOf("CON_")==0;

let tag,item,sub_item,is_sub,sub_tag,veldnaam,items=[],counter=0;
let stream = fs.createReadStream(filename, 'UTF-8')
let sbk;

stream.on('close', function (err) {
  done();
});

console.log('['); //open json
stream.pipe(replaceStream('<ZR>', '\n')).pipe(parser); //fix incorrect XML before sending it to XML parser  

parser.on('opentag', function(name, attrs) {
  tag = name.toLowerCase();
  if (name=='AHD') {
    if (item) console.log(JSON.stringify(item,null,4) + ",");

    // if (counter++>10) done();  //voor nu maar een paar nodes

    item = {};
    // items.push(item);
  }
  else if (/<AWE>|<ABD>|<REL>|<TWD>|<FVD>|<AGR>|<SOS>|<SBK>/.test("<"+name+">")) {
    //er volgt nu een sub_item in de XML. sub_items staan in de XML meestal buiten/na de AHD behalve bij AWE.
    //toch horen ze bij de AHD waar ze direct na komen.
    is_sub = true;
    sub_tag = name;
    sub_item = {};

    if (!isContextToegang && item && name=="REL") {
      if (!item["relaties"]) item["relaties"] = [];
      item["relaties"].push(sub_item);
    }
  }
});

parser.on('closetag', function(name) {
  if (name==sub_tag) is_sub=false;
});

parser.on('text', function(text) {
  if (!item) return;
  else if (!is_sub) item[tag] = text; //is property binnen een AHD
  else if (sub_tag=="AWE") {
    if (!item["flexvelden"]) item["flexvelden"] = {};
    if (tag=="naam") veldnaam = text.toLowerCase();
    else if (tag=="waarde") item["flexvelden"][veldnaam] = text
  }
  else if (sub_tag=="ABD") {
    if (!item["bestand"]) item["bestand"] = sub_item;
    sub_item[tag] = text;
  }
  else if (sub_tag=="TWD") {
    if (!item["trefwoorden"]) item["trefwoorden"] = [];
    if (tag=="trefwoord") item["trefwoorden"].push(text);
  }
  else if (!isContextToegang && sub_tag=="REL") {
    if (!item["relaties"]) item["relaties"] = [];
    sub_item[tag] = text;
  } 
  else if (sub_tag=="SBK") {    
    if (!item["onderliggende_archiefeenheidssoorten"]) item["onderliggende_archiefeenheidssoorten"] = {}; //archiefeenheidssoorten
    if (tag=="code") {
      sbk = item["onderliggende_archiefeenheidssoorten"][text] = [];
    }
  }
  else if (sub_tag=="FVD") { //FVD's zijn de flexvelden per SBK
    if (tag=="naam") sbk.push(text.toLowerCase());
  }
});

function done() {
  //console.log(JSON.stringify(items,null,4));
  console.log(']');
  process.exit();
}

