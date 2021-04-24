import bpy
from importlib import reload
from . import props, panels, ops

if "bpy" in locals():
    # Blender already started once
    reload(props)
    reload(ops)
    reload(panels)


bl_info = {
    "name": "Control Center",
    "description": (
        "Hide collections via customizable controls and regular "
        "expressions."
    ),
    "author": "David Kutschke",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "3D View > Sidebar",
    "category": "Interface"
}


_to_register = (
    props.Pattern,
    props.State,
    props.Control,
    ops.AddControl,
    ops.DelControl,
    ops.EditControl,
    ops.AddState,
    ops.DelState,
    ops.AddPattern,
    ops.DelPattern,
    ops.CloseManagePanel,
    panels.VIEW3D_PT_ControlCenter_Use,
    panels.VIEW3D_PT_ControlCenter_Manage,
)


def register():
    for c in _to_register:
        bpy.utils.register_class(c)

    bpy.types.Scene.ctrls =\
        bpy.props.CollectionProperty(type=props.Control)


def unregister():
    for c in _to_register:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.ctrls


if __name__ == "__main__":
    register()
