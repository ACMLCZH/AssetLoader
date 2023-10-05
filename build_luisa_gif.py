import os
import argparse
import subprocess
from process_image import pngs_to_gif

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--renderer_path", type=str,
        default="./ext/LuisaRender/build/bin/luisa-render-pipe-render")
    parser.add_argument("--output_dir", type=str, default=None)
    parser.add_argument("--scripts_dir", type=str, default=None)
    parser.add_argument("--script_path", type=str, default=None)
    parser.add_argument("--script_mark", type=str, default=None)
    parser.add_argument("--name", type=str, default=None)
    args = parser.parse_args()

    if args.scripts_dir is not None and args.script_mark is not None:
        files = os.listdir(args.scripts_dir)
        flles = [file for file in files if file.endswith(".luisa")]
        file_marks = [file[file.find("_") + 1: file.find(".")] for file in files]
        pngs = list()
        for i in range(len(files)):
            real_mark = f"{args.script_mark}_{file_marks[i]}"
            result = subprocess.run([
                args.renderer_path,
                f"-b CUDA",
                f"-o \"{args.output_dir}\"",
                f"-m {real_mark}",
                f"-r \"{os.path.join(args.script_dir, files[i])}\"",
            ])
            pngs.append(os.path.join(args.output_dir, f"image_{real_mark}.png"))
        pngs_to_gif(pngs, os.path.join(args.output_dir, f"{args.script_mark}.gif"))
        
    elif args.script_path is not None and args.script_mark is not None:
        result = subprocess.run([
            args.renderer_path,
            f"-b CUDA",
            f"-o \"{args.output_dir}\"",
            f"-m {args.script_mark}",
            f"-r \"{args.script_path}\"",
        ], stdout=subprocess.PIPE)
    else:
        raise Exception("No script specified!")
