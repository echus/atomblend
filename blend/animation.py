import bpy

# variables
offset = (100, 0, 0) #offset of camera with respect to origin
camOrthoScale = 150 #orthographic scale of camera
camClipDist = 500
animationDuration = 4 #s
fps = 25 #frames per second
rotAngle = 360 * 3.1416/180 #angle the camera will rotate in rad
resX = 1024 #render resolution x
resY = 1024 #render resolution y


# statics
START_FRAME = 1


# scene setup
endFrame = START_FRAME + animationDuration * fps -1 

bpy.context.scene.frame_start =  START_FRAME
bpy.context.scene.frame_end =  endFrame

for scene in bpy.data.scenes:
    scene.render.resolution_x = resX
    scene.render.resolution_y = resY

bpy.ops.object.select_all(action='DESELECT')


# creation of objects

# empties (act as reference coordinates)
bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
bpy.context.object.empty_draw_size = 20
bpy.context.object.name = "cam master"

bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
bpy.context.object.empty_draw_size = 20
bpy.context.object.name = "cam target"


# camera + constraint
bpy.ops.object.camera_add(view_align=True, enter_editmode=False, location=offset, rotation=(0,0,0),)
bpy.context.object.name = "animation cam"
bpy.context.object.data.type = 'ORTHO'
bpy.context.object.data.ortho_scale = camOrthoScale
bpy.context.object.data.ortho_scale = 100
bpy.context.object.data.show_limits = True
bpy.context.object.data.clip_end = camClipDist


bpy.ops.object.constraint_add(type='TRACK_TO')
bpy.context.object.constraints["Track To"].target = bpy.data.objects["cam target"]
bpy.context.object.constraints["Track To"].track_axis = 'TRACK_NEGATIVE_Z'
bpy.context.object.constraints["Track To"].up_axis = 'UP_Y'
bpy.context.object.data.show_guide = {'THIRDS'}



#set parenting
master = bpy.data.objects['cam master']
target = bpy.data.objects['cam target']

master.select = True
target.select = True

bpy.context.scene.objects.active = master
bpy.ops.object.parent_set()


bpy.ops.object.select_all(action='DESELECT')



#add animation
master.select = True
bpy.context.scene.objects.active = master

# set rotation for first frame
bpy.context.scene.frame_set(START_FRAME)
bpy.ops.anim.keyframe_insert(type='Rotation')
#set rotation for last frame
bpy.context.scene.frame_set(endFrame)
master.rotation_euler = (0,0,rotAngle)
bpy.ops.anim.keyframe_insert(type='Rotation')


#turn graph handles to vector
oldAreaType = bpy.context.area.type

bpy.context.area.type = 'GRAPH_EDITOR'
bpy.ops.graph.handle_type(type='VECTOR')
bpy.ops.graph.extrapolation_type(type='LINEAR')

bpy.context.area.type = oldAreaType
