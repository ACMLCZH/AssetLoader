# AssetLoader
A storage and processing project of textures and models mainly for LuisaRender use.

### Dependencies building
```
conda install -c conda-forge openexr-python
```

### Processing EXR image

 In LuisaRender, some compression types of exr images are not supported by tinyexr, like DWAA. So we should ensure all exr image textures in our storage use supported compression type, such as ZIP, ZIPS, PIZ. Here we use PIZ for loading efficiency.

You can run the script to convert all the texture in your storage:
```
python process_exr.py --check_all_textures
```