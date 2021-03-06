import bpy
from . import ops


# Panel showing all created controls
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
            col1.prop(c, c.propstr, text=c.name)
            op = col2.operator(
                "control_center.edit_control",
                text="",
                icon='THREE_DOTS',
                )
            op.ctrl_idx = i
        col1.operator("control_center.export_json")
        col2.operator("control_center.add_control", text="", icon='ADD')


# Panel to change a specific control
class VIEW3D_PT_ControlCenter_Manage(bpy.types.Panel):
    bl_label = "Manage"
    bl_category = "Control Center"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        if ops.ed_ctrl_idx is None:
            return

        # Per control settings
        lyt = self.layout
        ctrl = context.scene.ctrls[ops.ed_ctrl_idx]
        refattr = ctrl.refpropstr
        lyt.prop(ctrl, "name")
        lyt.prop(ctrl, "type")
        lyt.prop(ctrl, "action")

        # Draw the control's states
        for i, s in enumerate(ctrl.states):
            pattr = "name" if s.matchby == 'NAME' else refattr

            # Per state settings
            sbox = lyt.box()
            sbox.prop(s, "name")
            sbox.prop(s, "matchby")

            # Pattern box heading
            pbox = sbox.box()
            split = pbox.split(factor=.85)
            col1 = split.column()
            col2 = split.column()
            col1.alert = ctrl.index == i
            col1.label(text="Patterns")
            col1.alert = False
            col2.operator(
                "control_center.add_pattern",
                text="",
                icon='ADD',
            ).state_idx = i

            # Draw the state's patterns
            for j, p in enumerate(s.patterns):
                col1.prop(p, pattr, icon_only=True, text=str(j))
                op = col2.operator(
                    "control_center.del_pattern",
                    text="",
                    icon='REMOVE',
                )
                op.state_idx = i
                op.pat_idx = j
            sbox.operator(
                "control_center.del_state",
                icon='REMOVE',
                ).state_idx = i

        # Control's operators
        lyt.operator("control_center.add_state", icon='ADD')
        row = lyt.row()
        row.operator("control_center.del_control")
        row.operator("control_center.close_manage")
