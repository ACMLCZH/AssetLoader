import os

texture_folder = "./assets/textures"
model_folder = "./assets/models"
background_folder = "./assets/backgrounds"

class TextureSource:
    def __init__(
        self,
        texture,
        roughness = None,
        normal = None,
        metallic = None,
        displace = None
    ):
        self.texture = os.path.join(texture_folder, texture)
        self.roughness = None if roughness is None else os.path.join(texture_folder, roughness)
        self.normal = None if normal is None else os.path.join(texture_folder, normal)
        self.metallic = None if metallic is None else os.path.join(texture_folder, metallic)
        self.displace = None if displace is None else os.path.join(texture_folder, displace)

class BackgroundSource:
    def __init__(
        self,
        texture,
    ):
        self.texture = os.path.join(background_folder, texture)

class ModelSource:
    def __init__(
        self,
        object,
        texture,
        roughness = None,
        normal = None,
        metallic = None,
        displace = None
    ):
        self.object = os.path.join(model_folder, object)
        self.texture = os.path.join(model_folder, texture)
        self.roughness = None if roughness is None else os.path.join(model_folder, roughness)
        self.normal = None if normal is None else os.path.join(model_folder, normal)
        self.metallic = None if metallic is None else os.path.join(model_folder, metallic)
        self.displace = None if displace is None else os.path.join(model_folder, displace)


texture_lookup = {
    "dark_wood": TextureSource(
        texture="dark_wood/textures/dark_wood_diff_4k.jpg",
        roughness="dark_wood/textures/dark_wood_rough_4k.exr",
        normal="dark_wood/textures/dark_wood_nor_gl_4k.exr",
        displace="dark_wood/textures/dark_wood_disp_4k.png"
    ),
    
    "fabric_pattern_05": TextureSource(
        texture="fabric_pattern_05/textures/fabric_pattern_05_col_01_4k.png",
        roughness="fabric_pattern_05/textures/fabric_pattern_05_rough_4k.jpg",
        normal="fabric_pattern_05/textures/fabric_pattern_05_nor_gl_4k.exr",
    ),

    "fabric_pattern_07": TextureSource(
        texture="fabric_pattern_07/textures/fabric_pattern_07_col_1_4k.png",
        roughness="fabric_pattern_07/textures/fabric_pattern_07_rough_4k.jpg",
        normal="fabric_pattern_07/textures/fabric_pattern_07_nor_gl_4k.exr",
    ),
    
    "laminate_floor": TextureSource(
        texture="laminate_floor/textures/laminate_floor_diff_4k.jpg",
        roughness="laminate_floor/textures/laminate_floor_rough_4k.exr",
        normal="laminate_floor/textures/laminate_floor_nor_gl_4k.exr",
        displace="laminate_floor/textures/laminate_floor_disp_4k.png"
    ),
    
    "sandy_gravel": TextureSource(
        texture="sandy_gravel/textures/sandy_gravel_diff_4k.jpg",
        roughness="sandy_gravel/textures/sandy_gravel_rough_4k.exr",
        normal="sandy_gravel/textures/sandy_gravel_nor_gl_4k.exr",
        displace="sandy_gravel/textures/sandy_gravel_disp_4k.png"
    ),

    "eraser": TextureSource(
        texture="cube_bake/eraser/Regulated.png"
    ),

    "poker_1": TextureSource(
        texture="both_bake/poker/Poker_1.png"
    ),
    
    "poker_2": TextureSource(
        texture="both_bake/poker/Poker_2.png"
    ),
    
    "poker_3": TextureSource(
        texture="both_bake/poker/Poker_3.png"
    ),

    "postcard_1": TextureSource(
        texture="both_bake/postcard/Postcard_1.png"
    ),
    
    "postcard_2": TextureSource(
        texture="both_bake/postcard/Postcard_2.png"
    ),
}

background_lookup = {
    "sunflowers_puresky": BackgroundSource("sunflowers_puresky_8k.hdr"),
    "brown_photostudio_01": BackgroundSource("brown_photostudio_01_4k.exr"),
    "brown_photostudio_02": BackgroundSource("brown_photostudio_02_4k.exr"),
    "brown_photostudio_07": BackgroundSource("brown_photostudio_07_8k.hdr"),
    "lebombo": BackgroundSource("lebombo_4k.exr"),
}

model_lookup = {
    "wooden_table": ModelSource(
        object="blend/wooden_table/models/wooden_table_02.obj",
        texture="blend/wooden_table/textures/wooden_table_02_diff_4k.jpg",
        roughness="blend/wooden_table/textures/wooden_table_02_rough_4k.jpg",
        normal="blend/wooden_table/textures/wooden_table_02_nor_gl_4k.exr",
        metallic="blend/wooden_table/textures/wooden_table_02_metal_4k.exr",
    ),
}

# up, down, front, back, left, right
cube_corner_uvs = [
    [(0.375, 0.500), (0.125, 0.750)],   # (y, x)
    [(0.625, 0.500), (0.875, 0.750)],
    [(0.625, 0.750), (0.375, 1.000)],   # (z, y)
    [(0.625, 0.500), (0.375, 0.250)],
    [(0.625, 0.250), (0.375, 0.000)],   # (z, x)
    [(0.625, 0.500), (0.375, 0.750)]
]