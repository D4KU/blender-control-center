<div align="center">
<img src="https://github.com/D4KU/blender-control-center/blob/main/media/showcase.gif" width="661" />

*Switching between sets of objects becomes easy*


![](https://github.com/D4KU/blender-control-center/blob/main/media/new_control.gif)
<br/>*Customize controls to fit your demands*
</div>

This blender addon expands on the idea of *View Layers*. It allows you to
create controls like sliders, dropdowns, and checkboxes that you can hook up
to objects or collections in your scene. Those objects are then set hidden or
visible depending on the state of those controls. For example, you can create
a checkbox that toggles all objects with the string *Cube* in their names.

# Installation

* Download this repositories code as zip archive
* In Blender, navigate to `Edit > Preferences > Add-ons`
* Hit the **Install** button
* Select the downloaded file
* Enable the Addon in the list

# Manual

After installation, you can find the plugin in the right-hand bar of the 3D
view. It is divided into two panels: *Use* and *Manage*.

## Use Panel

The *Use* panel shows all the controls you have set up. This is where you
interact with them to actually manipulate objects and collections in your
scene.

## Manage Panel

The *Manage* panel shows the settings of one specific control you wish to
modify. To enter it, click on the three dots icon next to a control. It shows
the following elements:

| Element | Function |
| ------------ | -------- |
| Name | Set the name of your control |
| Type | Set whether the control is a checkbox, slider, or dropdown |
| Action | What should happen when a control state is changed? Should an object's visibility be toggled? Or a collection's? Or should objects be selected? |
| States | For each state of the control, set the objects or collections to manipulate. More below. |

### The State list

Controls have a modifiable number of *states*. Sliders have one for each
integer: if you add four states to a slider, you can change the slider between
zero and three. For each state you add to a dropdown you gain a new entry in
its list. Checkboxes can only handle two states: on and off. It toggles
between the first two states you add to it, and ignores all others.

Each state has the following attributes:

#### Name

Each state has a name, but only dropdowns are able to show it. It's the
string shown in the corresponding entry in their list.

#### Match by

The match type of a state specifies how you like to provide the state with the
*targets* (objects or collections) to manage. A match by *reference* lets you
directly choose a target from a list; a match by name let's you specify a
*regular expression*. By choosing the latter, the state is linked to each
target with a name for which the expression matches.

#### Patterns

Each state lets you specify an arbitrary number of *patterns* (regular
expressions or references). If a state becomes active after making changes to
its control in the *Use* panel, its associated targets are shown (or
selected, depending on your control's *action*). Targets associated with
other states of the control are hidden or deselected.  Objects or collections
not linked to any state of the control are ignored.  Regardless of type, per
control there is always only one active state.


## About hiding

Maybe you have noticed that Blender's interplay of object hierarchy and
visibility is a bit different from other applications. When you hide an
object, its children actually stay visible. You can hold *Alt* to hide them as
well, but if you then turn a child back on, it shows up despite of its parent
still being hidden. Many other applications make the parent override the state
of its children. Regardless whether a child wants to be visible, if the parent
is hidden, so are all of its children. If the parent is visible however, the
children can decide for themselves.

To be useful *Control Center* actually relies on this behaviour, so it
imitates it. An active state will not enable an associated object if one of
its parents is hidden. But it will keep track of this child's status
internally, so that when the parent does become visible, the child is
activated as well. Other children still wanting to be hidden stay hidden.

Why is this behaviour so important? Let me give you an example. Imagine one
checkbox toggles a parent object for all fences in the scene. Besides that, a
dropdown lets you choose between a construction fence and a wire fence. The
objects for those fence variants are children of the *Fences* object. If the
checkbox is turned off, you don't want any of the fences to be visible,
regardless of the type chosen by the dropdown. But if you turn the
checkbox on, you don't want both fences to be visible, either. Only the chosen
one. You can't easily replicate this interplay without the behaviour described
above. That's why this plugin operates the way it does.
