import bpy
import re
from . import ops


# Update targets referenced by the passed control in accordance to its
# index
def update_targets(self, context):
    vl = context.view_layer
    if self.trgt == 'OBJ':
        targets = vl.objects
        refattr = 'ob_ref'

        def hide_func(ob, hide):
            ob.hide_set(hide)
    else:
        targets = vl.layer_collection.children
        refattr = 'col_ref'

        def hide_func(col, hide):
            col.hide_viewport = hide

    for i, s in enumerate(self.states):
        # Hide targets matched by all inactive states and show all
        # targets matched by the active state
        hide = i != self.index
        if s.matchby == 'REF':
            # Targets are matched by reference
            # Update all objects/collections referenced by each pattern
            # of the state
            for p in s.patterns:
                ref = getattr(p, refattr)
                try:
                    hide_func(ref, hide)
                except (AttributeError, RuntimeError):
                    # AttributeError thrown when no object referenced
                    # RuntimeError thrown when object outside view
                    # layer referenced
                    pass
        else:
            # Targets are matched by name
            # Iterate over all objects/collections in the view layer
            for t in targets:
                # Update a target if at least one pattern of the state
                # matches its name
                for p in s.patterns:
                    if re.fullmatch(p.name, t.name):
                        hide_func(t, hide)
                        break


def update_targets_from_pattern(self, context):
    ctrl = context.scene.ctrls[ops.ed_ctrl_idx]
    update_targets(ctrl, context)


def update_type(self, context):
    # Get the index via the old type's property and set it again,
    # to that no invalid states can be reached on type change.
    # For example, an enumeration with index 3 would be converted to
    # a bool with index 1 (True).
    set_index(self, getattr(self, self.propstr))
    # Set target visible in accordance with new index
    # update_targets(self, context)


def set_index(self, value):
    self.index = int(value)


# A Pattern is either a regular expression matching a target's name or a
# direct reference
class Pattern(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="Target name",
        description=(
            "Regular expression matched against target names in the "
            "active view layer"
        ),
        update=update_targets_from_pattern,
    )
    ob_ref: bpy.props.PointerProperty(
        name="Object reference",
        type=bpy.types.Object,
        update=update_targets_from_pattern,
    )
    col_ref: bpy.props.PointerProperty(
        name="Collection reference",
        type=bpy.types.Collection,
        update=update_targets_from_pattern,
    )


# Each state represents a set of targets made visible if "
# the control's index is set equal to the respective "
# state's index in this list"
class State(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    patterns: bpy.props.CollectionProperty(type=Pattern)
    matchby: bpy.props.EnumProperty(
        name="Match by",
        description=(
            "Determines how to establish a connection between the "
            "Control Center and the targets to control"
        ),
        items=(
            ('REF' , "Reference", "Match targets by reference"),
            ('NAME', "Name"     , "Match targets by name"),
        )
    )


# An input of arbitrary type to control the visibility of referenced
# objects or collections
class Control(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        description=(
            "Determines the type of stored value and menu this control "
            "represents"
        ),
        items=(
            ('BOOL', "Boolean"    , "This control is a checkbox"),
            ('INT' , "Integer"    , "This control is a slider"),
            ('ENUM', "Enumeration", "This control is a dropdown"),
        ),
        update=update_type,
    )
    name: bpy.props.StringProperty(name="Name")
    states: bpy.props.CollectionProperty(type=State)
    trgt: bpy.props.EnumProperty(
        name="Target",
        description="Determines which type of target patterns match",
        items=(
            ('OBJ', "Objects"    , "Control visibility of objects"),
            ('COL', "Collections", "Control visibility of collections"),
        )
    )
    index: bpy.props.IntProperty(
        description="The index of the active state",
        update=update_targets,
    )
    # The actual properties drawn depending of the control's type
    pBOOL: bpy.props.BoolProperty(
        get=lambda self: bool(self.index),
        set=set_index,
    )
    pINT: bpy.props.IntProperty(
        get=lambda self: self.index,
        set=set_index,
    )
    pENUM: bpy.props.EnumProperty(
        name="",
        items=lambda self, _:
            [(str(i), s.name, "") for i, s in enumerate(self.states)],
        get=lambda self: self.index,
        set=set_index,
    )

    @property
    def propstr(self):
        return 'p' + str(self.type)
