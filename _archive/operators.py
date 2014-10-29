# =============================================================================
# (C) Copyright 2014
# Australian Centre for Microscopy & Microanalysis
# The University of Sydney
# =============================================================================
# File:   operators.py
# Date:   2014-07-01
# Author: Varvara Efremova
#
# Description:
# AtomBlend operator definitions.
# =============================================================================

import bpy
import numpy as np

# bpy types used
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

# Own pkgs
from .aptread import APTloader
from . import blend

# TODO move this to a default settings module
HALO_IMG_PATH = "/Users/varvara/Library/Application Support/Blender/2.70/scripts/addons/AtomBlend/atomtex.png"

# Operator classes
class VIEW3D_OT_pospath_button(Operator, ImportHelper):
    """Select POS file from dialogue"""
    bl_idname = "view3d.import_pospath"
    bl_label = "Select .pos file"

    # ImportHelper mixin class uses this
    filename_ext = ".pos"

    filter_glob = StringProperty(
            default="*.pos",
            options={'HIDDEN'},
            )

    def execute(self, context):
        props = context.scene.pos_panel_props
        # set pos filename
        props.pos_filename = self.filepath
        return {'FINISHED'}

class VIEW3D_OT_rngpath_button(Operator, ImportHelper):
    """Select RNG file from dialogue"""
    bl_idname = "view3d.import_rngpath"
    bl_label = "Select .rng file"

    # ImportHelper mixin class uses this
    filename_ext = ".rng"

    filter_glob = StringProperty(
            default="*.rng",
            options={'HIDDEN'},
            )

    def execute(self, context):
        props = context.scene.pos_panel_props
        # set rng filename
        props.rng_filename = self.filepath
        return {'FINISHED'}

class VIEW3D_OT_load_posrng_button(Operator):
    """Read and load POS/RNG files into memory"""
    bl_idname = "view3d.load_posrng"
    bl_label = "Load POS/RNG files"

    def execute(self, context):
        return _load_posrng_exec(self, context)

class VIEW3D_OT_bake_button(Operator):
    """Bake POS data to object"""
    bl_idname = "view3d.bake_button"
    bl_label = "Bake to object"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        return (area == 'VIEW_3D') and (mode == 'OBJECT')

    def execute(self, context):
        return _bake_exec(self, context)

class VIEW3D_OT_clear_button(Operator):
    """Clears all meshes in the scene"""
    bl_idname = "view3d.clear_button"
    bl_label = "Clear all objects"

    def execute(self, context):
        return _clear_exec(self, context)

class VIEW3D_OT_remove_duplivert(Operator):
    """Remove vertex duplication object on active object"""
    bl_idname = "view3d.remove_duplivert"
    bl_label = "Remove vertex object"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        obj = context.object
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (obj is not None) and (obj.vistype == 'DUPLI')

    def execute(self, context):
        return _remove_duplivert_exec(self, context)

class VIEW3D_OT_dupli_vert(Operator):
    """Duplicate icosphere on vertices of currently active object"""
    bl_idname = "view3d.add_duplivert"
    bl_label = "Add vertex object"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        obj = context.object
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (obj is not None)

    def execute(self, context):
        return _dupli_vert_exec(self, context)

class VIEW3D_OT_add_halo_material(Operator):
    """Apply halo material to currently selected object"""
    bl_idname = "view3d.add_halomat"
    bl_label = "Add halo material"

    # path to billboard texture
    halo_img_path = StringProperty(
            description = "Image to use for halo texture",
            default = HALO_IMG_PATH
            )

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        obj = context.object
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (obj is not None)

    def execute(self, context):
        return _add_halo_material_exec(self, context)

class VIEW3D_OT_add_halo_material(Operator):
    """Remove halo material on currently selected object"""
    bl_idname = "view3d.remove_halomat"
    bl_label = "Remove halo material"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        obj = context.object
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (obj is not None) and (obj.vistype == 'HALO')

    def execute(self, context):
        return _remove_halo_material_exec(self, context)

class VIEW3D_OT_add_camera_view(Operator):
    """View3D: Add camera placed at current view"""
    bl_idname = "view3d.add_camera"
    bl_label = "Place camera here"

    @classmethod
    def poll(cls, context):
        # Needs View3D, object mode (for selection), and view_perspective to be PERSP
        area = context.area.type
        mode = context.mode
        persp = context.region_data.view_perspective
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (persp == 'PERSP')

    def execute(self, context):
        return _add_camera_view_exec(self, context)

class VIEW3D_OT_add_lamp_view(Operator):
    """Add lamp placed at current view location"""
    bl_idname = "view3d.add_lamp"
    bl_label = "Place lamp here"

    @classmethod
    def poll(cls, context):
        # Needs View3D, object mode (for selection), and view_perspective to be PERSP
        area = context.area.type
        mode = context.mode
        persp = context.region_data.view_perspective
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (persp == 'PERSP')

    def execute(self, context):
        return _add_lamp_view_exec(self, context)

