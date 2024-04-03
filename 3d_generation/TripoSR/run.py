import argparse
import logging
import os
import sys
import time
import numpy as np
import torch
from PIL import Image
import rembg

from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground, save_video, to_gradio_3d_orientation

def print_gpu_info():
    print('========================================')
    print('Python interpreter:', sys.executable)
    print('PyTorch version:', torch.__version__)
    print('CUDA Available:', torch.cuda.is_available())
    print('CUDA Device count:', torch.cuda.device_count())
    print('CUDA threads for parallelizing CPU operations:', torch.get_num_threads())
    print('CUDA architectures library was compiled for:', torch.cuda.get_arch_list())
    print('========================================', flush=True)

class Timer:
    def __init__(self):
        self.items = {}
        self.time_scale = 1000.0  # ms
        self.time_unit = "ms"

    def start(self, name: str) -> None:
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        self.items[name] = time.time()
        logging.info(f"{name} ...")

    def end(self, name: str) -> None:
        if name not in self.items:
            return
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        elapsed = (time.time() - self.items.pop(name)) * self.time_scale
        logging.info(f"{name} finished in {elapsed:.2f}{self.time_unit}.")

def main():
    logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

    print_gpu_info()

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, nargs="+", help="Path to input image(s).")
    parser.add_argument("--device", default="cuda:0", type=str, help="Device to use. Defaults to 'cuda:0' if available.")
    parser.add_argument("--pretrained-model-name-or-path", default="stabilityai/TripoSR", type=str, help="Pretrained model path or Hugging Face model ID.")
    parser.add_argument("--chunk-size", default=8192, type=int, help="Chunk size for processing. Smaller values use less VRAM.")
    parser.add_argument("--mc-resolution", default=256, type=int, help="Resolution for the marching cubes algorithm.")
    parser.add_argument("--no-remove-bg", action="store_true", help="Disable automatic background removal.")
    parser.add_argument("--foreground-ratio", default=0.85, type=float, help="Foreground to image size ratio.")
    parser.add_argument("--output-dir", default="output/", type=str, help="Directory to save the output.")
    parser.add_argument("--model-save-format", default="glb", choices=["obj", "glb"], help="Mesh save format.")
    parser.add_argument("--render", action="store_true", help="Render a video from the model output.")
    args = parser.parse_args()

    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    device = args.device if torch.cuda.is_available() else "cpu"

    timer = Timer()
    timer.start("Initializing model")
    model = TSR.from_pretrained(args.pretrained_model_name_or_path, config_name="config.yaml", weight_name="model.ckpt")
    model.renderer.set_chunk_size(args.chunk_size)
    model.to(device)
    timer.end("Initializing model")

    timer.start("Processing images")
    images = []
    if args.no_remove_bg:
        rembg_session = None
    else:
        rembg_session = rembg.new_session()

    for i, image_path in enumerate(args.input):
        if args.no_remove_bg:
            image = np.array(Image.open(image_path).convert("RGB"))
        else:
            image = remove_background(Image.open(image_path), rembg_session)
            image = resize_foreground(image, args.foreground_ratio)
            image = np.array(image).astype(np.float32) / 255.0
            image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
            image = Image.fromarray((image * 255.0).astype(np.uint8))
        if not os.path.exists(os.path.join(output_dir, str(i))):
            os.makedirs(os.path.join(output_dir, str(i)))
        image.save(os.path.join(output_dir, str(i), "input.png"))
        images.append(image)
    timer.end("Processing images")

    for i, image in enumerate(images):
        logging.info(f"Running image {i + 1}/{len(images)} ...")

        timer.start("Running model")
        with torch.no_grad():
            scene_codes = model([image], device=device)
        timer.end("Running model")

        if args.render:
            timer.start("Rendering")
            render_images = model.render(scene_codes, n_views=30, return_type="pil")
            for ri, render_image in enumerate(render_images[0]):
                render_image.save(os.path.join(output_dir, str(i), f"render_{ri:03d}.png"))
            save_video(render_images[0], os.path.join(output_dir, str(i), "render.mp4"), fps=30)
            timer.end("Rendering")

        timer.start("Exporting mesh")
        meshes = model.extract_mesh(scene_codes, resolution=args.mc_resolution)
        meshes[0] = to_gradio_3d_orientation(meshes[0])
        mesh_path = os.path.join(output_dir, str(i), f"mesh.{args.model_save_format}")
        meshes[0].export(mesh_path)
        logging.info(f"Mesh saved to {mesh_path}")
        timer.end("Exporting mesh")

if __name__ == "__main__":
    main()
           
