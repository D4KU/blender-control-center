import bpy
from importlib import reload
from . import main

if "bpy" in locals():
    # Blender already started once
    reload(main)


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
    main.PatternProperty,
    main.ControlProperty,
    main.VIEW3D_PT_ControlCenter_Use,
    main.VIEW3D_PT_ControlCenter_Manage,
    main.Add_Control,
    main.Del_Control,
    main.Edit_Control,
    main.Add_Pattern,
    main.Del_Pattern,
    main.Close_Manage,
)


def register():
    for c in _to_register:
        bpy.utils.register_class(c)

    bpy.types.Scene.ctrls =\
        bpy.props.CollectionProperty(type=main.ControlProperty)


def unregister():
    for c in _to_register:
        bpy.utils.unregister_class(c)

    del bpy.types.Scene.ctrls


if __name__ == "__main__":
    register()
