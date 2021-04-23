import bpy

# Index of control edited in 'Manage' panel
ed_ctrl_idx = None


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


class AddPatternGroup(bpy.types.Operator):
    bl_idname = 'control_center.add_pattern_group'
    bl_label = 'Add Pattern Group'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.ctrls[ed_ctrl_idx].pgroups.add()
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
