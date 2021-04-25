import bpy
from . import export

# Index of control edited in 'Manage' panel
ed_ctrl_idx = None


class AddControl(bpy.types.Operator):
    bl_idname = 'control_center.add_control'
    bl_label = 'Add Control'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new control the Control Center"

    def execute(self, context):
        context.scene.ctrls.add()
        return {"FINISHED"}


class DelControl(bpy.types.Operator):
    bl_idname = 'control_center.del_control'
    bl_label = 'Delete Control'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove this control from the Control Center"

    def execute(self, context):
        global ed_ctrl_idx
        context.scene.ctrls.remove(ed_ctrl_idx)
        ed_ctrl_idx = None
        return {"FINISHED"}


class EditControl(bpy.types.Operator):
    bl_idname = 'control_center.edit_control'
    bl_label = 'Edit Control'
    ctrl_idx: bpy.props.IntProperty(options={'HIDDEN'})
    bl_description = "Edit this control in the 'Manage' panel"

    def execute(self, context):
        global ed_ctrl_idx
        ed_ctrl_idx = self.ctrl_idx
        return {"FINISHED"}


class AddState(bpy.types.Operator):
    bl_idname = 'control_center.add_state'
    bl_label = 'Add State'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Add a new state to the control. It can comprise several "
        "patterns activated if the control is set to that state"
    )

    def execute(self, context):
        context.scene.ctrls[ed_ctrl_idx].states.add()
        return {"FINISHED"}


class DelState(bpy.types.Operator):
    bl_idname = 'control_center.del_state'
    bl_label = 'Delete State'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove this state from the control"
    state_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        ctrl = context.scene.ctrls[ed_ctrl_idx]
        ctrl.states.remove(self.state_idx)
        return {"FINISHED"}


class AddPattern(bpy.types.Operator):
    bl_idname = 'control_center.add_pattern'
    bl_label = 'Add Pattern'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Add a pattern to the state. A pattern matches one or more "
        "targets hidden when the state is inactive and shown otherwise"
    )
    state_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        ctrl = context.scene.ctrls[ed_ctrl_idx]
        ctrl.states[self.state_idx].patterns.add()
        return {"FINISHED"}


class DelPattern(bpy.types.Operator):
    bl_idname = 'control_center.del_pattern'
    bl_label = 'Add Pattern'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove this pattern from the state"
    state_idx: bpy.props.IntProperty(options={'HIDDEN'})
    pat_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        ctrl = context.scene.ctrls[ed_ctrl_idx]
        ctrl.states[self.state_idx].patterns.remove(self.pat_idx)
        return {"FINISHED"}


class CloseManagePanel(bpy.types.Operator):
    bl_idname = 'control_center.close_manage'
    bl_label = 'Close'
    bl_description = "Close the 'Manage' panel"

    def execute(self, context):
        global ed_ctrl_idx
        ed_ctrl_idx = None
        return {"FINISHED"}


class ExportJson(bpy.types.Operator):
    bl_idname = 'control_center.export_json'
    bl_label = 'Export Json'
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Export the control center setup as Json file"
    filename: bpy.props.StringProperty(
        name="File Name",
        default="export.json",
        description="Relative path from directory in which Blender runs",
    )

    def execute(self, context):
        data = export.serialize_ctrls(context)
        export.write(data, self.filename)
        return {"FINISHED"}
