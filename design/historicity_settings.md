# Historicity settings

## Background

The project aims for historical accuracy as one of elements of its appeal. The intended target quality of maps can be equalled with its main sources: extensive, well-researched Wikipedia articles containing several strong source references. However, not all sources include highest quality of information, and even high quality sources present some information as contestable. The maps do not aim to be as detailed and irrefutable as the ones included in professional sources, especially scientific papers.

Project files include links to sources used. Alongside, the project includes evaluation of historicity of information coming from these sources. This is to help in discussions or when maps are used in derived contexts, so that the end user may better judge if information is trustworthy enough.

This document includes guide how historicity of information is graded to help in aforementioned judgment.

## Guidelines

Information for data points should include historicity attribute(s) in source files (e.g. GeoPackage `gpkg` files, commma-separate values `csv` files). There should be as many historicity-related attributes as needed to evaluate different aspects (e.g. an ancient city can be located without doubt so its placement is historical but dating its existence is problematic):
* placement - relates to placement on the map (single point, or range of borders in case of areas);
* dating - relates to dates between which some entity or phenomenon was valid;
* population - relates to population of cities, or countries;
* extra_info - relates to extra information present in information boxes.

## Settings

The following grading of historicity is currently used:

* historical: Information is sourced with high confidence and based on concrete underlying data (scientific or otherwise trusted sources). Example: placement of cities, modern country borders

* interpretive: Information considered trustworthy but having element of discretion in data ordering and/or selection. By nature this cannot be undisputed even if it is based on fully historical data. Examples: areas of strongest development, biggest population centres.

* informed: Information is based on historical facts but some aspects cannot be fully ascertained and may be subject to discussion. This best describes situations where consensus forms around some facts which have strong track record in scientific sources but because of nature of the subject cannot be decided with full certainty. Examples: exact placement of some ancient cultures, pre-modern borders.

* inconclusive: Existence is based on historical record but some important aspects like specific placement, borders, or other attributes (e.g. population) do not have definitive track record or cited values are contentious and there is no convincing agreement in available sources; also situations where some attribute is derived from available information. Example: placement of archeological cultures borders based only on existence of type sites.

* Conjectural - Information is plausible but not based on specific historical records; this usually means data that awaits better research but may also apply to abstract information that is presented only to support larger narrative and improve clarity. Example: "nomadic peoples" label for area between known settled socities.

* Fictitious - Regarded wholly or in large part non-historical; still included for its common recognition, or role in narration; this needs to be marked as non-historical on the map. Example: references to legendary early rulers.

By its nature, categories are discretional, and may not be fully comparable between maps. They are meant only to give general guidance.
