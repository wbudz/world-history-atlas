#!/usr/bin/env python3
"""Inkscape extension: delete empty groups (recursively).

A group is considered empty if it has no child elements, or if all of its
children are themselves empty groups. Comments and whitespace are ignored.
Groups containing anything else (shapes, text, <title>, <desc>, <use>, ...)
are kept.

Compatible with Inkscape 1.x (inkex API).
"""

import inkex


class DeleteEmptyGroups(inkex.EffectExtension):

    def add_arguments(self, pars):
        pars.add_argument(
            "--include_layers",
            type=inkex.Boolean,
            default=False,
            help="Also delete empty layers",
        )

    def effect(self):
        self.include_layers = self.options.include_layers
        removed = self.prune(self.svg)

        if removed == 0:
            self.msg("No empty groups found.")
        elif removed == 1:
            self.msg("Deleted 1 empty group.")
        else:
            self.msg(f"Deleted {removed} empty groups.")

    def prune(self, parent):
        """Remove empty groups below `parent`, depth-first.

        Children are cleaned before their parent is examined, so a group that
        only contained empty groups becomes empty itself and is removed in the
        same pass. Returns the number of groups removed.
        """
        removed = 0

        for child in list(parent):
            # Skip comments and processing instructions
            if not isinstance(child.tag, str):
                continue
            if not isinstance(child, inkex.Group):
                continue

            removed += self.prune(child)

            if self.is_empty(child) and self.may_delete(child):
                parent.remove(child)
                removed += 1

        return removed

    @staticmethod
    def is_empty(group):
        # Only real elements count as content; comments/PIs are ignored.
        return not any(isinstance(c.tag, str) for c in group)

    def may_delete(self, group):
        if self.include_layers:
            return True
        return group.get("inkscape:groupmode") != "layer"


if __name__ == "__main__":
    DeleteEmptyGroups().run()
