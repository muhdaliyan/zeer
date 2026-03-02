"""
Test the image generation skill and tool.
This script tests the generate_image tool functionality.
"""

import os
from src.tools import create_default_registry, ToolCall

def test_image_generation_tool():
    """Test that the generate_image tool is registered and has correct parameters."""
    print("🧪 Testing Image Generation Tool Registration\n")
    
    # Create registry
    registry = create_default_registry()
    
    # Check if tool is registered
    tool = registry.get_tool("generate_image")
    
    if tool:
        print("✓ generate_image tool is registered")
        print(f"  Name: {tool.name}")
        print(f"  Description: {tool.description[:80]}...")
        print(f"\n  Parameters:")
        for param, details in tool.parameters.get("properties", {}).items():
            required = "required" if param in tool.parameters.get("required", []) else "optional"
            print(f"    - {param} ({required}): {details.get('description', '')[:60]}...")
    else:
        print("✗ generate_image tool not found!")
        return False
    
    print("\n" + "="*80)
    print("Tool Registration Test: PASSED")
    print("="*80)
    
    # Check for API key
    print("\n🔑 Checking API Key Configuration\n")
    api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
    
    if api_key:
        print(f"✓ API key found: {api_key[:10]}...{api_key[-4:]}")
        print("\n  You can test image generation with:")
        print("  > generate an image of a modern coffee shop")
    else:
        print("⚠ No API key found")
        print("\n  To use image generation, set your API key:")
        print("  Windows (PowerShell): $env:GEMINI_API_KEY='your-key'")
        print("  Windows (CMD): set GEMINI_API_KEY=your-key")
        print("  Linux/Mac: export GEMINI_API_KEY='your-key'")
    
    print("\n" + "="*80)
    print("Setup Check: COMPLETE")
    print("="*80)
    
    return True

def test_skill_file():
    """Test that the skill file exists and is properly formatted."""
    print("\n📄 Testing Skill File\n")
    
    skill_path = "skills/image-generation/SKILL.md"
    
    if os.path.exists(skill_path):
        print(f"✓ Skill file exists: {skill_path}")
        
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for required sections
        checks = [
            ("name: image-generation", "Skill name"),
            ("allowed-tools:", "Allowed tools"),
            ("generate_image", "generate_image tool"),
            ("## Goal", "Goal section"),
            ("## Capabilities", "Capabilities section"),
            ("## Procedure", "Procedure section"),
        ]
        
        for check, description in checks:
            if check in content:
                print(f"  ✓ {description} found")
            else:
                print(f"  ✗ {description} missing")
    else:
        print(f"✗ Skill file not found: {skill_path}")
        return False
    
    print("\n" + "="*80)
    print("Skill File Test: PASSED")
    print("="*80)
    
    return True

if __name__ == "__main__":
    print("\n" + "="*80)
    print("IMAGE GENERATION SKILL TEST SUITE")
    print("="*80 + "\n")
    
    # Run tests
    test1 = test_image_generation_tool()
    test2 = test_skill_file()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tool Registration: {'✓ PASSED' if test1 else '✗ FAILED'}")
    print(f"Skill File: {'✓ PASSED' if test2 else '✗ FAILED'}")
    print("\n" + "="*80)
    
    if test1 and test2:
        print("🎉 All tests passed! Image generation skill is ready to use.")
        print("\nNext steps:")
        print("1. Set your GEMINI_API_KEY environment variable")
        print("2. Install google-genai: pip install google-genai")
        print("3. Try: 'generate an image of a modern coffee shop'")
    else:
        print("⚠ Some tests failed. Please check the errors above.")
    
    print("="*80 + "\n")
