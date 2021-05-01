import bpy
import re
from . import ops


def hide_hierarchy(root, hide, ctrls):
    stack = [root]
    while stack:
        o = stack.pop()
        if hide:
            o.hide_set(True)
        else:
            o.hide_set(is_ob_in_inactive_state(o, ctrls))
        stack.extend(o.children)


def get_lvl(ob):
    lvl = -1
    while ob:
        ob = ob.parent
        lvl += 1
    return lvl


def update_targets(self, context):
    vl = context.view_layer
    matchs = []

    def func(*args):
        matchs.append(args)

    # fill matchs
    map_to_targets(self, vl.objects, func)
    matchs.sort(key=lambda x: get_lvl(x[0]))

    for ob, state_idx in matchs:
        hide_self = state_idx != self.index
        hide_in_hierarchy = ob.parent.hide_get(view_layer=vl) \
            if ob.parent else False
        ctrls = list(context.scene.ctrls)
        ctrls.remove(self)
        hide_hierarchy(
            ob,
            hide_self or hide_in_hierarchy,
            ctrls,
        )


def is_ob_in_inactive_state(ob, ctrls):
    for c in ctrls:
        for i, s in enumerate(c.states):
            state_inactive = c.index != i
            for p in s.patterns:
                if s.matchby == 'REF':
                    if p.ob_ref is ob:
                        return state_inactive
                else:
                    if re.fullmatch(p.name, ob.name):
                        return state_inactive
    return False


# Update targets referenced by the passed control in accordance to its
# index
def update_targets2(self, context):
    vl = context.view_layer
    if self.trgt == 'OBJ':
        targets = vl.objects

        def hide_func(ob, i):
            hide = i != self.index
            ob.hide_set(hide)
    else:
        targets = vl.layer_collection.children

        def hide_func(col, i):
            hide = i != self.index
            col.hide_viewport = hide

    map_to_targets(self, targets, hide_func)


def map_to_targets(ctrl, targets, func):
    refattr = ctrl.refpropstr

    # Make sure active state is processed last
    states = [(i, s) for i, s in enumerate(ctrl.states) if i != ctrl.index]
    if not states:
        return
    states.append((ctrl.index, ctrl.states[ctrl.index]))

    for i, s in states:
        # Hide targets matched by all inactive states and show all
        # targets matched by the active state
        if s.matchby == 'REF':
            # Targets are matched by reference
            # Update all objects/collections referenced by each pattern
            # of the state
            for p in s.patterns:
                ref = getattr(p, refattr)
                if not ref:
                    continue
                try:
                    func(ref, i)
                except RuntimeError:
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
                        func(t, i)
                        break


def update_targets_from_pattern(self, context):
    ctrl = context.scene.ctrls[ops.ed_ctrl_idx]
    update_targets(ctrl, context)


def update_type(self, context):
    # Get the index via the old type's property and set it again,
    # to that no invalid states can be reached on type change.
    # For example, an enumeration with index 3 would be converted to
    # a bool with index 1 (True).
    if self.states:
        set_index(self, getattr(self, self.propstr))


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

    @property
    def refpropstr(self):
        return 'ob_ref' if self.trgt else 'col_ref'
