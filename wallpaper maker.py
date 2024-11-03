from PIL import Image, ImageFilter, ImageDraw
import os
from pathlib import Path
import math

def create_blurred_background(img, target_width, target_height):
    """Create a blurred background that fills the target dimensions"""
    # Create a copy and apply strong blur
    bg = img.copy()
    bg = bg.filter(ImageFilter.GaussianBlur(radius=30))
    
    # Resize to cover the entire background
    bg_aspect = bg.width / bg.height
    target_aspect = target_width / target_height
    
    if bg_aspect > target_aspect:
        new_height = target_height
        new_width = int(new_height * bg_aspect)
    else:
        new_width = target_width
        new_height = int(new_width / bg_aspect)
        
    bg = bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Center crop to target size
    left = (bg.width - target_width) // 2
    top = (bg.height - target_height) // 2
    bg = bg.crop((left, top, left + target_width, top + target_height))
    
    return bg

def create_rounded_corners_mask(size, radius):
    # Create an alpha mask for rounded corners
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw a rounded rectangle
    width, height = size
    draw.rounded_rectangle(
        (0, 0, width-1, height-1),  # -1 to avoid edge artifacts
        radius=radius,
        fill=255
    )
    
    return mask

def process_image(input_path, output_path):
    """Process an image according to the wallpaper rules"""
    TARGET_WIDTH = 1920
    TARGET_HEIGHT = 1080
    SQUARE_SIZE = 500
    
    # Open and convert to RGBA
    img = Image.open(input_path).convert('RGBA')
    aspect_ratio = img.width / img.height
    
    # Create new blank image
    result = Image.new('RGBA', (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))
    
    # Case 1: Already 16:9 at 1920x1080
    if abs(aspect_ratio - (16/9)) < 0.1 and img.width == TARGET_WIDTH and img.height == TARGET_HEIGHT:
        result = img
    
    # Case 2: Portrait (9:16)
    elif abs(aspect_ratio - (9/16)) < 0.1:
        # Create blurred background
        bg = create_blurred_background(img, TARGET_WIDTH, TARGET_HEIGHT)
        
        # Calculate centered position for original image
        new_height = TARGET_HEIGHT
        new_width = int(new_height * aspect_ratio)
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        x_offset = (TARGET_WIDTH - new_width) // 2
        result.paste(bg, (0, 0))
        result.paste(img_resized, (x_offset, 0), img_resized)
    
    # Case 3: Square-ish image
    elif abs(aspect_ratio - 1) < 0.1:
        # Create blurred background
        bg = create_blurred_background(img, TARGET_WIDTH, TARGET_HEIGHT)
        
        # Resize original to 500x500
        img_resized = img.resize((SQUARE_SIZE, SQUARE_SIZE), Image.Resampling.LANCZOS)
        
        # Create rounded corners mask
        mask = create_rounded_corners_mask((SQUARE_SIZE, SQUARE_SIZE), 20)
        
        # Calculate centered position
        x_offset = (TARGET_WIDTH - SQUARE_SIZE) // 2
        y_offset = (TARGET_HEIGHT - SQUARE_SIZE) // 2
        
        result.paste(bg, (0, 0))
        result.paste(img_resized, (x_offset, y_offset), mask)
    
    # Case 4: Other aspect ratios
    else:
        # Create blurred background
        bg = create_blurred_background(img, TARGET_WIDTH, TARGET_HEIGHT)
        
        # Resize image to fit height while maintaining aspect ratio
        new_height = TARGET_HEIGHT
        new_width = int(new_height * aspect_ratio)
        
        if new_width > TARGET_WIDTH:
            new_width = TARGET_WIDTH
            new_height = int(new_width / aspect_ratio)
        
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Create rounded corners mask
        mask = create_rounded_corners_mask((new_width, new_height), 20)
        
        # Calculate centered position
        x_offset = (TARGET_WIDTH - new_width) // 2
        y_offset = (TARGET_HEIGHT - new_height) // 2
        
        result.paste(bg, (0, 0))
        result.paste(img_resized, (x_offset, y_offset), mask)
    
    # Ensure final size is 1920x1080
    result = result.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
    
    # Save as PNG
    result.save(output_path, 'PNG')

def main():
    # Ask user for the import folder
    import_folder = input("Enter the path to the folder containing the images: ")
    
    # Define export folder as a "result" subfolder within the import folder
    export_folder = os.path.join(import_folder, "result")
    Path(export_folder).mkdir(parents=True, exist_ok=True)
    
    # Process all images in import folder
    for filename in os.listdir(import_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_path = os.path.join(import_folder, filename)
            output_path = os.path.join(export_folder, f"{Path(filename).stem}.png")
            try:
                process_image(input_path, output_path)
                print(f"Processed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    main()
