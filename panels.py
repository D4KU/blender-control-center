import bpy
from . import ops


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
        if ops.ed_ctrl_idx is None:
            return

        # Name & Type
        lyt = self.layout
        ctrl = context.scene.ctrls[ops.ed_ctrl_idx]
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
