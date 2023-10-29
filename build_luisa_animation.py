import os
import argparse
import subprocess
from process_image import write_gif, write_mp4, read_png

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--renderer_path", type=str,
        default="./ext/LuisaRender/build/bin/luisa-render-pipe-render")
    parser.add_argument("--output_dir", type=str, default=None)
    parser.add_argument("--scripts_dir", type=str, default=None)
    parser.add_argument("--script_path", type=str, default=None)
    parser.add_argument("--script_mark", type=str, default=None)
    parser.add_argument("--fps", type=int, default=60)
    parser.add_argument("--image_scale", type=float, default=1.0)
    parser.add_argument("--render_mp4", action="store_true", default=False)
    parser.add_argument("--no_render", action="store_true", default=False)
    parser.add_argument("--no_zero", action="store_true", default=False)
    args = parser.parse_args()

    if args.scripts_dir is not None and args.script_mark is not None:
        files = os.listdir(args.scripts_dir)
        files = [file for file in files if file.endswith(".luisa")]
        file_marks = [file[file.find("_") + 1: file.find(".")] for file in files]
        idx = [i for i in range(len(file_marks))]
        idx.sort(key=lambda x: int(file_marks[x]))
        pngs = list()
        mark_start = 1 if args.no_zero else 0
        for i in range(mark_start, len(file_marks)):
            real_mark = f"{args.script_mark}_{file_marks[idx[i]]}"
            if not args.no_render:
            # if not True:
                command = [
                    args.renderer_path,
                    f"-b CUDA",
                    f"-o \"{args.output_dir}\"",
                    f"-m {real_mark}",
                    f"-r",
                    f"\"{os.path.join(args.scripts_dir, files[idx[i]])}\"",
                ]
                print(" ".join(command))
                result = subprocess.run(command)
            real_img = os.path.join(args.output_dir, f"image_{real_mark}.png")
            if os.path.exists(real_img):
                pngs.append(real_img)
        imgs = [read_png(png) for png in pngs]
        if args.render_mp4:
            mp4_file = os.path.join(args.output_dir, f"{args.script_mark}.mp4")
            write_mp4(imgs, mp4_file, fps=args.fps, scale=args.image_scale)
        else:
            gif_file = os.path.join(args.output_dir, f"{args.script_mark}.gif")
            write_gif(imgs, gif_file, fps=args.fps)
        
    elif args.script_path is not None and args.script_mark is not None:
        command = [
            args.renderer_path,
            f"-b CUDA",
            f"-o \"{args.output_dir}\"",
            f"-m {args.script_mark}",
            f"-r",
            f"\"{args.script_path}\"",
        ]
        print(" ".join(command))
        result = subprocess.run(command)
    else:
        raise Exception("No script specified!")
