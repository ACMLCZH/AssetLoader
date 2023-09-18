import OpenEXR
import Imath
import argparse
import os

# Imath.Compression.NO_COMPRESSION: No compression
# Imath.Compression.RLE_COMPRESSION: Run Length Encoding (RLE)
# Imath.Compression.ZIPS_COMPRESSION: ZIP, single scanline
# Imath.Compression.ZIP_COMPRESSION: ZIP, multiple scanlines
# Imath.Compression.PIZ_COMPRESSION: PIZ-based wavelet compression
# Imath.Compression.PXR24_COMPRESSION: PXR24 compression
# Imath.Compression.B44_COMPRESSION: B44 compression
# Imath.Compression.B44A_COMPRESSION: B44A compression
# Imath.Compression.DWAA_COMPRESSION: DWAA compression
# Imath.Compression.DWAB_COMPRESSION: DWAB compression
def change_compression_type(filename, new_type):
    input_file = OpenEXR.InputFile(filename)
    header = input_file.header()
    old_comp = header['compression']
    if old_comp.v == new_type:
        return
    
    new_comp = Imath.Compression(new_type)
    print(f"Change {filename}'s compression type from {old_comp} to {new_comp}")
    pixels = { c: input_file.channel(c) for c in header["channels"] }
    input_file.close()
    header['compression'] = new_comp
    output_file = OpenEXR.OutputFile(filename, header)
    output_file.writePixels(pixels)
    output_file.close()
    # print(type(compression_type), compression_type, DWAA_COMPRESSION)
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check_all_textures", action="store_true", default=False)
    parser.add_argument("--check_all_models", action="store_true", default=False)
    parser.add_argument("--path", type=str, default=None)
    args = parser.parse_args()
    
    # test_file = "./assets/textures/fabric_pattern_05/textures/fabric_pattern_05_nor_gl_4k.exr"
    if args.check_all_textures or args.check_all_models:
        if args.check_all_textures:
            walks = os.walk("./assets/textures/")
        else:
            walks = os.walk("./assets/models/")
        for dir_path, dirnames, filenames in walks:
            for filename in filenames:
                if filename.endswith(".exr"):
                    file_path = os.path.join(dir_path, filename)
                    change_compression_type(file_path, Imath.Compression.PIZ_COMPRESSION)
			# relative_dirpath = dirpath[len(root_dir):]
    else:
        file_path = args.path
        change_compression_type(file_path, Imath.Compression.PIZ_COMPRESSION)