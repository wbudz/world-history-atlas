#!/usr/bin/env python3
"""Apply a stroke (color, width, paint order) to every text object in the
selected layer / selection, searching recursively through nested groups."""

import math

import inkex
from inkex.units import convert_unit

SVG_NS = "{http://www.w3.org/2000/svg}"
TEXT_TAGS = (SVG_NS + "text", SVG_NS + "flowRoot")
SKIP_TAGS = (SVG_NS + "defs", SVG_NS + "metadata", SVG_NS + "namedview")
STROKE_PROPS = ("stroke", "stroke-width", "stroke-opacity", "paint-order")


def parse_rgba(value):
    """Return (r, g, b, a) from the integer / hex value Inkscape passes."""
    s = str(value).strip()
    if s.startswith("#"):
        s = s[1:]
        n = int(s, 16)
        if len(s) <= 6:
            n = (n << 8) | 0xFF
    elif s.lower().startswith("0x"):
        n = int(s, 16)
    elif s.isdigit():
        n = int(s)
    else:
        n = int(s, 16)
    n &= 0xFFFFFFFF
    return (n >> 24) & 255, (n >> 16) & 255, (n >> 8) & 255, n & 255


def px_per_user_unit(svg):
    """CSS px per one user unit of the document (viewBox scale).

    Computed from the root width/height and viewBox directly, because
    svg.unittouu() does not apply the viewBox scale in recent inkex versions.
    """
    try:
        vb = svg.get_viewbox()
    except Exception:
        vb = None
    if vb and len(vb) == 4:
        for attr, size in (("width", vb[2]), ("height", vb[3])):
            value = svg.get(attr)
            if value and size and "%" not in value:
                try:
                    return convert_unit(value, "px") / size
                except Exception:
                    pass
    return 1.0


def fmt(number):
    return ("%.6f" % number).rstrip("0").rstrip(".") or "0"


class TextStroke(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument("--stroke_color", type=str, default="4294967295")
        pars.add_argument("--stroke_width", type=float, default=0.3)
        pars.add_argument("--unit", type=str, default="mm")
        pars.add_argument("--paint_order", type=str, default="markers stroke fill")
        pars.add_argument("--compensate", type=inkex.Boolean, default=True)

    @staticmethod
    def find_text(element):
        """Yield text objects below (or equal to) element, recursively."""
        tag = element.tag
        if tag in TEXT_TAGS:
            yield element
            return
        if tag in SKIP_TAGS or not isinstance(tag, str):
            return
        for child in element:
            yield from TextStroke.find_text(child)

    def effect(self):
        roots = list(self.svg.selection.values())
        if not roots:
            layer = self.svg.get_current_layer()
            if layer is None or layer is self.svg:
                inkex.errormsg("Select a layer (or objects) first.")
                return
            roots = [layer]

        texts, seen = [], set()
        for root in roots:
            for text in self.find_text(root):
                key = text.get_id()
                if key not in seen:
                    seen.add(key)
                    texts.append(text)

        if not texts:
            inkex.errormsg("No text objects found in the selected layer.")
            return

        r, g, b, a = parse_rgba(self.options.stroke_color)
        color = "#%02x%02x%02x" % (r, g, b)
        opacity = fmt(a / 255.0)
        # Requested width in px, then converted to user units via the viewBox scale.
        width_px = convert_unit("%s%s" % (self.options.stroke_width, self.options.unit), "px")
        width_uu = width_px / px_per_user_unit(self.svg)

        for text in texts:
            width = width_uu
            if self.options.compensate:
                if hasattr(text, "composed_transform"):  # inkex 1.2+
                    t = text.composed_transform()
                else:  # older inkex
                    t = text.composite_transform()
                scale = math.sqrt(abs(t.a * t.d - t.b * t.c))
                if scale > 1e-9:
                    width = width_uu / scale

            style = text.style
            style["stroke"] = color
            style["stroke-opacity"] = opacity
            style["stroke-width"] = fmt(width)
            style["paint-order"] = self.options.paint_order

            # Remove stroke overrides on tspans so the text-level setting wins.
            for child in text.descendants():
                if child is text:
                    continue
                cstyle = child.style
                for prop in STROKE_PROPS:
                    if prop in cstyle:
                        del cstyle[prop]


if __name__ == "__main__":
    TextStroke().run()
