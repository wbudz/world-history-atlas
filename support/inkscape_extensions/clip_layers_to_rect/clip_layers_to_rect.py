#!/usr/bin/env python3
"""Clip every group in a layer to the single rectangle held by the layer's last group.

For each layer (inkscape:groupmode="layer"):
  1. The clip group = the first or last child <g> of the layer that contains
     exactly one element which is a <rect>.
  2. The clip group is moved to the top of the layer (last in document order).
  3. Every other child group of the layer is clipped to the rectangle,
     like Object > Clip > Set Clip, and the clip group is consumed.

Tested against the Inkscape 1.2+ inkex API.
"""
import inkex
from inkex import ClipPath, Group, Rectangle


def is_layer(el):
    return el.get("inkscape:groupmode") == "layer"


class ClipLayersToRect(inkex.EffectExtension):
    def add_arguments(self, pars):
        pars.add_argument(
            "--wrap",
            type=inkex.Boolean,
            default=False,
            help="Wrap all groups in one group and clip that, instead of "
            "clipping each group separately",
        )

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def child_groups(layer):
        return [c for c in layer if isinstance(c, Group) and not is_layer(c)]

    @staticmethod
    def clip_rect_of(group):
        """Return the rectangle if `group` holds exactly one element and it is a rect."""
        kids = [c for c in group if isinstance(c, inkex.BaseElement)]
        if len(kids) == 1 and isinstance(kids[0], Rectangle):
            return kids[0]
        return None

    def make_clip(self, rect, tf):
        """Create a <clipPath> in defs containing a copy of `rect` with transform `tf`."""
        clip = ClipPath()
        clip.set("clipPathUnits", "userSpaceOnUse")
        self.svg.defs.append(clip)
        clip.get_id()  # assigns a unique id

        r = rect.copy()
        if "id" in r.attrib:
            del r.attrib["id"]
        r.transform = tf
        clip.append(r)
        r.get_id()
        return clip

    def apply_clip(self, target, clip_group, rect):
        # The clipPath is interpreted in the *target's* local coordinate system
        # (i.e. after the target's own transform), so express the rectangle's
        # position, given in layer coordinates, relative to the target.
        tf = (-target.transform) @ clip_group.transform @ rect.transform
        clip = self.make_clip(rect, tf)
        target.set("clip-path", f"url(#{clip.get_id()})")

    # ------------------------------------------------------------------- effect
    def effect(self):
        layers = self.svg.xpath('//svg:g[@inkscape:groupmode="layer"]')
        done = 0

        for layer in layers:
            groups = self.child_groups(layer)
            if len(groups) < 2:
                continue

            # The clip group (a group holding a single rectangle) may sit at
            # either end of the layer: Inkscape's Objects panel lists the
            # topmost object first, so the "last" item there is the FIRST
            # group in the XML (bottom of the z-order).
            clip_group = None
            for candidate in (groups[0], groups[-1]):
                if self.clip_rect_of(candidate) is not None:
                    clip_group = candidate
                    break
            if clip_group is None:
                continue  # not a layer of the expected shape
            rect = self.clip_rect_of(clip_group)

            # Step 2: make sure the clip group is the topmost one
            layer.remove(clip_group)
            layer.append(clip_group)

            targets = [g for g in groups if g is not clip_group]

            if self.options.wrap:
                wrapper = Group()
                wrapper.set("inkscape:label", "clipped")
                layer.insert(layer.index(targets[0]), wrapper)
                for t in targets:
                    wrapper.append(t)  # re-parents, keeps z-order
                targets = [wrapper]

            # Step 3: clip
            for t in targets:
                if t.get("clip-path"):
                    # already clipped: nest it so the old clip is preserved
                    wrapper = Group()
                    layer.insert(layer.index(t), wrapper)
                    wrapper.append(t)
                    t = wrapper
                self.apply_clip(t, clip_group, rect)

            # "Set Clip" consumes the clipping object
            layer.remove(clip_group)
            done += 1

        if done == 0:
            inkex.errormsg(
                "No suitable layers found. A layer needs at least two groups, "
                "with the first or last group containing exactly one rectangle."
            )


if __name__ == "__main__":
    ClipLayersToRect().run()
