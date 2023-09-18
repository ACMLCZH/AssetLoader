import os
import numpy as np
import argparse
import trimesh

zup_tag = "ZUP"

def export_without_mtl(mesh, path: str, add_zup: bool = False):
    obj_str = trimesh.exchange.obj.export_obj(
        mesh, include_color=True, include_texture=True, write_texture=False
    )
    obj_list = obj_str.split("\n")
    obj_list = [s for s in obj_list if not s.startswith("usemtl") and 
                                       not s.startswith("mtllib") and 
                                       not s.startswith("#")]
    if add_zup:
        obj_list = [f"# {zup_tag}"] + obj_list
    obj_str = "\n".join(obj_list)
    fw = open(path, "w")
    fw.write(obj_str)
    fw.close()

def fix_zup(filename):
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('#'):
                if line.strip() == f"# {zup_tag}":
                    return

    print(f"Convert {filename} to be z-up")
    
    mesh = trimesh.load_mesh(filename, skip_material=True)
    vertices = mesh.vertices.copy()
    vertices[:, 1], vertices[:, 2] = -mesh.vertices[:, 2], mesh.vertices[:, 1]
    normals = mesh.vertex_normals.copy()
    normals[:, 1], normals[:, 2] = -mesh.vertex_normals[:, 2], mesh.vertex_normals[:, 1]
    mesh.vertices = vertices
    mesh.vertex_normals = normals
    export_without_mtl(mesh, filename, add_zup=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check_all_models", action="store_true", default=False)
    parser.add_argument("--path", type=str, default=None)
    args = parser.parse_args()

    # test_file = "./assets/models/glb/eraser.glb"
    if args.check_all_models:
        walks = os.walk("./assets/models/")
        for dir_path, dirnames, filenames in walks:
            for filename in filenames:
                if filename.endswith(".obj"):
                    file_path = os.path.join(dir_path, filename)
                    fix_zup(file_path)
    else:
        file_path = args.path
        fix_zup(file_path)