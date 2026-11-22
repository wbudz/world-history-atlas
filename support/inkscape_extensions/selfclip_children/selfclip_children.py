#!/usr/bin/env python3
"""Clip every immediate child of the selected layer(s) by a copy of itself."""
import inkex


class SelfClipChildren(inkex.EffectExtension):
    def effect(self):
        parents = [el for el in self.svg.selection
                   if isinstance(el, inkex.Group)]
        if not parents:
            # Nothing selected as an object: fall back to the current layer
            # (the one highlighted in the Layers dialog).
            layer = self.svg.get_current_layer()
            if isinstance(layer, inkex.Group):
                parents = [layer]
        if not parents:
            raise inkex.AbortExtension("Select a layer (or a group) first.")

        defs = self.svg.defs
        for parent in parents:
            children = [c for c in parent if isinstance(c, inkex.ShapeElement)]
            for child in children:
                self.clip_by_copy(child, defs)

    def clip_by_copy(self, child, defs):
        # Inkscape-style: if the child already has a clip, wrap it first so
        # the existing clip is kept and the new one applies on top.
        target = child
        if child.get("clip-path"):
            wrapper = inkex.Group()
            child.addprevious(wrapper)
            wrapper.append(child)
            target = wrapper

        # Duplicate, placed directly below the original in the same parent
        # (the copy is then moved into the clipPath, as "Set Clip" does).
        copy = child.copy()
        child.addprevious(copy)
        for el in copy.descendants():
            if el.get("id") is not None:
                el.set_random_id(el.TAG)
        copy.set_random_id(copy.TAG)

        # A clipPath lives in the user space of the clipped element, which
        # already includes the element's own transform. When the target is
        # the element itself, the copy must therefore drop that transform.
        if target is child:
            copy.pop("transform", None)

        clip = inkex.ClipPath()
        clip.set("clipPathUnits", "userSpaceOnUse")
        defs.append(clip)
        clip.append(copy)
        target.set("clip-path", "url(#{})".format(clip.get_id()))


if __name__ == "__main__":
    SelfClipChildren().run()
