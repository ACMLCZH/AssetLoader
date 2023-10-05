import os
import numpy as np


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


def pngs_to_gif(pngs, gif_file):
    from PIL import Image
    frames = []

    for png_file in pngs:
        with Image.open(png_file) as frame:
            frames.append(frame.copy())

    frames[0].save(
        gif_file, format='GIF', append_images=frames[1:],
        save_all=True, duration=25, loop=0
    )


def save_tif(image, image_path):
    from tifffile import imsave

    # Save as TIF - when reading, use "data = imread('file.tif')"
    imsave(image_path, image)


def save_png(image, image_path):
    from PIL import Image

    if image.dtype == np.float32 or image.dtype == np.float64:
        image = np.uint8(image * 255)
    Image.fromarray(image).save(image_path)