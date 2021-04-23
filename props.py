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

    if self.type == 'BOOL':
        index = int(self.bval)
    elif self.type == 'INT':
        index = self.ival
    else:
        index = int(self.eval)

    for i, g in enumerate(self.pgroups):
        hide = i == index
        if g.matchby == 'REF':
            for p in g.patterns:
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
                for p in g.patterns:
                    if re.fullmatch(p.name, t.name):
                        hide_func(t, hide)
                        break


class Pattern(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    ob_ref: bpy.props.PointerProperty(type=bpy.types.Object)
    col_ref: bpy.props.PointerProperty(type=bpy.types.Collection)


class PatternGroup(bpy.types.PropertyGroup):
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
    )
    pgroups: bpy.props.CollectionProperty(type=PatternGroup)
    name: bpy.props.StringProperty(name="Name")
    bval: bpy.props.BoolProperty(
        update=update_targets,
    )
    ival: bpy.props.IntProperty(
        update=update_targets,
    )
    dval: bpy.props.EnumProperty(
        name="",
        items=lambda self, _:
            [(str(i), g.name, "") for i, g in enumerate(self.pgroups)],
        update=update_targets,
    )
    trgt: bpy.props.EnumProperty(
        name="Target",
        items=(
            ('OBJ', "Objects"    , ""),
            ('COL', "Collections", ""),
        )
    )