class VIEW3D_OT_add_bounding_box(Operator):
    """Add a bounding box to current data"""
    bl_idname = "view3d.add_bound_box"
    bl_label = "Add bounding box"

    def execute(self, context):
        return _add_bounding_box_exec(self, context)

class VIEW3D_OT_make_camera_active(Operator):
    """Make currently selected camera active"""
    bl_idname = "view3d.make_camera_active"
    bl_label = "Make camera active"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        obj = context.object
        if obj is None:
            return False
        return (area == 'VIEW_3D') and (obj.type == 'CAMERA')

    def execute(self, context):
        return _make_camera_active_exec(self, context)

class VIEW3D_OT_position_active_camera(Operator):
    """Position currently active camera"""
    bl_idname = "view3d.position_cam"
    bl_label = "Position active camera"

    positioning = bpy.props.BoolProperty(name="Positioning", default=False)

    @classmethod
    def poll(cls, context):
        area = context.area.type
        cam = context.scene.camera
        if cam is None:
            return False
        return (area == 'VIEW_3D')

    def execute(self, context):
        if self.positioning == False:
            self.positioning = True
            return _position_active_camera_exec_on(self, context)
        else:
            self.positioning = False
            return _position_active_camera_exec_off(self, context)

class VIEW3D_OT_pointcloud_add(Operator):
    """Create pointcloud visualisation for the active object"""
    bl_idname = "view3d.pointcloud_add"
    bl_label = "Create pointcloud"

    @classmethod
    def poll(cls, context):
        area = context.area.type
        mode = context.mode
        objtype = None
        if context.object is not None:
            objtype = context.object.type
        return (area == 'VIEW_3D') and (mode == 'OBJECT') and (objtype == 'MESH')

    def execute(self, context):
        return _pointcloud_add(self, context)

class VIEW3D_OT_scale_child(Operator):
    """Scale child of currently selected object"""
    bl_idname = "view3d.scale_child"
    bl_label = "Scale vertex object"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj is not None) and obj.children

    def execute(self, context):
        obj = context.object
        child = obj.children[0]

        # select child and deselect obj
        blend.object.select(obj, False)
        blend.object.select(child, True)
        return blend.object.selected_resize()

# === Private button execute functions ===
def _position_active_camera_exec_on(self, context):
    blend.space.camera_position_on()
    return {'FINISHED'}

def _position_active_camera_exec_off(self, context):
    blend.space.camera_position_off()
    return {'FINISHED'}

def _make_camera_active_exec(self, context):
    cam = context.object
    blend.space.camera_set_active(cam)
    return {'FINISHED'}

def _add_bounding_box_exec(self, context):
    props = context.scene.pos_panel_props
    padding = props.boundbox_padding

    # FIXME don't load this again!!! save as global var for now?
    data = APTloader.ReadAPTData(props.pos_filename, props.rng_filename)

    pointlist = data.xyz
    xyzmax = np.amax(pointlist, axis=0) # max locations in data
    xyzmin = np.amin(pointlist, axis=0) # min locations in data

    # add padding to extremal xyz coords
    xyzmax += padding
    xyzmin -= padding

    # define vertices of cube, clockwise, starting from bottom
    coords = [[-1, -1, -1],
             [-1,  1, -1],
             [ 1,  1, -1],
             [ 1, -1, -1],
             [-1, -1,  1],
             [-1,  1,  1],
             [ 1,  1,  1],
             [ 1, -1,  1]]
    coords = np.array(coords)
    # numpy where is awesome
    # (replaces -ves with respective min values, +ves with max values)
    verts = np.where(coords > 0, xyzmax, xyzmin)

    # create bounding box and draw as wireframe
    name = "Bound"
    origin = (0.0, 0.0, 0.0)
    bound = blend.object.cube_add_from_verts(name, origin, verts)
    boundmat = blend.material.surface_add(name+"_mat", shadeless=True)
    blend.material.set(bound, boundmat)
    blend.object.modifier_add_wireframe(bound)

    grp = blend.space.group_get("Bounds")
    if not grp:
        grp = blend.space.group_add("Bounds")
    blend.space.group_add_object(grp, bound)

    bound.datatype = 'BOUND'
    return {'FINISHED'}

def _add_lamp_view_exec(self, context):
    props = context.scene.pos_panel_props

    # FIXME temp hack
    cam, lamp = blend.space.camlamp_add_to_view(ltype='SUN')
    blend.object.delete(cam)
    context.scene.objects.active = lamp
    # end temp hack

    # proper code ...
    #drawing.add_lamp_to_view(name="Lamp", ltype='SUN', color=color)

    # Add to lamp group
    grp = blend.space.group_get("Lamps")
    if not grp:
        grp = blend.space.group_add("Lamps")
    blend.space.group_add_object(grp, lamp)
    return {'FINISHED'}

