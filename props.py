import bpy
import re


def update_targets(self, context):
    vl = context.view_layer
    if self.trgt == 'OBJ':
        def hide_func(ob, hide):
            ob.hide_set(hide)

        targets = vl.objects
        refattr = 'ob_ref'
    else:
        def hide_func(col, hide):
            col.hide_viewport = hide

        targets = vl.layer_collection.children
        refattr = 'col_ref'

    for i, s in enumerate(self.states):
        hide = i != self.index
        if s.matchby == 'REF':
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
            for t in targets:
                for p in s.patterns:
                    if re.fullmatch(p.name, t.name):
                        hide_func(t, hide)
                        break


def update_type(self, context):
    set_index(self, getattr(self, self.propstr))
    update_targets(self, context)


def set_index(self, value):
    self.index = int(value)


class Pattern(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    ob_ref: bpy.props.PointerProperty(type=bpy.types.Object)
    col_ref: bpy.props.PointerProperty(type=bpy.types.Collection)


class State(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    patterns: bpy.props.CollectionProperty(type=Pattern)
    matchby: bpy.props.EnumProperty(
        name="Match by",
        items=(
            ('REF' , "Reference", ""),
            ('NAME', "Name"     , ""),
        )
    )


class Control(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        items=(
            ('BOOL', "Boolean"    , ""),
            ('INT' , "Integer"    , ""),
            ('ENUM', "Enumeration", ""),
        ),
        update=update_type,
    )
    states: bpy.props.CollectionProperty(type=State)
    name: bpy.props.StringProperty(name="Name")
    trgt: bpy.props.EnumProperty(
        name="Target",
        items=(
            ('OBJ', "Objects"    , ""),
            ('COL', "Collections", ""),
        )
    )
    index: bpy.props.IntProperty(
        update=update_targets,
    )
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
