# Rochford Bins API

An API for the Rochford District Council bin collection calendar. Useful for home automation
projects that notify you of the bin collection days.

Note that this isn't a *proper* API. It's a series of JSON files scraped from the council website,
hosted on GitHub Pages. This is done (a) for simplicity and (b) because the tools are free!

## Structure of the files

There are two endpoints (types of files):

| Endpoint                      | Description                                                                   |
| ----------------------------- | ----------------------------------------------------------------------------- |
| `/roads.json`                 | A list of all roads their area and their *usual* collection day.              |
| `/collections/:roadName.json` | A list of the collection days and associated information for a specific road. |

### All Roads

```json
{
 "all_roads": [
    {
        "road": "",
        "area": "",
        "collection_day": ""
    }
 ]
}
```


### Specific Road

```json
{
    "road": "",
    "area": "",
    "usual_collection_day": "",
    "collection_days": {
        "2024-01-01": "Non-Recyclables",
        "2025-01-01": "Recyclables"
    }
}
```
