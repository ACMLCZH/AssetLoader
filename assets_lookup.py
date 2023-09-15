import os

texture_folder = "./assets/textures"
model_folder = "./assets/models"

class TextureSource:
    def __init__(
        self,
        texture,
        roughness,
        normal,
        displace = None
    ):
        self.texture = os.path.join(texture_folder, texture)
        self.roughness = os.path.join(texture_folder, roughness)
        self.normal = os.path.join(texture_folder, normal)
        if displace is None:
            self.displace = None
        else:
            self.displace = os.path.join(texture_folder, displace)

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
}