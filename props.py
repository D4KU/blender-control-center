import bpy
import re
from . import ops


# Call a function on each recursive child of passed root object
def map_to_hierarchy(root, func):
    stack = [root]
    while stack:
        o = stack.pop()
        func(o)
        stack.extend(o.children)


# Get a passed object's deepness in the hierarchy
def get_lvl(ob):
    lvl = -1
    while ob:
        ob = ob.parent
        lvl += 1
    return lvl


def _hide_ob(ob, hide):
    ob.hide_set(hide)


def _unsel_ob(ob, unsel):
    ob.select_set(not unsel)


# Update targets matched by the given control
def update_targets(ctrl, context):
    vl = context.view_layer

    if ctrl.action == 'OBJV':
        action = _hide_ob
    elif ctrl.action == 'OBJS':
        action = _unsel_ob
    else:
        def hide_col(col, state_idx):
            col.hide_viewport = state_idx != ctrl.index
        map_to_targets(ctrl, vl.layer_collection.children, hide_col)
        return

    # If the targets are objects, we are interested in a behavior
    # where a parent hides all its children, even if one of those
    # children is not hidden itself

    # Find all matches and sort them according to their deepness in the
    # scene hierarchy. The sorting ensures that children can test their
    # parents to see weather they need to stay hidden, even though they
    # themselves are set visible
    matches = []
    map_to_targets(ctrl, vl.objects, lambda *a: matches.append(a))
    matches.sort(key=lambda x: get_lvl(x[0]))

    def pass_action_true(ob):
        action(ob, True)

    for ob, state_idx in matches:
        hide_self = state_idx != ctrl.index
        hide_in_hierarchy = ob.parent.hide_get(view_layer=vl) \
            if ob.parent else False

        if hide_self or hide_in_hierarchy:
            # Object is hidden anyway, no further checks required
            func = pass_action_true
        else:
            # Prepare list of every control except passed one
            ctrls = list(context.scene.ctrls)
            ctrls.remove(ctrl)

            # Object could be visible. But to let it be, it must be
            # checked whether this object is matched by any other
            # inactive state. If so, it stays hidden.
            def func(ob):
                action(ob, is_ob_in_inactive_state(ob, ctrls))

        map_to_hierarchy(ob, func)


# Returns True if the passed object is matched by any inactive state
# in any of the passed controls
def is_ob_in_inactive_state(ob, ctrls):
    for c in ctrls:
        for i, s in enumerate(c.states):
            if c.index == i:
                # Not interested in active states
                continue
            if s.matchby == 'REF':
                for p in s.patterns:
                    if p.ob_ref is ob:
                        return True
            else:
                for p in s.patterns:
                    if re.fullmatch(p.name, ob.name):
                        return True
    return False


# Update targets referenced by the passed control in accordance to its
# index without the behaviour that objects hide their children
def update_targets_simple(self, context):
    vl = context.view_layer
    if self.action == 'OBJV':
        targets = vl.objects

        def func(ob, i):
            ob.hide_set(i != self.index)
    elif self.action == 'OBJS':
        targets = vl.objects

        def func(ob, i):
            ob.select_set(i != self.index)
    else:
        targets = vl.layer_collection.children

        def func(col, i):
            col.hide_viewport = i != self.index

    map_to_targets(self, targets, func)


# On every target in 'targets', matched by passed control, call passed
# function
def map_to_targets(ctrl, targets, func):
    refattr = ctrl.refpropstr
    if not ctrl.states:
        return

    # Make sure active state is processed last
    # This is important for controls where a target is matched
    # by an active and inactive state. An inactive state must not
    # override an active one.
    states = [x for x in enumerate(ctrl.states) if x[0] != ctrl.index]
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


def update_targets_from_pattern(_, context):
    ctrl = context.scene.ctrls[ops.ed_ctrl_idx]
    update_targets(ctrl, context)


def update_type(ctrl, context):
    # Get the index via the old type's property and set it again,
    # to that no invalid states can be reached on type change.
    # For example, an enumeration with index 3 would be converted to
    # a bool with index 1 (True).
    if ctrl.states:
        set_index(ctrl, getattr(ctrl, ctrl.propstr))


def set_index(ctrl, value):
    ctrl.index = max(0, min(int(value), len(ctrl.states) - 1))


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
    action: bpy.props.EnumProperty(
        name="Target",
        description="Determines which type of target patterns match",
        items=(
            ('OBJV', "Object Visibility"    , "Control visibility of objects"),
            ('OBJS', "Object Selection"     , "Control selection of objects"),
            ('COL' , "Collection Visibility", "Control visibility of collections"),
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
        min=0,
        max=15,
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
        return 'col_ref' if self.action == 'COL' else 'ob_ref'
