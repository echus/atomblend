#-----------------------------------------------------------
# File blend.py
#-----------------------------------------------------------
# Blender draw function wrappers

import bpy
import numpy as np
import os

# === OBJECTS ===
# === object creation ===
def create_pointcloud(verts, name, trunc=None):
    """Draw new mesh-pointcloud defined with vertices and zero length edges"""
    if trunc is not None:
        verts = verts[0:trunc]

    # Create new mesh with verts as its vertices, obj
    length = len(verts)
    verts = list(verts)+list(verts)

    edges = []

    # create edges of 0 length for pointcloud viz w/ wireframe material
    for i in range(length):
        edges.append([i, i+length])
    faces = []

    mesh = bpy.data.meshes.new(name+"_mesh")
    mesh.from_pydata(verts, edges, faces)
    obj = bpy.data.objects.new(name, mesh)

    for v in mesh.vertices:
        vv = (v.normal[0], v.normal[1], v.normal[2])
        if sum(vv) != 0:
            print(vv)

    # Link and update scene
    scene = bpy.context.scene
    scene.objects.link(obj)
    scene.objects.active = obj
    obj.select = True
    scene.update()

    return obj

def create_icosphere(name, size=1, origin=(0, 0, 0), smooth=True):
    """Create icosphere primitive"""
    bpy.ops.mesh.primitive_ico_sphere_add(size=size, location=origin)
    obj = bpy.context.object
    obj.name = name
    obj.show_name = True
    mesh = obj.data
    mesh.name = name+"_mesh"
    if smooth:
        bpy.ops.object.shade_smooth()
    return obj

def create_cube_from_verts(name, origin, verts):
    """Create cube with faces defined from input vertices

    verts: arraylike, must define vertices in clockwise order
           starting from bottom face -x, -y, -z point
    """
    # Verts must be defined: bottom face first clockwise, top face clockwise starting from (-x, -y, -z)
    faces = [(0,1,2,3), (4,5,6,7), (0,4,5,1), (1,5,6,2), (2,6,7,3), (3,7,4,0)]
    edges = []

    obj = create_mesh_from_pydata(name, verts, edges, faces)
    obj.location = origin

    return obj

def create_mesh_from_vertices(verts, name, trunc=None):
    """Draw new mesh defined with vertices"""
    if trunc is not None:
        verts = verts[0:trunc]

    # Create new mesh with verts as its vertices, obj
    verts = list(verts)
    edges = []
    faces = []

    obj = create_mesh_from_pydata(name, verts, edges, faces)

    return obj

def create_mesh_from_pydata(name, verts, edges, faces):
    """Create mesh from vert, edge and face definitions"""
    mesh = bpy.data.meshes.new(name+"_mesh")
    mesh.from_pydata(verts, edges, faces)
    obj = bpy.data.objects.new(name, mesh)

    # Link and update scene
    scene = bpy.context.scene
    scene.objects.link(obj)
    scene.objects.active = obj
    obj.select = True
    scene.update()

    return obj

# === object manipulation ===
def OBJECT_delete_all_children(obj):
    """Delete all children of obj"""
    children = obj.children
    for ch in children:
        remove_object(ch)
    return children

def add_to_group(grp, obj):
    """Add obj to group grp"""
    grp.objects.link(obj)

def get_vertices(obj):
    """Get list of vertex tuples for the given object"""
    verts = []
    mesh = obj.data
    for vert in mesh.vertices:
        verts.append((vert.co[0], vert.co[1], vert.co[2]))
    return verts

def add_modifier_wireframe(obj, thickness=0.2):
    """Add wireframe modifier to obj

    thickness: thickness of wireframe
    """
    mod = obj.modifiers.new("Wireframe", type='WIREFRAME')
    mod.thickness = thickness
    mod.show_in_editmode = True
    return mod

def remove_object(obj):
    """Remove object"""
    scene = bpy.context.scene
    bpy.ops.object.select_all(action='DESELECT')
    obj.select = True
    scene.objects.active = obj
    bpy.ops.object.delete()

def OPS_resize():
    return bpy.ops.transform.resize('INVOKE_DEFAULT')

def OBJECT_set_duplitype(obj, type):
    """Set duplication type on obj"""
    obj.dupli_type = type

def OBJECT_set_parent(parent, child):
    """Set parent/child pair"""
    bpy.ops.object.select_all(action='DESELECT')

    # set active object to parent
    bpy.context.scene.objects.active = parent
    child.select = True

    # sets selected object as child of active object
    bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

    # add child object to parent object's groups
    for grp in parent.users_group:
        add_to_group(grp, child)

def obj_view_wireframe(obj):
    """Draw object as wireframe in View3D"""
    obj.show_wire = True
    obj.draw_type = 'WIRE'

