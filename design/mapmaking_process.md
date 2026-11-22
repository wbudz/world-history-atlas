# New map preparation
Copy a previous map from the project.
Settle on the map format (size, orientation) and scope (which decides the scale). Map format should be A2 (for large scope and/or high detail maps), otherwise A3.

# QGIS preparation
Prepare all data structures to be exported.
Open layout to be exported. Check if all intended layers are included.
Choose Layout --> Export to SVG and export to 'export' subdirectory. Use settings:
* export map layers as SVG groups: checked;
* always export as vectors: checked;
* export RDF metadata: checked;
* simplify geometries to reduce output file size: unchecked;
* text export: always export text as text objects;
* crop to content: checked (all margins = 0);
* disable tiled raster layer exports: checked.

# Inkscape preparation
Fix Page Properties to correct page size (A3 or A2)
Delete empty groups // Choose Extensions --> History Atlas --> Delete empty groups.
Delete unused layers.
Delete "Map 1: world-ocean-names".
Click "Map 1: Frame" (topmost layer) and check X/Y origin. Select all objects and move them by these values so that topmost layer has X/Y origin = 0.
Set world-shaded-relief to "Multiply".
Go into non-label layers and set the last group (which is bounding rectangle) on top. Select all groups in a layer and set clip (Ctrl+M) // Choose Extensions --> History Atlas --> Clip Layers to Rectangles
Self-clip bordered areas. // Choose Extensions --> History Atlas --> Selfclip Children
Add/edit elements not supported well by QGIS:
* patterned fills;
* arrows;
* multiline flyouts.
Apply 0.3 mm white stroke and "Markers, Stroke, Fill" order to all non-geographic labels. // Choose Extensions --> History Atlas --> Set Text Buffer (Stroke)
Copy and adapt border with geographic coordinates. Width is always 6 mm, with inner 1 mm for black-white pattern.
Copy and adapt legend.