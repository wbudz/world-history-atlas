#!/usr/bin/env python3
"""
Fit Frame to Text
-----------------
Select a rectangle and a (flowed) text object together, run this extension,
and the rectangle is resized/repositioned to hug the text's actual rendered
bounding box plus a margin you choose. The text is also centered horizontally
(via paragraph alignment) and vertically (by measuring the real post-resize
layout and nudging the text into place — see note below).

Why this needs a subprocess call:
Inkscape's internal Python geometry (bounding_box()) does not compute real
font metrics, so it cannot report an accurate box for text. The reliable way
to get the true rendered bounding box is to ask Inkscape itself, via its own
command line query flags, which is what query_bbox() below does.

Why vertical centering needs a SECOND query, mid-script:
Flowed/shape-inside text is always anchored flush to the top of its region,
with only a small, fixed, font-driven gap above the first line — any extra
room in the frame is left entirely below the text, never split evenly, no
matter how the frame is sized. So after resizing the rectangle, we write the
in-progress document to a temp file, ask Inkscape where the text *actually*
landed in the new frame, and nudge the whole text object down by however
much is needed to make the leftover space equal top and bottom. Nudging via
a transform on the text element is safe here: per standard SVG semantics, an
element's own transform is a pure rigid transform applied after its content
is laid out, so it doesn't affect how the shape-inside wrapping itself is
computed.

Known limitations:
- Assumes the rectangle and text are not inside a rotated or non-uniformly
  scaled group. A plain translation on the layer/group is handled; rotation
  or skew is not.
- Expects exactly one <rect> and one text element (either modern
  shape-inside flowed text, or a legacy <flowRoot>) in the selection.
- If resizing the frame's width changes how the text wraps (rare, only
  happens if the original frame was much wider than the longest line), the
  vertical centering measurement still uses the true post-resize layout, so
  it stays correct even then — only the very first (pre-resize) query could
  be thrown off by a rewrap, and that only feeds into the target size, not
  the final centering.
"""

import os
import tempfile

import inkex
from inkex.command import inkscape
from inkex.transforms import Transform


class FitFrameToText(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument("--margin", type=float, default=5.0)
        pars.add_argument("--unit", type=str, default="mm")

    def effect(self):
        selected = list(self.svg.selection)
        if len(selected) != 2:
            raise inkex.AbortExtension(
                "Select exactly one rectangle and one text object, then run this again."
            )

        rect_elem = None
        text_elem = None
        for elem in selected:
            tag = elem.TAG  # e.g. 'rect', 'text', 'flowRoot'
            if tag == 'rect' and rect_elem is None:
                rect_elem = elem
            elif tag in ('text', 'flowRoot') and text_elem is None:
                text_elem = elem

        if rect_elem is None or text_elem is None:
            raise inkex.AbortExtension(
                "Couldn't find one rectangle and one text object in the selection. "
                "Legacy flowRoot elements and modern shape-inside text both work, "
                "but paths converted from text do not (they lose the ability to reflow)."
            )

        # Horizontal centering: fitting the frame to the widest line only
        # matches the block's overall width to that line — it doesn't center
        # every shorter line within it. This is the same property Inkscape's
        # own center-align button sets.
        text_elem.style['text-align'] = 'center'

        # --- Pass 1: size the frame to the text + margin (as before) -------
        margin_uu = self.svg.unittouu(f"{self.options.margin}{self.options.unit}")

        tx, ty, tw, th = self.query_bbox(text_elem.get_id(), self.options.input_file)
        tx, ty, tw, th = (self.svg.unittouu(f"{v}px") for v in (tx, ty, tw, th))

        # Corners of the desired frame, in the root document's user-unit
        # space (i.e. as if the rect had no ancestor transform).
        x0, y0 = tx - margin_uu, ty - margin_uu
        x1, y1 = tx + tw + margin_uu, ty + th + margin_uu

        rect_parent = rect_elem.getparent()
        rect_inv = -rect_parent.composed_transform() if rect_parent is not None else Transform()
        rx0, ry0 = rect_inv.apply_to_point((x0, y0))
        rx1, ry1 = rect_inv.apply_to_point((x1, y1))

        new_x, new_y = min(rx0, rx1), min(ry0, ry1)
        new_w, new_h = abs(rx1 - rx0), abs(ry1 - ry0)

        if new_w <= 0 or new_h <= 0:
            raise inkex.AbortExtension(
                f"Computed a zero/negative size ({new_w:.3g} x {new_h:.3g}) — "
                "aborting instead of hiding your objects. This usually means "
                "the rectangle sits inside a rotated or skewed group."
            )

        rect_elem.set('x', str(new_x))
        rect_elem.set('y', str(new_y))
        rect_elem.set('width', str(new_w))
        rect_elem.set('height', str(new_h))

        # --- Pass 2: measure the real post-resize layout, then vertically --
        # --- center by nudging the text object -----------------------------
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(suffix='.svg')
            os.close(fd)
            self.document.write(tmp_path)

            tx2, ty2, tw2, th2 = self.query_bbox(text_elem.get_id(), tmp_path)
            tx2, ty2, tw2, th2 = (self.svg.unittouu(f"{v}px") for v in (tx2, ty2, tw2, th2))
        finally:
            if tmp_path is not None:
                os.remove(tmp_path)

        # x0,y0,x1,y1 are still the frame's box in root-space user units.
        target_center_y = (y0 + y1) / 2.0
        actual_center_y = ty2 + th2 / 2.0
        dy_root = target_center_y - actual_center_y

        text_parent = text_elem.getparent()
        text_parent_transform = (
            text_parent.composed_transform() if text_parent is not None else Transform()
        )
        dx_local, dy_local = self.transform_vector(-text_parent_transform, 0.0, dy_root)

        text_elem.transform = Transform(translate=(dx_local, dy_local)) @ text_elem.transform

    @staticmethod
    def transform_vector(transform, dx, dy):
        """Transform a DELTA (not an absolute point) through an affine
        transform, i.e. apply its rotation/scale but ignore its translation."""
        ax, ay = transform.apply_to_point((dx, dy))
        ox, oy = transform.apply_to_point((0.0, 0.0))
        return ax - ox, ay - oy

    def query_bbox(self, element_id, file_path):
        """Ask Inkscape's own renderer for the true bounding box of an
        element in a given SVG file, in document pixels. Returns
        (x, y, width, height)."""
        output = inkscape(
            file_path,
            f"--query-id={element_id}",
            "--query-x", "--query-y", "--query-width", "--query-height",
        )
        try:
            x, y, w, h = (float(v) for v in output.strip().splitlines()[:4])
        except (ValueError, IndexError):
            raise inkex.AbortExtension(
                "Couldn't read the text's bounding box from Inkscape. "
                f"Raw output was: {output!r}"
            )
        return x, y, w, h


if __name__ == '__main__':
    FitFrameToText().run()
