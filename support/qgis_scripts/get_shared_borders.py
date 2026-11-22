from qgis.core import (QgsVectorLayer, QgsField, QgsFeature, QgsGeometry,
                       QgsSpatialIndex, QgsWkbTypes, QgsProject)
from qgis.PyQt.QtCore import QVariant

layer = iface.activeLayer()   # must be a polygon layer
TOL = 0            # map units; set >0 (e.g. 0.5 for metres) if borders don't match exactly
ID_FIELD = "id"    # attribute to copy from each polygon into id_a / id_b

if layer.fields().indexFromName(ID_FIELD) == -1:
    raise ValueError(f"Field '{ID_FIELD}' not found. Available: "
                     f"{[f.name() for f in layer.fields()]}")
id_type = layer.fields().field(ID_FIELD).type()   # keep original data type

out = QgsVectorLayer(f"MultiLineString?crs={layer.crs().authid()}",
                     "shared_borders", "memory")
pr = out.dataProvider()
pr.addAttributes([
    QgsField("fid_a", QVariant.LongLong),
    QgsField("fid_b", QVariant.LongLong),
    QgsField("id_a", id_type),
    QgsField("id_b", id_type),
    QgsField("length", QVariant.Double),
])
out.updateFields()

feats = {f.id(): f for f in layer.getFeatures()}
index = QgsSpatialIndex(layer.getFeatures())

def line_parts(geom):
    if geom is None or geom.isEmpty():
        return []
    return [p for p in geom.asGeometryCollection()
            if QgsWkbTypes.geometryType(p.wkbType()) == QgsWkbTypes.LineGeometry]

new = []
for fid, f in feats.items():
    g1 = f.geometry()
    bbox = g1.boundingBox()
    if TOL > 0:
        bbox.grow(TOL)
    for cid in index.intersects(bbox):
        if cid <= fid:          # each pair only once, skip self
            continue
        fb = feats[cid]
        g2 = fb.geometry()
        if TOL > 0:
            shared = g2.boundary().intersection(g1.boundary().buffer(TOL, 8))
        else:
            if not g1.intersects(g2):
                continue
            shared = g1.intersection(g2)
        parts = line_parts(shared)
        if not parts:
            continue
        merged = QgsGeometry.collectGeometry(parts).mergeLines()
        merged.convertToMultiType()
        nf = QgsFeature(out.fields())
        nf.setGeometry(merged)
        nf.setAttributes([fid, cid, f[ID_FIELD], fb[ID_FIELD], merged.length()])
        new.append(nf)

pr.addFeatures(new)
out.updateExtents()
QgsProject.instance().addMapLayer(out)
print(f"{len(new)} shared borders found")