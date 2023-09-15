import os
import numpy as np
import base64
import trimesh
from PIL import Image
from io import BytesIO
import pygltflib

from . import geom as geom_utils
import unisim as us

class GLBObject:
    def __init__(self,
        vertices,
        faces,
        vertex_normals,
        vertex_colors,
        uvs,
        image_texture,
        metallic_texture,
        roughness_texture
    ):
        self.vertices          = vertices
        self.faces             = faces
        self.vertex_normals    = vertex_normals
        self.vertex_colors     = vertex_colors
        self.uvs               = uvs
        self.image_texture     = image_texture
        self.metallic_texture  = metallic_texture
        self.roughness_texture = roughness_texture

class GLBObjectScene:
    def __init__(self, filename):
        self.filename = filename
        self.objects = list()

        glb = pygltflib.GLTF2().load(filename)
        glb.convert_images(pygltflib.ImageFormat.DATAURI)       # for accessing the binary image data

        binary_blob = glb.binary_blob()        # all binary data
        scene = glb.scenes[glb.scene]

        mesh_list = list()
        for node_index in scene.nodes:
            root_mesh_list = parse_tree(glb.nodes, node_index)
            mesh_list.extend(root_mesh_list)

        for i in range(len(mesh_list)):
            mesh = glb.meshes[mesh_list[i][0]]
            matrix = mesh_list[i][1]
            primitive = mesh.primitives[0]
            us.logger.debug(f"Mesh index: {i}")
            us.logger.debug(f"    Attributes={primitive.attributes}")
            us.logger.debug(f"    Indices={primitive.indices}, Material={primitive.material}")
            # "primitive.attributes" records the indices in "accessors". It is like:
            #      Attributes(POSITION=2, NORMAL=1, TANGENT=None, TEXCOORD_0=None, TEXCOORD_1=None,
            #                 COLOR_0=None, JOINTS_0=None, WEIGHTS_0=None)

            # parse vertices
            points_accessor = glb.accessors[primitive.attributes.POSITION]
            points_buffer_view = glb.bufferViews[points_accessor.bufferView]
            points = np.frombuffer(
                binary_blob[
                    points_buffer_view.byteOffset + points_accessor.byteOffset:
                    points_buffer_view.byteOffset + points_buffer_view.byteLength
                ],
                dtype=np.float32, count=points_accessor.count * 3,
            ).reshape((-1, 3))
            us.logger.debug(f"Points: {points.shape}")
            
            # parse faces
            triangles_accessor = glb.accessors[primitive.indices]
            triangles_buffer_view = glb.bufferViews[triangles_accessor.bufferView]
            triangles_component_type = triangles_accessor.componentType
            # triangles_buffer_range = triangles_buffer_view.byteLength - triangles_accessor.byteOffset
            if triangles_component_type == pygltflib.UNSIGNED_BYTE:
                triangles_t = np.uint8
            elif triangles_component_type == pygltflib.UNSIGNED_INT:
                triangles_t = np.uint32
            else:
                raise Exception(f"Invalid triangles uint alignment, component_type: {triangles_component_type}")
            triangles = np.frombuffer(
                binary_blob[
                    triangles_buffer_view.byteOffset + triangles_accessor.byteOffset:
                    triangles_buffer_view.byteOffset + triangles_buffer_view.byteLength
                ],
                dtype=triangles_t, count=triangles_accessor.count
            ).reshape((-1, 3)).astype(np.int32)
            us.logger.debug(f"Triangles: {triangles.shape}, "
                            f"{triangles_buffer_view.byteLength - triangles_accessor.byteOffset}")

            # parse normals
            if primitive.attributes.NORMAL:
                normals_accessor = glb.accessors[primitive.attributes.NORMAL]
                normals_buffer_view = glb.bufferViews[normals_accessor.bufferView]
                normals = np.frombuffer(
                    binary_blob[
                        normals_buffer_view.byteOffset + normals_accessor.byteOffset:
                        normals_buffer_view.byteOffset + normals_buffer_view.byteLength
                    ],
                    dtype=np.float32, count=normals_accessor.count * 3,
                ).reshape((-1, 3))
                us.logger.debug(f"Normals: {normals.shape}, "
                                f"{normals_buffer_view.byteLength - normals_accessor.byteOffset}")
            else:
                normals = None

            # parse images
            color_image, metallic_image, roughness_image = None, None, None
            if primitive.material is not None:
                material = glb.materials[primitive.material]

                # Check if material has a base color texture
                if material.pbrMetallicRoughness.baseColorTexture is not None:
                    texture = glb.textures[material.pbrMetallicRoughness.baseColorTexture.index]
                    image_index = texture.source
                    color_image = uri_to_image(glb.images[image_index].uri)
                    # image_data = Image.open(image_data).convert("RGBA")

                # parse colors
                if material.pbrMetallicRoughness.baseColorFactor is not None:
                    colors_factor = material.pbrMetallicRoughness.baseColorFactor
                    colors_factor = np.array(colors_factor, dtype=np.float32)
                    if color_image is None:
                        color_image = Image.new("RGBA", (1, 1), (255, 255, 255, 255))
                    # colors_factor
                    bands = color_image.split()
                    color_image = Image.merge("RGBA", [
                        Image.eval(bands[i], lambda x: x * colors_factor[i]) for i in range(4)
                    ])

                if material.pbrMetallicRoughness.metallicRoughnessTexture is not None:
                    texture = glb.textures[material.pbrMetallicRoughness.metallicRoughnessTexture.index]
                    image_index = texture.source
                    image = uri_to_image(glb.images[image_index].uri)
                    # image_data = BytesIO()
                    # image = Image.open(image_data)
                    bands = image.split()
                    metallic_image, roughness_image = bands[1], bands[2]    # G for metallic, B for roughness

                if material.pbrMetallicRoughness.metallicFactor is not None:
                    metallic_factor = material.pbrMetallicRoughness.metallicFactor
                    if metallic_image is None:
                        metallic_image = Image.new("L", (1, 1), 255)
                    metallic_image = Image.eval(metallic_image, lambda x: x * metallic_factor)

                if material.pbrMetallicRoughness.roughnessFactor is not None:
                    roughness_factor = material.pbrMetallicRoughness.roughnessFactor
                    if roughness_image is None:
                        roughness_image = Image.new("L", (1, 1), 255)
                    roughness_image = Image.eval(roughness_image, lambda x: x * roughness_factor)
            
            # parse uvs
            if primitive.attributes.TEXCOORD_0:
                texcoords_accessor = glb.accessors[primitive.attributes.TEXCOORD_0]
                texcoords_buffer_view = glb.bufferViews[texcoords_accessor.bufferView]
                uvs = np.frombuffer(
                    binary_blob[
                        texcoords_buffer_view.byteOffset + texcoords_accessor.byteOffset:
                        texcoords_buffer_view.byteOffset + texcoords_buffer_view.byteLength
                    ],
                    dtype=np.float32, count=texcoords_accessor.count * 2,
                ).reshape((-1, 2))
            else:
                uvs = None

            # parse colors
            if primitive.attributes.COLOR_0:
                colors_accessor = glb.accessors[primitive.attributes.COLOR_0]
                colors_buffer_view = glb.bufferViews[colors_accessor.bufferView]
                if colors_accessor.type == "VEC3":
                    colors_vec = 3
                elif colors_accessor.type == "VEC4":
                    colors_vec = 4
                else:
                    raise Exception(f"Invalid colors channels, type: {colors_accessor.type}")
                if colors_accessor.componentType == pygltflib.UNSIGNED_BYTE:
                    colors_t = np.uint8
                elif colors_accessor.componentType == pygltflib.FLOAT:
                    colors_t = np.float32
                else:
                    raise Exception(f"Invalid colors alignment, component_type: {colors_accessor.componentType}")
                colors = np.frombuffer(
                    binary_blob[
                        colors_buffer_view.byteOffset + colors_accessor.byteOffset:
                        colors_buffer_view.byteOffset + colors_buffer_view.byteLength
                    ],
                    dtype=colors_t, count=colors_accessor.count * colors_vec
                ).reshape((-1, colors_vec))
                if colors_t == np.float32:
                    colors = np.round(colors * 255).astype(np.uint8)
                us.logger.debug(f"Colors: {colors.shape}, "
                                f"{colors_buffer_view.byteLength - colors_accessor.byteOffset}")
            else:
                colors = None

            # rebuild mesh and save to .obj file
            points, normals = apply_transform(matrix, points, normals)
            self.objects.append(GLBObject(
                vertices=points,
                faces=triangles,
                vertex_normals=normals,
                vertex_colors=colors,
                uvs=uvs,
                image_texture=color_image,
                metallic_texture=metallic_image,
                roughness_texture=roughness_image
            ))
            
    def obj_count(self):
        return len(self.objects)

    def get_object(self, index=0):
        return self.objects[index]
    
    def export_object(self, index=0):
        object_dir = self.filename + '.objects'
        os.makedirs(object_dir, exist_ok=True)
        obj = self.objects[index]
        obj_file = os.path.join(object_dir, f"object_{index}.obj")
        us.logger.info(f"Export mesh index {index} to: {obj_file}")
        mesh = trimesh.Trimesh(
            vertices=obj.vertices,
            faces=obj.faces,
            vertex_normals=obj.vertex_normals,
            vertex_colors=obj.vertex_colors
        )

        # Metallic and roughness will be discarded
        if obj.image_texture is not None:
            us.logger.debug(f"Image Texture")
            mesh.visual = trimesh.visual.texture.TextureVisuals(uv=obj.uvs, image=obj.image_texture)
        else:
            us.logger.debug(f"Color Texture")
            mesh.visual.uv = obj.uvs
            # visuals = trimesh.visual.color.ColorVisuals(mesh=mesh, vertex_colors=colors)
            # visuals = visuals.to_texture()
            # visuals.uv = texcoords
            # mesh.visual = visuals
        mesh.export(obj_file, file_type="obj", include_color=True)

    def export_texture(self, index=0):
        image_dir = self.filename + '.textures'
        os.makedirs(image_dir, exist_ok=True)
        obj = self.objects[index]
        if obj.image_texture is not None:
            color_image_filename = os.path.join(image_dir, f'color_{index}.png')
            obj.image_texture.save(color_image_filename)
        else:
            color_image_filename = None
    
        if obj.metallic_texture is not None:
            metallic_image_filename = os.path.join(image_dir, f'matallic_{index}.png')
            obj.metallic_texture.save(metallic_image_filename)
        else:
            metallic_image_filename = None
    
        if obj.roughness_texture is not None:
            roughness_image_filename = os.path.join(image_dir, f'roughness_{index}.png')
            obj.roughness_texture.save(roughness_image_filename)
        else:
            roughness_image_filename = None

