# Indian state boundaries

`india-states.geojson` is a simplified GeoJSON derivative of DataMeet's
`States/Admin2` shapefile at pinned commit
`b3fbbde595310b397a55d718e0958ce249a4fa1f`.

- Source: https://github.com/datameet/maps/tree/b3fbbde595310b397a55d718e0958ce249a4fa1f/States
- License: CC BY 4.0
- Processing: cleaned and simplified to 8% with Mapshaper, retaining all 36
  source features and the original `ST_NM` state-name attribute.

The Regional Dashboard renders India's 28 states plus Delhi. The ten areas
present in Retail IQ's source data are colored by the selected business metric;
the remaining state boundaries render in neutral gray.
