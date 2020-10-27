# van MAIS Flexis Export XML naar JSON
Dit script (index.js) maakt van een MAIS Flexis Export XML-bestand een JSON bestand.

Voorbeeld output:
```json
{ "@context": "context.json", "@graph": [
{
    "GUID": "B8CA17023A134E8CA9C22DF85F149D39",
    "aet": "col",
    "code": "BEELDBANK",
    "id": "131/5430230",
    "link": "http://proxy.archieven.nl/131/B8CA17023A134E8CA9C22DF85F149D39",
    "soortarchief": "Atlas en Beeldbank",
    "titel": "BEELDBANK",
    "volgnummer": "5430230"
}
,
{
    "GUID": "B8691E4090BC4486BCD3109D04FD915F",
    "aet": "rub",
    "datemutated": "03-06-2019 15:02",
    "id": "131/5475188",
    "link": "http://proxy.archieven.nl/131/B8691E4090BC4486BCD3109D04FD915F",
    "parentItem": "131/5430230",
    "rootItem": "131/5430230",
    "titel": "Muziekvereniging Juliana Marken",
    "volgnummer": "5430231"
}
,
{
    "GUID": "FF9F873466F411E39374CBE597083A45",
    "aet": "ft",
    "auteursrecht_beperkt": "lst_1061/Nee",
    "auteursrechten": "vervaardiger",
    "beschrijving": "STICK_ATLAS/Marken, muziekver. Juliana/F001793 Muziekvereniging Juliana",
    "code": "WAT120003109",
    "datecreated": "11-09-2018 08:54",
    "datemutated": "03-06-2019 15:31",
    "deelcollectie": "lst_2/Muziekvereniging-Juliana-Marken",
    "herkomst": "Margreet Lenstra",
    "id": "131/5484213",
    "kadastrale_kaarten": "lst_1061/Nee",
    "link": "http://proxy.archieven.nl/131/FF9F873466F411E39374CBE597083A45",
    "parentItem": "131/5475188",
    "photoid": "WAT120003109",
    "rootItem": "131/5430230",
    "rst_113": "131/5427754",
    "rst_bes-rubr": "131/5430129",
    "thumb": "http://proxy.archieven.nl/thumb/131/FF9F873466F411E39374CBE597083A45",
    "tst_thwtw": [
        "https://waterlandsarchief.nl/def/twd#muziek",
        "https://waterlandsarchief.nl/def/twd#Marken"
    ],
    "uiterlijkevorm": "lst_2/Foto-s",
    "volgnummer": "5430236"
}
]}
```

