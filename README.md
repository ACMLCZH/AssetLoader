# AssetLoader
A storage and processing project of textures and models mainly for LuisaRender use.

### Dependencies building
```
conda install -c conda-forge openexr-python
pip install Pillow scipy trimesh
```

### Processing EXR image

In LuisaRender, some compression types of exr images are not supported by tinyexr, like DWAA. So we should ensure all exr image textures in our storage use supported compression type, such as ZIP, ZIPS, PIZ. Here we use PIZ for loading efficiency.

You can run the script to convert all the textures in your storage:
```
python process_exr.py --check_all_textures
```

### Processing GLB files

GLB files cannot be directly loaded by LuisaRender. So we should extract meshes and textures from GLB files.

You can run the script to convert extract the meshes and textures in your storage:
```
python process_glb.py --check_all_models
```

### Processing OBJ files

Objects used in Blender are often y-up. So converting y-up meshes to z-up meshes is needed.

You can run the script to convert all the meshes in your storage:
```
python process_obj.py --check_all_models
```