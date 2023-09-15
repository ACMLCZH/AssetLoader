import bpy
import bmesh

# Create a new mesh object
mesh = bpy.data.meshes.new(name="Cube")
obj = bpy.data.objects.new(name="Cube", object_data=mesh)

# Link the object to the current collection
bpy.context.collection.objects.link(obj)

# Set the object as the active object
bpy.context.view_layer.objects.active = obj
obj.select_set(True)

# Create a BMesh instance
bm = bmesh.new()

# Define the vertices of the cube
verts = [
    bm.verts.new((-1, -1, -1)),
    bm.verts.new((-1, -1, 1)),
    bm.verts.new((-1, 1, -1)),
    bm.verts.new((-1, 1, 1)),
    bm.verts.new((1, -1, -1)),
    bm.verts.new((1, -1, 1)),
    bm.verts.new((1, 1, -1)),
    bm.verts.new((1, 1, 1))
]

# Define the faces of the cube
faces = [
    bm.faces.new((verts[0], verts[2], verts[3], verts[1])),
    bm.faces.new((verts[0], verts[4], verts[6], verts[2])),
    bm.faces.new((verts[4], verts[5], verts[7], verts[6])),
    bm.faces.new((verts[5], verts[1], verts[3], verts[7])),
    bm.faces.new((verts[2], verts[6], verts[7], verts[3])),
    bm.faces.new((verts[0], verts[1], verts[5], verts[4]))
]

# Define the UV coordinates for each vertex
uvs = [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1)
]

# Create a new UV map
uv_layer = bm.loops.layers.uv.verify()

# Assign the UV coordinates to each loop in each face
for face in faces:
    for loop in face.loops:
        loop_index = loop.vert.index % 4
        loop[uv_layer].uv = uvs[loop_index]

# Update the mesh with the new data
bm.to_mesh(mesh)
bm.free()