def _pointcloud_add(self, context):
    props = context.scene.pos_panel_props
    color = props.ptcld_color
    emit = props.ptcld_emit

    obj = context.object

    # Get list of verts from active object
    verts = blend.object.vertices_get(obj)

    # Create pointcloud from these verts and set its parent to active obj
    ptcld = blend.object.pointcloud_add(verts, obj.name+"_pointcloud")
    blend.object.parent_set(obj, ptcld)

    # Add wireframe material
    # TODO FIXME
    mat = drawing.create_material_wire(ptcld.name+"_mat", color=color, emit=emit)
    blend.material.set(ptcld, mat)
    return {'FINISHED'}

def _add_camera_view_exec(self, context):
    cam = blend.space.camera_add_to_view(name="Camera", clip_start=0.1, clip_end=1000.0)

    # Add to camera group
    grp = blend.space.group_get("Cameras")
    if not grp:
        grp = blend.space.group_add("Cameras")
    blend.space.group_add_object(grp, cam)
    return {'FINISHED'}

def _add_halo_material_exec(self, context):
    obj = context.object

    mat = blend.material.halo_add(obj.name+"_halo", use_tex=True)
    tex = blend.material.texture_add_img(obj.name+"_tex", path=self.halo_img_path)
    blend.material.texture_add(mat, tex)
    blend.material.set(obj, mat)

    obj.vistype = 'HALO'
    return{'FINISHED'}

def _remove_halo_material_exec(self, context):
    obj = context.object
    blend.object.active_material_delete(obj)

    obj.vistype = 'NONE'
    return{'FINISHED'}

def _dupli_vert_exec(self, context):
    # Applies vertex duplication with icospheres to currently selected objects
    # select object to add mesh child to (props)
    # create desired mesh (props)

    # active object is parent
    obj = context.object

    # create child icosphere
    vertobj = blend.object.icosphere_add(name=obj.name+"_vert")

    # create material for child icosphere, link to child
    vertmat = blend.material.surface_add(name=obj.name+"_mat")
    blend.material.set(vertobj, vertmat)

    blend.object.parent_set(obj, vertobj)
    blend.object.dupli_set(obj, 'VERTS')

    obj.vistype = 'DUPLI'
    return {'FINISHED'}

def _remove_duplivert_exec(self, context):
    obj = context.object
    blend.object.delete_children(obj)
    blend.object.dupli_set(obj, 'NONE')

    obj.vistype = 'NONE'
    return{'FINISHED'}

def _clear_exec(self, context):
    # Clear all objects and meshes in scene
    blend.space.delete_all()
    return {'FINISHED'}

def _bake_exec(self, context):
    # Draws currently selected data
    # called by: draw_button operator
    props = context.scene.pos_panel_props
    plot_type = props.plot_type

    # FIXME temp don't do this, should be able to store ReadAPTData object in blender props??
    data = APTloader.ReadAPTData(props.pos_filename, props.rng_filename)

    if plot_type == 'ISO':
        groupname = "Isotopes"
        listfunc = "rnglist"
        getfunc = "getrng"
    elif plot_type == 'EA':
        groupname = "Elements"
        listfunc = "atomlist"
        getfunc = "getatom"
    elif plot_type == 'ION':
        groupname = "Ions"
        listfunc = "ionlist"
        getfunc = "getion"

    # populate item names and point locations
    itemlist = getattr(data, listfunc)

    namelist = []
    pointlist = []
    for ind, item in enumerate(itemlist):
        # convert item to string name
        namelist.append(str(item))
        # get points (vertices) for current item and append
        pointlist.append(getattr(data, getfunc)(ind))

    # Create group for meshes of same type
    grp = blend.space.group_add(groupname)

    # Draw all meshes in pointlist and link to group
    for name, verts in zip(namelist, pointlist):
        obj = blend.object.object_add_from_verts(verts, name, trunc=None)
        obj.datatype = 'DATA'
        blend.space.group_add_object(grp, obj)

    # centre view on created group
    blend.space.view_selected_group(groupname)
    return {'FINISHED'}

def _load_posrng_exec(self, context):
    # Load APT pos/rng data
    # called by: load_posrng_button operator
    # populates props.atomlist collection property with atoms in rng file
    props = context.scene.pos_panel_props

    try:
        data = APTloader.ReadAPTData(props.pos_filename, props.rng_filename)
        print("Loaded rng data: ", data.atomlist) # DEBUG
        self.report({'INFO'}, "Loaded %s as POS, %s as RNG" % \
                (props.pos_filename, props.rng_filename))
    except APTloader.APTReadError:
        self.report({'ERROR'}, "Error reading pos or rng file. Double check file names.")
        return {'CANCELLED'}

    # separate ion names and index refs for data.getion
    print("--- ATOMLIST", data.atomlist)
    print("--- RNGLIST", data.rnglist)
    print("--- IONLIST", data.ionlist)
    return {'FINISHED'}
