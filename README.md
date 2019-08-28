# MF-Export-XML-to-JSON
Dit script (index.js) maakt van een MAIS Flexis Export XML-bestand een JSON bestand.

Voorbeeld output:
```json
[
  {
    "id": "41799421",
    "aet": "COL",
    "voorlopig_nummer": "0",
    "code": "BEELDBANK_FOT_DOC_1A",
    "volgnummer": "1",
    "adt_id": "39",
    "kot_code": "BES",
    "uitleenprioriteit": "1",
    "guid": "689F075A8A60E609E0534701000A426A",
    "flexvelden": {
      "titel": "Fotografische documenten 1A",
      "datecreated": "30-03-2018 11:40 21",
      "datemutated": "10-07-2018 09:01 52",
      "usercreated": "...",
      "usermutated": "...",
      "reageer_email": "...",
      "opslaglokatie": "fonc-hua",
      "basismap": "Beeldbank",
      "fnc_bep_toegang": "Ja",
      "canmakephysic": "Ja"
    },
    "trefwoorden": [
      "Beeldbank",
      "Beeldbank HUA"
    ],
    "bestand": {
      "pad_is_basispad": "0"
    },
    "relaties": [
      {
        "rel_lr": "AHD_ID2",
        "ahd_id_rel": "40815696",
        "rel_adt_id": "39",
        "rel_top_aet_code": "ABK2",
        "rel_top_code": "BEELDBANK",
        "rel_rst_id": "6",
        "rel_volgnr": "2",
        "rel_volgnr2": "1"
      }
    ],
    "onderliggende_archiefeenheidssoorten": {
      "BTEK": [
        "beschrijving",
        "bouwwerk",
        "redvorm",
        "adres",
        //......
      ],
      "COL": [
        "auteursrechtrechthebbende",
        "auteursrechtovergedragen",
        "auteursrechtverlooptna",
        "digiverzoek",
        "synchroniseren_met_import",
        "archvormer",
        //......
      ],
      "RUB": [
        "auteursrechtovergedragen",
        "digiverzoek",
        "reageer_email",
        //.....
      ],
      //......
    }
  },

  {
    "id": "41799439",
    "aet": "RUB",
    "voorlopig_nummer": "0",
    "volgnummer": "1",
    "ahd_id": "41799421",
    "adt_id": "39",
    "ahd_id_top": "41799421",
    "kot_code": "BES",
    "uitleenprioriteit": "1",
    "guid": "689F075A8A70E609E0534701000A426A",
    "flexvelden": {
      "titel": "1 - 6.499 (fotografische documenten op opzetkartons)",
      "datecreated": "30-03-2018 12:16 25",
      "usercreated": "...",
      "datemutated": "24-04-2018 15:32 11",
      "usermutated": "..."
    }
  },
  //...
]

