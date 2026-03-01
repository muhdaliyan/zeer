"""
Test script to demonstrate image generation handling.
This simulates what happens when Gemini returns an image.
"""

import base64
from src.image_handler import save_images, display_image_in_terminal


def create_test_image():
    """Create a simple test image (1x1 red pixel PNG)."""
    # Minimal PNG file (1x1 red pixel)
    png_data = (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
        b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf'
        b'\xc0\x00\x00\x00\x03\x00\x01\x00\x18\xdd\x8d\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )
    return base64.b64encode(png_data).decode('utf-8')


def test_image_handling():
    """Test the image saving and display functionality."""
    print("🧪 Testing Image Generation Handling\n")
    
    # Simulate a response with generated images
    test_images = [
        {
            "data": create_test_image(),
            "mimeType": "image/png"
        }
    ]
    
    print("📥 Saving test image...")
    saved_paths = save_images(test_images, output_dir="generated_images")
    
    if saved_paths:
        print(f"✅ Successfully saved {len(saved_paths)} image(s)\n")
        
        for path in saved_paths:
            display_image_in_terminal(path)
            print(f"✓ You can view the image at: {path}\n")
    else:
        print("❌ Failed to save images\n")


if __name__ == "__main__":
    test_image_handling()