def uri_to_image(uri):
    image_data = base64.b64decode(uri.split(",")[1])
    return Image.open(BytesIO(image_data)).convert("RGBA")

def apply_transform(matrix, positions, normals=None):
    n = positions.shape[0]
    transformed_positions = (np.hstack([positions, np.ones((n, 1))]) @ matrix)[:, :3]
    if normals is not None:
        transformed_normals = (np.hstack([normals, np.zeros((n, 1))]) @ matrix)[:, :3]
    else:
        transformed_normals = None
    return transformed_positions, transformed_normals

def parse_tree(nodes, node_index):
    node = nodes[node_index]
    if node.matrix is not None:
        matrix = np.array(node.matrix, dtype=np.float32).reshape((4, 4))
    else:
        matrix = np.identity(4, dtype=np.float32)
        if node.translation is not None:
            translation = np.array(node.translation, dtype=np.float32)
            translation_matrix = np.identity(4, dtype=np.float32)
            translation_matrix[3, :3] = translation
            matrix = translation_matrix @ matrix
        if node.rotation is not None:
            rotation = np.array(node.rotation, dtype=np.float32)     # xyzw
            rotation_matrix = np.identity(4, dtype=np.float32)
            rotation = [rotation[3], rotation[0], rotation[1], rotation[2]]
            rotation_matrix[:3, :3] = trimesh.transformations.quaternion_matrix(rotation)[:3, :3].T
            matrix = rotation_matrix @ matrix
        if node.scale is not None:
            scale = np.array(node.scale, dtype=np.float32)
            scale_matrix = np.diag(np.append(scale, 1))
            matrix = scale_matrix @ matrix
    mesh_list = list()
    if node.mesh is not None:
        mesh_list.append([node.mesh, np.identity(4, dtype=np.float32)])
    for sub_node_index in node.children:
        sub_mesh_list = parse_tree(nodes, sub_node_index)
        mesh_list.extend(sub_mesh_list)
    for i in range(len(mesh_list)):
        mesh_list[i][1] = mesh_list[i][1] @ matrix
    return mesh_list

def process_glb_aspose(glb_file):
    from aspose3dcloud import Scene, SaveOptions, FileFormat
    # Load GLB file via the from_file of Scene class
    obj_file = get_obj_filename(glb_file)
    scene = Scene.from_file(glb_file)

    # Call the Scene.save method with OBJ’s format
    scene.save(obj_file, SaveOptions(FileFormat.WAVEFRONTOBJ))

def process_glb_trimesh(glb_file):
    obj_file = get_obj_filename(glb_file)
    scene = trimesh.load(glb_file)

    trimesh.exchange.export.export_mesh(scene, obj_file)
    
def get_obj_filename(glb_file, suffix=""):
    us.logger.debug(f"Converting file: {glb_file} {os.path.exists(glb_file)}")
    filename, extension = os.path.splitext(glb_file)
    # if not extension.lower().endswith('.glb'):
    #     raise Exception("Not glb file")
    obj_file = f"{filename}_{suffix}.obj"
    return obj_file

def get_png_pic(dir_name, file_name, suffix):
    filename = os.path.split(file_name)[1]
    prefix = os.path.splitext(filename)[0]
    png_pic = os.path.join(dir_name, f"{prefix}_{suffix}.png")
    return png_pic