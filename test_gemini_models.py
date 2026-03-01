"""
Quick test script to verify Gemini model fetching.
Run with: python test_gemini_models.py
"""

import asyncio
import os
from src.providers.gemini_provider import GeminiProvider


async def test_fetch_models():
    """Test fetching models from Gemini API."""
    # Get API key from environment
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("Set it with: set GEMINI_API_KEY=your_key_here")
        return
    
    print("🔍 Fetching latest Gemini models from v1beta API...\n")
    
    try:
        provider = GeminiProvider(api_key)
        models = await provider.get_models()
        
        print(f"✅ Found {len(models)} models:\n")
        print("=" * 80)
        
        # Group models by version
        gemini_3_models = [m for m in models if "gemini-3" in m.id.lower()]
        gemini_25_models = [m for m in models if "gemini-2.5" in m.id.lower() or "gemini-2-5" in m.id.lower()]
        gemini_2_models = [m for m in models if "gemini-2.0" in m.id.lower() or ("gemini-2" in m.id.lower() and "2.5" not in m.id.lower())]
        other_models = [m for m in models if m not in gemini_3_models + gemini_25_models + gemini_2_models]
        
        if gemini_3_models:
            print("\n🚀 GEMINI 3.x MODELS:")
            print("-" * 80)
            for model in gemini_3_models:
                print(f"  • {model.name}")
                print(f"    ID: {model.id}")
                if model.context_window:
                    print(f"    Context: {model.context_window:,} tokens")
                print()
        
        if gemini_25_models:
            print("\n⚡ GEMINI 2.5 MODELS:")
            print("-" * 80)
            for model in gemini_25_models:
                print(f"  • {model.name}")
                print(f"    ID: {model.id}")
                if model.context_window:
                    print(f"    Context: {model.context_window:,} tokens")
                print()
        
        if gemini_2_models:
            print("\n📦 GEMINI 2.0 MODELS:")
            print("-" * 80)
            for model in gemini_2_models:
                print(f"  • {model.name}")
                print(f"    ID: {model.id}")
                if model.context_window:
                    print(f"    Context: {model.context_window:,} tokens")
                print()
        
        if other_models:
            print("\n🔧 OTHER MODELS:")
            print("-" * 80)
            for model in other_models:
                print(f"  • {model.name}")
                print(f"    ID: {model.id}")
                if model.context_window:
                    print(f"    Context: {model.context_window:,} tokens")
                print()
        
        print("=" * 80)
        print(f"\n✅ Successfully fetched {len(models)} models from Gemini API")
        print(f"   - Gemini 3.x: {len(gemini_3_models)} models")
        print(f"   - Gemini 2.5: {len(gemini_25_models)} models")
        print(f"   - Gemini 2.0: {len(gemini_2_models)} models")
        print(f"   - Other: {len(other_models)} models")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_fetch_models())
