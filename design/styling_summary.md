# Map styling summary

## General

Maps are created in ISO formats (A1-A4), landscape or portrait and sizes are defined in QGIS in millimeters.
For the purpose of screen display and raster file export 300 dpi resolution is assumed.

### Layer order

From top to bottom the layers are as follows:

* Extra - Used for extra insets, like timelines, infographics, photos, etc.;
* Border - white-filled path plus a path filled with checkerboard pattern, both with 0.2 mm stroke, used for a page border containing coordinates;
* Labels - Textual labels for areas, cities names, geographic features;
* Places - Symbology for cities and other places;
* Grid - World grid (logitudinal or latitudinal graticules);
* Map-specific geographic features - Extra lakes or changed ocean shorelines;
* Lakes;
* Rivers;
* Shaded relief - Simulated shading of elevated terrain to give impression of local terrain ruggedness;
* Areas - Countries, regions, marked areas;
* Land - Continents;
* Ocean;
* Bounds - Bounds of world projection.

Shaded relief uses Multiply blend mode so that hills and mountain darken the layers beneath it.

---

## Geographic features

`world-bounds` use stroke #000000, 0.2 mm thick.
`world-ocean` uses fill of #c6ecff (light blue) and stroke of #0978ab (medium blue). Stroke is 0.1 mm thick (effectively 0.05 mm as half of stroke is hidden behind the land layer)
`world-land` uses fill of #fefef0 (off-white) and no stroke. Delineation between land and water comes fully from stroke of oceans and lakes.
`world-rivers` use stroke of #0978ab (medium blue). Thickness is variable in 0.16–0.25 mm range and depends on river size (derived from SCALERANK attribute).
`world-shaded-relief` is a raster image. It uses Multiply blend mode, brightness 80, gamma 1.50, contrast -20 and cubic resampling.
`world-grid-standard` use stroke of `#808080`, 0.1 mm thick.
`world-grid-equator` uses stroke of `#808080`, 0.2 mm thick.
`world-grid-special` (polar circles and tropics) use stroke of `#808080`, 0.2 mm thick, dashed 0.8 mm / 0.4 mm gap.

## Areas and cultures

`areas` are regions of settlement which do not have any state-like organization. There are a few default settings used:
* Settled societies use fill of #ccc4ad and no stroke. Labels are colored #000000 and use normal font style.
* Pastoral (mobile) societies use no fill and no stroke. Labels are colored #666666 and use normal font style.
* Hunter-gatherer societies use no fill and no stroke. Labels are colored #3c5a3c and use normal font style.
Otherwise areas are marked as needed, depending on the map.
`archeological-cultures` are artifacts, buildings, and monuments from a specific period and region that may constitute the material culture remains of a particular past human society. They are represented by regions with no fill and light-colored stroke 1 mm thick (those regions are clipped by themselves so that actual stroke comes as 0.5 mm). Labels are colored #ff0000 (red).

---

## Fonts

All text uses **Fira Sans** font. Standard size is 6 pt and emphasis is done by making font bold and/or italic. When marking of large region is needed, it is preferred to make font spacing bigger, rather than making font itself bigger. For titles and other special cases, 9 pt or 12 pt font size can be used.

Some text labels use a white buffer which is a white (`#ffffff`) stroke painted behind the text (`paint-order: markers stroke fill`). The stroke is 0.3 mm thick which comes as 0.15 mm effective thickness (half of stroke is hidden behind the text).

Titles use 12 pt #000000 bold font. Subtitles may use 12 pt regular font, or 9 pt regular font of the same color.
Ocean names use 12 pt #0978ab regular font.
Names of other water bodies (seas, lakes, rivers) use 6 pt #0978ab italic font.
World grid uses 6 pt #000000 italic font inside the map and 6 pt #000000 light font of the same color in border area.
Standard labels (e.g. for countries or cities) use 6 pt #000000 regular font.