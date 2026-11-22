# World History Atlas

This project documents world history through a chronological series of maps. It aims to create a compelling overview of history for casual users and history enthusiasts.

I always loved reading maps and getting my understanding of history and geography from them. For people like me, maps can pique imagination much better than just text alone. I am an avid reader of Wikipedia and I found that many detailed articles do not go with similarly rich cartographic material (with honorable exceptions of course). Maps in the project are therefore made to complement data already available in Wikipedia articles, which is often the primary source of map data. The idea is to present information in a streamlined and unified format and make it consistent over time.

Care is given to critically assess validity of data used for the maps, correct obvious inconsistencies and enrich the material with information from trustworthy sources. However, with the assumed project vision, professional level of data reliability is not the goal. Project files (QGIS files and Markdown map notes) do however make note of sources used, including links to Wikipedia and other pages, often scientific in nature. As Wikipedia itself cites its sources, it should be possible to pin down trustworthiness of objects found on the maps. Also project files themselves include rough self-assessment of historicity (undisputability) of data elements. Overall, it should be fine to use the maps as a jump off point in research but they do not go through process rigorous enough to make them citable in professional contexts. 

In the project I use artificial intelligence technologies (large language model chatbots) in the following scope:
* initial research to help me identify articles and webpages relevant to the map topic and to narrow down information; Wikipedia has some topics spread through different pages with unclear hierarchy which are easy to miss otherwise;
* validations of included information, including providing extra sources for information I already have;
* creation of supporting scripts automating repetitive actions.

The details of this process may be subject to change but let me state it clearly that this is a love project. Process of reading through data, learning and devising ways to present it in compelling form is crucial part which I do not ever intend to hand off to AI, even if it means that the maps take longer to make.

At present the project uses [**QGIS**](https://qgis.org) for preparation and collation of source map data and [**Inkscape**](https://inkscape.org/) for final layout, typography, annotations, and vector export. 

The intended sequence is to add more maps toward the modern period, making the scope and timing of presented subjects tighter as I move nearer to present time.

## Project structure

- `_YYYY-topic/` - one directory per map, QGIS project with geographic data and historical description;
- `world/` - shared geographic resources for QGIS (vector data for land, ocean, river, lake, bounds, world grid and raster data for relief); they appear in maps as embedded layers;
- `common/` - shared palettes and common project data;
- `design/` - formatting guidance, historical-accuracy notes, templates, icons, and map-making instructions;
- `icons/` - shared SVG symbols;
- `logo/` - project logo artwork;
- `support/` - small utilities used while preparing maps.

"YYYY" in directory name denotes year (for maps presenting a period it marks end boundary), underscore before year indicates BCE dates.

Each published map has a narrative Markdown description file (`.md`) in its directory - map notes. It identifies the period, scope, sources, caveats, and further reading. 

The source QGIS project (`.qgz`) is the primary record for map layers and embedded source data. It references information included in GeoPackage files (`.gpkg`), or comma-separated files (`.csv`). QGIS project files use relative path referencing to source data. That means that if you download a specific map directory, along with at least `world/` and `common/` directories, QGIS project for that map should successfully open.

Structure of data tables in GeoPackage files may differ but they should usually include the following information:
* `fid` - internal identifier created and used by QGIS;
* `Geometry` - point data or vertices of polygons representing information;
* `id` - project specific identifier allowing to link data between map tables and `common` data, e.g. to maintain the same coloring of polygons across maps;
* `name` - names displayed on the map
* `source` - references to sources (usually webpage links); multiple links are separated by semicolon;
* `historicity_*` - self-assessed evaluation of how trustworthy given data point is; this is very approximate and grading is explained in design documents; what makes the score higher is: existence of high-quality, especially scientific sources, quality of article where information is found and confidence of the source article itself (sometimes information is already given as "approximate"); note that there can be several categories of this attribute (like historicity of placement, dating, etc.)
* `historical_year/date_start/end` - boundaries of validity of the given data; e.g. if the country appears on a map dated at year 1600, this attribute can give the information that the country existed between 1590 and 1620;
* `valid_year/date_start/end` - at present serves similar purpose as the previous field and should not be used for interpretation; in the future it may be used for situation where some data point is not documented to exist in the period (does not fall within boundary of historical dates) but it should nevertheless show up on a map.

## Sources

Historical data comes predominantly from Wikipedia and sites linked as sources to Wikipedia articles: scholarly publications, institutional databases, and popular sources. If some webpage is used widely for a given map, it is listed in "Sources" or "Further reading" section of map notes.

For the purpose of drawing maps, the following sources are used:
- **Vector and raster basemap data:** uses [Natural Earth](https://www.naturalearthdata.com) data.
- **Symbols and artwork:** icons partially based on [SVG Repo](https://www.svgrepo.com).

In general, sources are listed along with project data in QGIS project files and in map notes.

## License

Original project content is licensed under the **Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)**. See [LICENSE.md](LICENSE.md).

Third-party basemaps, datasets, fonts, icons, photographs, and artwork remain subject to their own licenses. Details about license terms of used content are listed along with references to sources, in a way to sufficiently satisfy licensing conditions. See each map's source notes for details.

## Contact

At present this is a solo project, not accepting contributions. GitHub can be used to report problems with the data and for other inquiries.