import bpy
import os

# blender.exe --background "./assets/models/blend/dir/file.blend" --python ./process_blend.py
# "E:/Program Files/Blender Foundation/Blender 3.5/blender.exe"
# ./assets/models/blend/postcard/postcard_set_01_4k.blend

print(dir(bpy.data))
blend_file_path = bpy.data.filepath
blend_dir = os.path.dirname(blend_file_path)
model_dir = os.path.join(blend_dir, "models")
os.makedirs(model_dir, exist_ok=True)

bpy.ops.object.select_all(action='DESELECT')

# Loop through all the objects in the scene
scene = bpy.context.scene
for ob in scene.objects:
    # Select each object
    print("object name: ", ob.name)

    # Make sure that we only export meshes
    if ob.type == 'MESH':
        ob.select_set(True)
        # Export the currently selected object to its own file based on its name
        bpy.ops.export_scene.obj(
            filepath=os.path.join(model_dir, f"{ob.name}.obj"),
            use_selection=True,
            use_materials=False,
        )

        # Deselect the object and move on to another if any more are left
        ob.select_set(False)