#!/usr/bin/env node

// const args = require('args');
const fs = require('fs');
const path = require('path');
const replaceStream = require('replacestream');
const node_xml_stream = require('node-xml-stream');
const parser = new node_xml_stream();
const filename = process.argv[2];

if (!filename) return console.log('usage: mf2json input_xml_file');
if (!fs.existsSync(filename)) return console.log('File not found: ' + filename);

const isContextToegang = path.basename(filename).indexOf("CON_")==0;

let tag,item,sub_item,is_sub,sub_tag,veldnaam,items=[],counter=0,sbk;
let stream = fs.createReadStream(filename, 'UTF-8')

stream.on('close', function (err) {
  done();
});

console.log('['); //open json
stream.pipe(replaceStream('<ZR>', '\n')).pipe(parser); //fix incorrect XML before sending it to XML parser  

parser.on('opentag', function(name, attrs) {
  tag = name.toLowerCase();
  if (name=='AHD') { //mis je zo het laatste item niet?
    if (item && item["skipoutput"]!="Ja") {

      delete item["skipoutput"];
      delete item["canmakephysic"];
      delete item["fnc_bep_toegang"];
      delete item["basismap"];
      delete item["opslaglokatie"];
      delete item["ahd_id_top"];
      delete item["sde_id"];
      delete item["sorteerblokkade"];
      delete item["reageer_email"];
      delete item["voorlopig_nummer"];
      delete item["volgnummer"];
      delete item["adt_id"];
      delete item["kot_code"];
      delete item["uitleenprioriteit"];
      delete item["origineel"];
      delete item["datecreated"];
      delete item["datemutated"];
      delete item["usercreated"];
      delete item["usermutated"];
      delete item["oid"];
      delete item["auditheaders"];
      delete item["aantuitvorm"];
      delete item["betaaldeprijs_1"];
      delete item["naamvorigeeigenaar_1"];
      delete item["vermeldinjaarverslag_1"];
      delete item["verworvenvanop_1"];
      delete item["wijzevanverwerving_1"];
      delete item["overige_bestanden"];
      delete item["bestand_padnaam"];
      delete item["bestand_pad_is_basispad"];
      delete item["bestand_bestandsnaam"];
      delete item["beschrijver_naam_1"];
      delete item["beschrijver_datum_1"];

      // for (const i in item["relaties"]) {
      //   const rel = item["relaties"][i];
      //   if (/PAP/.test(rel.rel_stuk_aet_code)) {
      //     //item["relaties"].splice(i,1); //
      //     delete item["relaties"][i]; 
      //   } else {
      //     const aet_code = (rel.rel_stuk_aet_code || rel.rel_top_aet_code).toLowerCase();
      //     item["relaties"][i] = rel.rel_adt_id + "/" + aet_code + "/" + rel.ahd_id_rel;
      //   }
      // }
      if (Array.isArray(item["relaties"])) {
        item["relaties"] = item["relaties"].map(item => /PAP/.test(item.rel_stuk_aet_code) ? null : "rst:"+item.rel_rst_id + " id:" + item.ahd_id_rel); //item.rel_adt_id + "/" + item.rel_top_code + "/" + 
        item["relaties"] = item["relaties"].filter(item => item!=null);
      }


      console.log(JSON.stringify(item,null,4) + ",");
    }

    // if (counter++>10) done();  //voor nu maar een paar nodes

    item = { GUID:"" };
    // items.push(item);
  }
  else if (/<AWE>|<ABD>|<REL>|<TWD>|<TWE>|<FVD>|<AGR>|<SOS>|<SBK>/.test("<"+name+">")) {
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
  else if (!is_sub) {
    if (tag=="guid") tag=tag.toUpperCase();
    if (tag=="aet") text=text.toLowerCase();
    item[tag] = text; //is property binnen een AHD
  }
  else if (sub_tag=="AWE") {
    // if (!item["flexvelden"]) item["flexvelden"] = {};
    if (tag=="naam") veldnaam = text.toLowerCase();
    // else if (tag=="waarde") item["flexvelden"][veldnaam] = text
    else if (tag=="waarde") item[""+veldnaam] = text
  }
  else if (sub_tag=="ABD") {
    // if (!item["bestand"]) item["bestand"] = sub_item;
    item["bestand_"+tag] = text;
  }
  else if (sub_tag=="TWD") {
    if (!item["trefwoorden"]) item["trefwoorden"] = [];
    if (tag=="trefwoord") item["trefwoorden"].push(text);
  }
  // else if (!isContextToegang && 
  else if (sub_tag=="REL") {
    if (!item["relaties"]) item["relaties"] = [];
    sub_item[tag] = text;
  } 

  // else if (sub_tag=="SBK") {    
  //   if (!item["onderliggende_archiefeenheidssoorten"]) item["onderliggende_archiefeenheidssoorten"] = {}; //archiefeenheidssoorten
  //   if (tag=="code") sbk = item["onderliggende_archiefeenheidssoorten"][text] = [];
  // }
  // else if (sub_tag=="FVD") { //FVD's zijn de flexvelden per SBK
  //   if (tag=="naam") sbk.push(text.toLowerCase());
  // }
});

function done() {
  //console.log(JSON.stringify(items,null,4));
  console.log(']');
  process.exit();
}

