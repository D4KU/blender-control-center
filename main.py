from collections import deque, defaultdict
import re
import bpy


# Index of control edited in 'Manage' panel
ed_ctrl_idx = None


def match_children(roots, patterns):
    # vl = bpy.context.view_layer if not view_layer else view_layer
    # vl.layer_collection
    tomatch = deque(roots)
    matchs = defaultdict(list)
    while tomatch:
        e = tomatch.popleft()
        for i, p in enumerate(patterns):
            if re.fullmatch(p, e.name):
                matchs[e].append(i)
        tomatch.extend(e.children)
    return matchs


def match_entries(entries, patterns):
    matchs = defaultdict(list)
    for e in entries:
        for i, p in enumerate(patterns):
            if re.fullmatch(p, e.name):
                matchs[e].append(i)
    return matchs


def _hide_collection(col, hide):
    col.hide_viewport = hide
def _hide_object(ob, hide):
    ob.hide_set(hide)


def update_targets(self, context):
    pats = [p.value for p in self.patterns]
    invs = [p.invert for p in self.patterns]
    vl = context.view_layer
    if self.trgt == 'OBJ':
        matchs = match_entries(vl.objects, pats)
        hide = _hide_object
    else:
        matchs = match_children([vl.layer_collection], pats)
        hide = _hide_collection

    def as_int(index):
        try:
            # True if active pattern (with same index as 'intp') is
            # inverted
            inv = invs[index]
        except IndexError:
            return

        # Hide every collection matched by any pattern
        # Show collections matched by active pattern
        # If inversion is True, swap hide and show
        for match, indcs in matchs.items():
            hide(match, (index in indcs) == inv)

    if self.type == 'BOOL':
        for match, indcs in matchs.items():
            # Invert if the first pattern this collection matched to
            # is inverted
            hide(match, self.boolp == invs[indcs[0]])
    elif self.type == 'INT':
        as_int(self.intp)
    elif self.type == 'ENUM':
        as_int(int(self.enump))


def update_targets_as_pattern(self, context):
    ctrl = context.scene.ctrls[ed_ctrl_idx]
    update_targets(ctrl, context)


def get_enum(self, context):
    ret = []
    for i, p in enumerate(self.patterns):
        label = p.enum_entry or p.value
        ret.append((str(i), label, ""))
    return ret


class PatternProperty(bpy.types.PropertyGroup):
    value: bpy.props.StringProperty(default="Collection")
    invert: bpy.props.BoolProperty(update=update_targets_as_pattern)
    enum_entry: bpy.props.StringProperty()


class ControlProperty(bpy.types.PropertyGroup):
    type: bpy.props.EnumProperty(
        name="Type",
        items=(
            ('BOOL', "Boolean", ""),
            ('INT', "Integer", ""),
            ('ENUM', "Enumeration", ""),
        ),
    )
    patterns: bpy.props.CollectionProperty(type=PatternProperty)
    name: bpy.props.StringProperty(name="Name")
    boolp: bpy.props.BoolProperty(
        update=update_targets,
    )
    intp: bpy.props.IntProperty(
        update=update_targets,
    )
    enump: bpy.props.EnumProperty(
        name="",
        items=get_enum,
        update=update_targets,
    )
    trgt: bpy.props.EnumProperty(
        name="Target",
        items=(
            ('OBJ', "Objects", ""),
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
            propstr = "boolp"
            if c.type == 'INT':
                propstr = "intp"
            elif c.type == 'ENUM':
                propstr = "enump"

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
        lyt.prop(ctrl, "name")
        lyt.prop(ctrl, "type")
        lyt.prop(ctrl, "trgt")

        # Patterns
        box = lyt.box()
        split = box.split(factor=.8)
        col1 = split.column()
        col2 = split.column()
        col3 = split.column()
        col1.label(text="Patterns")
        col2.label(text="")
        col3.operator("control_center.add_pattern", text="", icon='ADD')
        for i, p in enumerate(ctrl.patterns):
            col1.prop(p, "value", text=str(i), icon_only=True)
            col2.prop(p, "invert", icon_only=True, icon='LOOP_BACK')
            op = col3.operator(
                "control_center.del_pattern",
                text="",
                icon='REMOVE',
                )
            op.pattern_idx = i

        # Dropdown entries
        if ctrl.type == 'ENUM':
            box = lyt.box()
            box.label(text="Dropdown Entries")

            for i, p in enumerate(ctrl.patterns):
                box.prop(p, "enum_entry", text=str(i), icon_only=True)

        row = lyt.row()
        row.operator("control_center.del_control", text="Delete")
        row.operator("control_center.close_manage")


class Add_Control(bpy.types.Operator):
    bl_idname = 'control_center.add_control'
    bl_label = 'Add Control'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.ctrls.add()
        return {"FINISHED"}


class Del_Control(bpy.types.Operator):
    bl_idname = 'control_center.del_control'
    bl_label = 'Delete Control'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global ed_ctrl_idx
        context.scene.ctrls.remove(ed_ctrl_idx)
        ed_ctrl_idx = None
        return {"FINISHED"}


class Edit_Control(bpy.types.Operator):
    bl_idname = 'control_center.edit_control'
    bl_label = 'Edit Control'
    ctrl_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        global ed_ctrl_idx
        ed_ctrl_idx = self.ctrl_idx
        return {"FINISHED"}


class Add_Pattern(bpy.types.Operator):
    bl_idname = 'control_center.add_pattern'
    bl_label = 'Add Pattern'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.ctrls[ed_ctrl_idx].patterns.add()
        return {"FINISHED"}


class Del_Pattern(bpy.types.Operator):
    bl_idname = 'control_center.del_pattern'
    bl_label = 'Delete Pattern'
    bl_options = {"REGISTER", "UNDO"}
    pattern_idx: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        ctrl = context.scene.ctrls[ed_ctrl_idx]
        ctrl.patterns.remove(self.pattern_idx)
        return {"FINISHED"}


class Close_Manage(bpy.types.Operator):
    bl_idname = 'control_center.close_manage'
    bl_label = 'Close'

    def execute(self, context):
        global ed_ctrl_idx
        ed_ctrl_idx = None
        return {"FINISHED"}
