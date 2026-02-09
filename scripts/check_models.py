#!/usr/bin/env python3
"""
Helper script to check available Whisper models and prevent unwanted downloads.
"""

import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from transcriber import SpeechTranscriber


def main():
    print("🔍 Checking available Whisper models...")
    print("=" * 50)

    # List available models
    available = SpeechTranscriber.list_available_models()

    if not available:
        print("❌ No models found in cache (~/.cache/whisper/)")
        print("You need to download models first.")
        return

    print("✅ Available models:")
    for model_name, size in available:
        print(f"  • {model_name}: {size}")

    print("\n🎯 Recommended for development:")
    for model_name, size in available:
        if model_name in ["tiny", "base"]:
            print(f"  ✓ {model_name}: {size} (fast loading)")

    print(f"\n📁 Cache location: ~/.cache/whisper/")

    # Test specific models
    test_models = ["tiny", "base", "small"]
    print(f"\n🧪 Testing model availability:")

    for model in test_models:
        available = SpeechTranscriber.check_model_available(model)
        status = "✅ Available" if available else "❌ Missing"
        print(f"  {model}: {status}")


if __name__ == "__main__":
    main()