def OBJECT_select(obj, sel):
    obj.select = sel

# === MATERIALS ===
# === material creation ===
def create_material_surface(name, mtype='SURFACE', color=(1.0, 1.0, 1.0), specular=(1.0, 1.0, 1.0), shadeless=False, emit=0.0, alpha=1.0):
    """Create basic surface material"""
    mat = bpy.data.materials.new(name)
    mat.type = mtype

    mat.diffuse_color = color
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0

    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5

    mat.emit = emit

    if shadeless:
        mat.use_shadeless = True

    mat.alpha = alpha
    mat.ambient = 1
    return mat

def create_material_wire(name, mtype='WIRE', color=(1.0, 1.0, 1.0), emit=0.0, alpha=1.0):
    """Create basic wireframe material"""
    mat = bpy.data.materials.new(name)
    mat.type = mtype

    mat.diffuse_color = color
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0

    mat.specular_color = color
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5

    mat.emit = emit

    mat.alpha = alpha
    mat.ambient = 1
    return mat

def create_material_halo(name, mtype='HALO', color=(1.0, 1.0, 1.0), alpha=1.0, hard=0, size=0.1, use_tex=True):
    """Create basic halo material"""
    mat = bpy.data.materials.new(name)
    mat.type = mtype

    mat.diffuse_color = color
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0

    mat.specular_color = color
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5

    mat.alpha = alpha
    mat.ambient = 1

    halo = mat.halo
    halo.hardness = hard
    halo.size = size
    halo.use_texture = use_tex

    halo.add = 0
    halo.seed = 0
    return mat

def create_texture_img(name, path):
    realpath = os.path.expanduser(path)
    try:
        img = bpy.data.images.load(realpath)
    except:
        raise NameError("Cannot load image %s" % realpath)

    tex = bpy.data.textures.new(name, type='IMAGE')
    tex.image = img
    return tex

# === material manipulation ===
def set_material(obj, mat):
    """Assign material to object"""
    mesh = obj.data
    mesh.materials.append(mat)

def material_add_texture(mat, tex):
    """Assign texture to material"""
    # Add texture slot
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.blend_type = 'MULTIPLY'
    mtex.use_map_alpha = True
    mtex.use_map_color_diffuse = True
    #mtex.use_face_texture_alpha = True
    return mtex

def object_active_material_remove(obj):
    """Remove active material slot of object"""
    i = obj.active_material_index
    obj.data.materials.pop(i, update_data=True)

# === CAMERAS + LAMPS ===
# === camlamp creation ===
def create_camera(name, origin=(0, 0, 0), clip_start=0.1, clip_end=1000.0):
    """Create camera"""
    # Create and general object options
    cam = bpy.data.cameras.new(name+"_cam")
    obj = bpy.data.objects.new(name, cam)
    obj.location = origin
    obj.show_name = True

    # Lens options
    cam.clip_start = clip_start
    cam.clip_end = clip_end

    # Link to scene and set active
    scene = bpy.context.scene
    scene.objects.link(obj)
    scene.objects.active = obj
    obj.select = True
    scene.camera = obj
    scene.update()

    return obj

def create_lamp(name, origin=(0.0, 0.0, 0.0), rotation_euler=(0.0, 0.0, 0.0), ltype='POINT', color=(0.0, 0.0, 0.0), view_align=True):
    """Create lamp"""
    # Create and general object options
    lamp = bpy.data.lamps.new(name+"_lamp", ltype)
    obj = bpy.data.objects.new(name, lamp)
    obj.location = origin
    obj.rotation_euler = rotation_euler
    obj.show_name = True

    # Lamp options
    lamp.color = color

    # Link to scene and set active
    scene = bpy.context.scene
    scene.objects.link(obj)
    scene.objects.active = obj
    obj.select = True
    scene.update()

    return obj

def add_camera_to_view(name, clip_start=0.1, clip_end=1000.0):
    """Create camera positioned at current view"""
    cam = create_camera(name=name, clip_start=clip_start, clip_end=clip_end)
    # Move camera to current view
    bpy.ops.view3d.camera_to_view()
    return cam

def add_camlamp_to_view(ltype='SUN', lcolor=(1.0, 1.0, 1.0), clip_start=0.1, clip_end=1000.0):
    """TEMP: Create camera and lamp positioned at current view"""
    cam = create_camera(name="Camera", clip_start=clip_start, clip_end=clip_end)
    # Move camera to current view
    bpy.ops.view3d.camera_to_view()

    # FIXME TEMP add lamp at camera's position and rotation
    loc = cam.location
    rot = cam.rotation_euler
    lamp = create_lamp(name="Lamp", origin=loc, rotation_euler=rot, ltype=ltype, color=lcolor)

    return cam, lamp

