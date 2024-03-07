import argparse
import logging
import os
import sys
import time
from PIL import Image
import numpy as np
import rembg
import torch

from tsr.system import TSR
from tsr.utils import remove_background, resize_foreground, save_video

# Setup logging configuration
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

# Print environment and GPU information
def print_environment_info():
    logging.info("Environment variables:")
    for key, value in os.environ.items():
        logging.info(f"{key}: {value}")

    logging.info('========================================')
    logging.info(f'Python interpreter: {sys.executable}')
    logging.info(f'PyTorch version: {torch.__version__}')
    logging.info(f'CUDA Available: {torch.cuda.is_available()}')
    logging.info(f'CUDA Device count: {torch.cuda.device_count()}')
    logging.info(f'CUDA threads for parallelizing CPU operations: {torch.get_num_threads()}')
    logging.info(f'CUDA architectures library was compiled for: {torch.cuda.get_arch_list()}')
    logging.info('========================================')

print_environment_info()

class Timer:
    def __init__(self):
        self.start_times = {}

    def start(self, name: str):
        self.start_times[name] = time.time()

    def end(self, name: str):
        if name in self.start_times:
            elapsed_time = time.time() - self.start_times[name]
            logging.info(f"{name} finished in {elapsed_time * 1000:.2f}ms.")
            del self.start_times[name]

timer = Timer()

def process_image(image_path, remove_bg=True, foreground_ratio=0.85):
    image = Image.open(image_path).convert("RGB")
    if remove_bg:
        rembg_session = rembg.new_session()
        image = remove_background(image, rembg_session)
        image = resize_foreground(image, foreground_ratio)
    image = np.array(image).astype(np.float32) / 255.0
    image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5  # Blend with grey background
    return Image.fromarray((image * 255.0).astype(np.uint8))

def main(args):
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)

    device = args.device if torch.cuda.is_available() else "cpu"

    timer.start("Initializing model")
    model = TSR.from_pretrained(args.pretrained_model_name_or_path, config_name="config.yaml", weight_name="model.ckpt")
    model.renderer.set_chunk_size(args.chunk_size)
    model.to(device)
    timer.end("Initializing model")

    for i, image_path in enumerate(args.image):
        timer.start(f"Processing image {i+1}")
        processed_image = process_image(image_path, not args.no_remove_bg, args.foreground_ratio)
        processed_image_path = os.path.join(output_dir, f"processed_{i}.png")
        processed_image.save(processed_image_path)
        timer.end(f"Processing image {i+1}")

        timer.start(f"Running model on image {i+1}")
        with torch.no_grad():
            scene_codes = model([np.array(processed_image).astype(np.float32) / 255.0], device=device)
        timer.end(f"Running model on image {i+1}")

        timer.start(f"Exporting mesh for image {i+1}")
        meshes = model.extract_mesh(scene_codes, resolution=args.mc_resolution)
        mesh_export_path = os.path.join(output_dir, f"mesh_{i}.{args.model_save_format}")
        meshes[0].export(mesh_export_path, file_type=args.model_save_format)
        timer.end(f"Exporting mesh for image {i+1}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run TSR model on input images.")
    parser.add_argument("image", type=str, nargs="+", help="Path to input image(s).")
    parser.add_argument("--device", default="cuda:0", type=str, help="Device to use. Defaults to 'cuda:0', falls back to 'cpu' if CUDA is not available.")
    parser.add_argument("--pretrained-model-name-or-path", default="stabilityai/TripoSR", type=str, help="Pretrained model identifier or file path.")
    parser.add_argument("--chunk-size", default=8192, type=int, help="Evaluation chunk size for rendering. Defaults to 8192.")
    parser.add_argument("--mc-resolution", default=256, type=int, help="Resolution for marching cubes algorithm. Defaults to 256.")
    parser.add_argument("--no-remove-bg", action="store_true", help="Don't remove background from input images.")
    parser.add_argument("--foreground-ratio", default=0.85, type=float, help="Foreground ratio for resizing foreground. Defaults to 0.85.")
    parser.add_argument("--output-dir", default="output/", type=str, help="Directory to save the output. Defaults to 'output/'.")
    parser.add_argument("--model-save-format", default="obj", choices=["obj", "glb"], type=str, help="Format for saving the model. Supports 'obj' and 'glb'. Defaults to 'obj'.")
    args = parser.parse_args()

    main(args)