import os
import argparse
from pathlib import Path
import concurrent.futures
from tqdm import tqdm
import rembg
from PIL import Image
import numpy as np

class SmartBgRemover:
    def __init__(self, model_name="u2net"):
        """Initialize the background remover with specified model."""
        self.model_name = model_name
        self.session = rembg.new_session(model_name=model_name)
    
    def remove_background(self, input_path, output_path=None, alpha_matting=False, 
                          alpha_matting_foreground_threshold=240,
                          alpha_matting_background_threshold=10,
                          alpha_matting_erode_size=10):
        """Remove background from a single image."""
        # Determine output path if not provided
        if output_path is None:
            input_path = Path(input_path)
            output_path = input_path.parent / f"{input_path.stem}_nobg{input_path.suffix}"
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Open the image
        try:
            img = Image.open(input_path)
            
            # Process the image
            output = rembg.remove(
                img, 
                session=self.session,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=alpha_matting_background_threshold,
                alpha_matting_erode_size=alpha_matting_erode_size
            )
            
            # Save the result
            output.save(output_path)
            return True, output_path
        except Exception as e:
            return False, f"Error processing {input_path}: {str(e)}"
    
    def process_batch(self, input_paths, output_dir=None, output_suffix="_nobg", 
                      max_workers=None, **kwargs):
        """Process multiple images in parallel."""
        results = []
        
        # Create output directory if specified
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Process images in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            for input_path in input_paths:
                input_path = Path(input_path)
                
                # Determine output path
                if output_dir:
                    output_path = Path(output_dir) / f"{input_path.stem}{output_suffix}{input_path.suffix}"
                else:
                    output_path = input_path.parent / f"{input_path.stem}{output_suffix}{input_path.suffix}"
                
                # Submit task to executor
                future = executor.submit(
                    self.remove_background, 
                    str(input_path), 
                    str(output_path),
                    **kwargs
                )
                futures.append((future, input_path))
            
            # Process results with progress bar
            for future, input_path in tqdm(futures, desc="Removing backgrounds"):
                success, result = future.result()
                results.append({
                    "input": str(input_path),
                    "success": success,
                    "result": result
                })
        
        return results

def find_image_files(paths):
    """Find all image files in the given paths."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for path in paths:
        path = Path(path)
        if path.is_file() and path.suffix.lower() in image_extensions:
            image_files.append(str(path))
        elif path.is_dir():
            for img_path in path.glob('**/*'):
                if img_path.is_file() and img_path.suffix.lower() in image_extensions:
                    image_files.append(str(img_path))
    
    return image_files

def main():
    parser = argparse.ArgumentParser(description="Smart Background Remover")
    parser.add_argument("inputs", nargs="+", help="Input image files or directories")
    parser.add_argument("-o", "--output-dir", help="Output directory for processed images")
    parser.add_argument("-s", "--suffix", default="_nobg", help="Suffix to add to output filenames")
    parser.add_argument("-m", "--model", default="u2net", 
                        choices=["u2net", "u2netp", "u2net_human_seg", "silueta"],
                        help="Model to use for background removal")
    parser.add_argument("-a", "--alpha-matting", action="store_true", 
                        help="Enable alpha matting for better edge detection")
    parser.add_argument("--workers", type=int, default=None, 
                        help="Number of worker threads (defaults to CPU count)")
    
    args = parser.parse_args()
    
    # Find all image files in the input paths
    image_files = find_image_files(args.inputs)
    
    if not image_files:
        print("No image files found in the specified paths.")
        return
    
    print(f"Found {len(image_files)} image files to process.")
    
    # Initialize the background remover
    remover = SmartBgRemover(model_name=args.model)
    
    # Process the images
    results = remover.process_batch(
        image_files,
        output_dir=args.output_dir,
        output_suffix=args.suffix,
        max_workers=args.workers,
        alpha_matting=args.alpha_matting
    )
    
    # Print summary
    success_count = sum(1 for r in results if r["success"])
    print(f"\nProcessed {len(results)} images: {success_count} successful, {len(results) - success_count} failed")
    
    # Print failures if any
    failures = [r for r in results if not r["success"]]
    if failures:
        print("\nFailed images:")
        for failure in failures:
            print(f"- {failure['input']}: {failure['result']}")

if __name__ == "__main__":
    main()
