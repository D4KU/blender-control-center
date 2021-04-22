from collections import deque, defaultdict
import re
import bpy


# Index of control edited in 'Manage' panel
ed_ctrl_idx = None


def _hide_collection(col, hide):
    col.hide_viewport = hide
def _hide_object(ob, hide):
    ob.hide_set(hide)


def update_targets(self, context):
    vl = context.view_layer
    if self.trgt == 'OBJ':
        targets = vl.objects
        hide_func = _hide_object
        refattr = 'ob_ref'
    else:
        targets = vl.layer_collection.children
        hide_func = _hide_collection
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
                hide_func(getattr(p, refattr), hide)
        else:
            for t in targets:
                for p in g.patterns:
                    if re.fullmatch(p.name, t.name):
                        hide_func(t, hide)
                        break


def update_targets_as_pattern(self, context):
    update_targets(context.scene.ctrls[ed_ctrl_idx], context)


def get_enum(self, context):
    return [(str(i), g.name, "") for i, g in enumerate(self.pgroups)]


class Pattern(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    # invert: bpy.props.BoolProperty(update=update_targets_as_pattern)
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
        items=get_enum,
        update=update_targets,
    )
    trgt: bpy.props.EnumProperty(
        name="Target",
        items=(
            ('OBJ', "Objects"    , ""),
            ('COL', "Collections", ""),
        )
    )


class VIEW3D_PT_ControlCenter_Use(bpy.types.Panel):
    bl_label = "Use"
    bl_category = "Control Center"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        split = self.layout.split(factor=.85)
        col1 = split.column()
        col2 = split.column()
        for i, c in enumerate(context.scene.ctrls):
            if c.type == 'INT':
                propstr = "ival"
            elif c.type == 'ENUM':
                propstr = "dval"
            else:
                propstr = "bval"

            col1.prop(c, propstr, text=c.name)
            op = col2.operator(
                "control_center.edit_control",
                text="",
                icon='THREE_DOTS',
                )
            op.ctrl_idx = i
        col2.operator("control_center.add_control", text="", icon='ADD')


class VIEW3D_PT_ControlCenter_Manage(bpy.types.Panel):
    bl_label = "Manage"
    bl_category = "Control Center"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        if ed_ctrl_idx is None:
            return

        # Name & Type
        lyt = self.layout
        ctrl = context.scene.ctrls[ed_ctrl_idx]
        refattr = 'ob_ref' if ctrl.trgt == 'OBJ' else 'col_ref'
        lyt.prop(ctrl, "name")
        lyt.prop(ctrl, "type")
        lyt.prop(ctrl, "trgt")

        # Pattern Groups
        for i in range(len(ctrl.pgroups)):
            group = ctrl.pgroups[i]
            pattr = "name" if group.matchby == 'NAME' else refattr

            gbox = lyt.box()
            if ctrl.type == 'BOOL':
                active = ctrl.bval == bool(i)
            elif ctrl.type == 'INT':
                active = ctrl.ival == i
            else:
                active = ctrl.dval == str(i)

            psplit = gbox.split(factor=.85)
            pcol1 = psplit.column()
            pcol2 = psplit.column()
            gbox.prop(group, "name")
            gbox.prop(group, "matchby")

            pbox = gbox.box()
            psplit = pbox.split(factor=.85)
            pcol1 = psplit.column()
            pcol2 = psplit.column()
            pcol1.alert = active
            pcol1.label(text="Patterns")
            pcol1.alert = False
            op = pcol2.operator(
                "control_center.add_pattern",
                text="",
                icon='ADD',
            )
            op.group_idx = i

            for j, p in enumerate(group.patterns):
                pcol1.prop(p, pattr, icon_only=True, text=str(j))
                op = pcol2.operator(
                    "control_center.del_pattern",
                    text="",
                    icon='REMOVE',
                )
                op.group_idx = i
                op.pat_idx = j
            op = gbox.operator(
                "control_center.del_pattern_group",
                icon='REMOVE',
                )
            op.group_idx = i

        lyt.operator(
            "control_center.add_pattern_group",
            icon='ADD',
            )

        row = lyt.row()
        row.operator("control_center.del_control")
        row.operator("control_center.close_manage")


class AddControl(bpy.types.Operator):
    bl_idname = 'control_center.add_control'
    bl_label = 'Add Control'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.ctrls.add()
        return {"FINISHED"}


class DelControl(bpy.types.Operator):
    bl_idname = 'control_center.del_control'
    bl_label = 'Delete Control'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global ed_ctrl_idx
        context.scene.ctrls.remove(ed_ctrl_idx)
        ed_ctrl_idx = None
        return {"FINISHED"}


class EditControl(bpy.types.Operator):
    bl_idname = 'control_center.edit_control'
    bl_label = 'Edit Control'
    ctrl_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        global ed_ctrl_idx
        ed_ctrl_idx = self.ctrl_idx
        return {"FINISHED"}


def add_pattern_group(context):
    context.scene.ctrls[ed_ctrl_idx].pgroups.add()


class AddPatternGroup(bpy.types.Operator):
    bl_idname = 'control_center.add_pattern_group'
    bl_label = 'Add Pattern Group'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        add_pattern_group(context)
        return {"FINISHED"}


class DelPatternGroup(bpy.types.Operator):
    bl_idname = 'control_center.del_pattern_group'
    bl_label = 'Delete Pattern Group'
    bl_options = {"REGISTER", "UNDO"}
    group_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        ctrl = context.scene.ctrls[ed_ctrl_idx]
        ctrl.pgroups.remove(self.group_idx)
        return {"FINISHED"}


class AddPattern(bpy.types.Operator):
    bl_idname = 'control_center.add_pattern'
    bl_label = 'Add Pattern'
    bl_options = {"REGISTER", "UNDO"}
    group_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        ctrl = context.scene.ctrls[ed_ctrl_idx]
        ctrl.pgroups[self.group_idx].patterns.add()
        return {"FINISHED"}


class DelPattern(bpy.types.Operator):
    bl_idname = 'control_center.del_pattern'
    bl_label = 'Add Pattern'
    bl_options = {"REGISTER", "UNDO"}
    group_idx: bpy.props.IntProperty(options={'HIDDEN'})
    pat_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        ctrl = context.scene.ctrls[ed_ctrl_idx]
        ctrl.pgroups[self.group_idx].patterns.remove(self.pat_idx)
        return {"FINISHED"}


class CloseManagePanel(bpy.types.Operator):
    bl_idname = 'control_center.close_manage'
    bl_label = 'Close'

    def execute(self, context):
        global ed_ctrl_idx
        ed_ctrl_idx = None
        return {"FINISHED"}