# === camlamp manipulation ===
def make_camera_active(cam):
    """Set cam to active camera"""
    scene = bpy.context.scene
    scene.camera = cam

def position_camera_on():
    """Turn View3D viewpoint camera positioning on"""
    bpy.context.region_data.view_perspective = 'CAMERA'
    bpy.context.space_data.lock_camera = True

def position_camera_off():
    """Turn View3D viewpoint camera positioning off"""
    bpy.context.space_data.lock_camera = False
    bpy.context.region_data.view_perspective = 'PERSP'




# === VIEW3D/SCENE ===
# === [view] operations ===
def delete_all_meshes():
    """ Delete all objects/meshes in scene """
    # Gather list of items of interest
    candidate_list = [item.name for item in bpy.data.objects if item.type == "MESH"]

    # Select them only
    for object_name in candidate_list:
        bpy.data.objects[object_name].select = True

    # Remove all selected
    bpy.ops.object.delete()

    # Remove the meshes, they have no users anymore.
    for item in bpy.data.meshes:
        bpy.data.meshes.remove(item)

def create_group(groupname):
    """Create new group"""
    grp = bpy.data.groups.new(groupname)
    return grp

def group_get(groupname):
    for grp in bpy.data.groups:
        if groupname == grp.name:
            return grp
    return False

# === viewpoint maniuplation ===
def view_selected_pattern(exp):
    """Select objects with name matching exp, and view"""
    bpy.ops.object.select_pattern(pattern=exp, case_sensitive=False, extend=False)
    bpy.ops.view3d.view_selected()

def view_selected_group(gname):
    """Select objects in gname group, and view"""
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.object.select_same_group(group=gname)
    bpy.ops.view3d.view_selected()

# === [view] information ===
def get_area(name='VIEW_3D'):
    # get view3d space object
    def areas_tuple():
        res = {}
        count = 0
        for area in bpy.context.screen.areas:
            res[area.type] = count
            count += 1
        return res

    areas = areas_tuple()
    view3d = bpy.context.screen.areas[areas[name]].spaces[0]
    return view3d












# === SCRAPS ===
# FIXME FIXME FIXME
def add_lamp_to_view(name, ltype='SUN', color=(0.0, 0.0, 0.0)):
    # FIXME a bit hacky here
    # Creates camera, sets camera to view,
    # gets its location and rotation and applies these to lamp

    # --- Previous code attempting to use rv3d properties ---
    ### TODO test if this works if mouse is outside of view3d??
    #v3d = get_area('VIEW_3D')
    #rv3d = v3d.region_3d
    ###
    #### calculate position to place lamp at
    #loc = rv3d.view_location.copy()            # Vector location
    #rot = rv3d.view_rotation.to_euler()        # Quaternion rotation
    #mat = rv3d.view_matrix         # 4x4 rotation matrix
    #pmat = rv3d.perspective_matrix
    #loc, rot, sca = (pmat+mat).decompose()
    # -------------------------------------------------------
    #bpy.ops.object.lamp_add(type=lamptype, location=loc, rotation=rot)
    #obj = bpy.context.object
    #obj.name = name
    #return obj

    scene = bpy.context.scene

    # Camera hacks ...
    bpy.ops.object.camera_add()
    cam_obj = bpy.context.object
    bpy.ops.view3d.camera_to_view()

    # Add lamp at current camera location and view rotation
    bpy.ops.object.lamp_add(type=lamptype, location=cam_obj.location, view_align=True)
    lamp_obj = bpy.context.object
    lamp_obj.name = name
    lamp_data = lamp_obj.data
    lamp_data.name = name+"_data"

    # Create lamp datablock, create obj, link to scene
    #lamp_data = bpy.data.lamps.new(name=name+"_data", type='SUN')
    #lamp_object = bpy.data.objects.new(name=name, object_data=lamp_data)
    #scene.objects.link(lamp_object)

    #lamp_object.location = cam_obj.location
    #lamp_object.rotation = rv3d.view_rotation.to_euler()

    # Remove camera
    #bpy.ops.object.select_all(action='DESELECT')
    #cam_obj.select = True
    #scene.objects.active = cam_obj
    #bpy.ops.object.delete()

    # Make active
    lamp_obj.select = True
    scene.objects.active = lamp_obj

    return lamp_obj

# FIXME is this needed??
def set_cursor_pivot_to_center(points):
    center = np.mean(points, axis=0)

    # Move cursor to centre of mesh and set pivot point around cursor
    def areas_tuple():
        res = {}
        count = 0
        for area in bpy.context.screen.areas:
            res[area.type] = count
            count += 1
        return res
    areas = areas_tuple()
    view3d = bpy.context.screen.areas[areas['VIEW_3D']].spaces[0]

    view3d.pivot_point='CURSOR'
    view3d.cursor_location = tuple(center)



