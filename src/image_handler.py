"""
Image handling utilities for zeer CLI.
Handles saving and displaying generated images.
"""

import os
import base64
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


def save_images(images: List[Dict[str, Any]], output_dir: str = "generated_images") -> List[str]:
    """
    Save generated images to disk.
    
    Args:
        images: List of image dictionaries with 'data' (base64) and 'mimeType'
        output_dir: Directory to save images (default: 'generated_images')
        
    Returns:
        List of saved file paths
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for idx, image in enumerate(images, 1):
        # Get image data and mime type
        image_data = image.get("data", "")
        mime_type = image.get("mimeType", "image/png")
        
        # Determine file extension from mime type
        extension = mime_type.split("/")[-1]
        if extension == "jpeg":
            extension = "jpg"
        
        # Generate filename
        filename = f"image_{timestamp}_{idx}.{extension}"
        filepath = os.path.join(output_dir, filename)
        
        # Decode and save image
        try:
            image_bytes = base64.b64decode(image_data)
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            saved_paths.append(filepath)
        except Exception as e:
            print(f"Error saving image {idx}: {str(e)}")
    
    return saved_paths


def display_image_in_terminal(filepath: str, max_width: int = 80) -> None:
    """
    Display image information in terminal with box style.
    
    Args:
        filepath: Path to the image file
        max_width: Maximum width for display
    """
    from colorama import Fore, Style
    import shutil
    
    # Get terminal width
    term_width = shutil.get_terminal_size().columns
    max_width = min(term_width - 2, 80)
    
    # Get file size
    file_size = os.path.getsize(filepath)
    size_kb = file_size / 1024
    
    # Create header
    header = "─ Image Generated "
    print(f"{Fore.CYAN}╭{header}{'─' * (max_width - len(header) - 1)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Path:{Style.RESET_ALL} {Fore.YELLOW}{filepath}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}│{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Size:{Style.RESET_ALL} {size_kb:.1f} KB")
    print()
