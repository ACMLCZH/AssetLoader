import os
import numpy as np
from PIL import Image
from typing import List

def get_png_filename(exr_file):
    print(f"Converting file: {exr_file} {os.path.exists(exr_file)}")
    filename, extension = os.path.splitext(exr_file)
    if not extension.lower().endswith('.exr'):
        raise Exception("Not exr file")
    png_file = f"{filename}.png"

    return png_file


def exr_to_png_imageio(exr_file):
    import imageio

    png_file = get_png_filename(exr_file)

    imageio.plugins.freeimage.download()
    image = imageio.imread(exr_file, format='EXR-FI')
    image = image[:, :, :3]  # remove alpha channel for jpg conversion
    data = image.astype(image.dtype) / image.max()  # normalize the data to 0 - 1
    data = 255 * data  # Now scale by 255
    rgb_image = data.astype('uint8')
    imageio.imwrite(png_file, rgb_image, format='png')
    return png_file


def exr_to_png_cv(exr_file):
    import cv2

    png_file = get_png_filename(exr_file)

    exr_image = cv2.imread(exr_file, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    tonemap = cv2.createTonemap(gamma=2.2)
    ldr_image = tonemap.process(exr_image)
    ldr_image = np.clip(ldr_image * 255, 0, 255).astype('uint8')
    cv2.imwrite(png_file, ldr_image)
    return png_file


def exr_to_png_openexr(exr_file):
    import OpenEXR
    import Imath
    from PIL import Image

    png_file = get_png_filename(exr_file)

    exr_img = OpenEXR.InputFile(exr_file)
    header = exr_img.header()
    dw = header['dataWindow']
    size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    channels = ['R', 'G', 'B']
    rgb = [np.frombuffer(exr_img.channel(c, pt), dtype=np.float32) for c in channels]
    rgb = [c.reshape(size[1], size[0]) for c in rgb]

    exposure = 0.5
    tonemapped_rgb = [np.clip(np.power(c * np.power(2, exposure), 1 / 2.2), 0, 1) for c in rgb]
    tonemapped_image = np.dstack(tonemapped_rgb)
    tonemapped_image = np.uint8(tonemapped_image * 255)

    Image.fromarray(tonemapped_image).save(png_file)
    return png_file

def read_png(png_file) -> Image.Image:
    frame = Image.open(png_file)
    return frame.copy()

def write_gif(imgs: List[Image.Image], gif_file, fps=60):
    duration = int(1000 / fps)
    imgs[0].save(
        gif_file, format='GIF', append_images=imgs[1:],
        save_all=True, duration=duration, loop=0
    )
    print(f'GIF saved to {gif_file}.')

def write_mp4(imgs: List[Image.Image], mp4_file, fps=60, scale=1.0):
    #  bitrate='50000k', 
    from moviepy.editor import ImageSequenceClip

    imgs_arr = [np.array(img) for img in imgs]
    imgs_clip = ImageSequenceClip(imgs_arr, fps=fps)
    imgs_clip.resize(scale)
    imgs_clip.write_videofile(mp4_file, fps=fps, logger=None)
    print(f'Video saved to {mp4_file}.')

def np_write_png(img_arr: np.ndarray, png_file):
    if img_arr.dtype == np.float32 or img_arr.dtype == np.float64:
        img_arr = np.uint8(img_arr * 255)
    Image.fromarray(img_arr).save(png_file)
    print(f'PNG saved to {png_file}.')

def save_tif(image, image_path):
    from tifffile import imsave

    # Save as TIF - when reading, use "data = imread('file.tif')"
    imsave(image_path, image)
