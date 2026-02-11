"""
Quick Start Script - Test Generation
=====================================

This script generates a small batch of test conversations to validate
your setup before scaling up. Run this first!

Usage:
    python quick_test.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from generate_conversations import (
    LLMClient, LLMProvider, ConversationGenerator, 
    ScamType, generate_dataset
)


def run_quick_test():
    """Run a quick test to validate the setup."""
    
    print("=" * 60)
    print("SCAM CONVERSATION GENERATOR - QUICK TEST")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found!")
        print("\nTo fix this:")
        print("1. Get your API key from https://console.anthropic.com/")
        print("2. Set it as an environment variable:")
        print("   export ANTHROPIC_API_KEY=your-key-here")
        print("\nOr create a .env file with:")
        print("   ANTHROPIC_API_KEY=your-key-here")
        return False
    
    print("\n✓ API key found")
    
    # Initialize client
    print("\nInitializing Anthropic client...")
    try:
        llm_client = LLMClient(
            provider=LLMProvider.ANTHROPIC,
            model="claude-sonnet-4-20250514"  # Using Sonnet for cost efficiency
        )
        print(f"✓ Using model: {llm_client.model}")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False
    
    # Initialize generator
    prompts_dir = Path(__file__).parent.parent / "prompts"
    print(f"\nLooking for prompts in: {prompts_dir}")
    
    generator = ConversationGenerator(
        llm_client=llm_client,
        prompts_dir=str(prompts_dir),
        max_turns=15  # Shorter for testing
    )
    print("✓ Generator initialized")
    
    # Test generation - just 2 conversations
    print("\n" + "-" * 60)
    print("GENERATING TEST CONVERSATIONS")
    print("-" * 60)
    
    output_dir = Path(__file__).parent / "test_output"
    
    test_configs = [
        (ScamType.GRANDPARENT, "Grandparent Scam"),
        (ScamType.MEDICARE, "Medicare Scam"),
    ]
    
    for scam_type, name in test_configs:
        print(f"\n🔄 Generating 1 {name} conversation...")
        try:
            files = generate_dataset(
                generator=generator,
                scam_type=scam_type,
                num_conversations=1,
                output_dir=str(output_dir / scam_type.value)
            )
            if files:
                print(f"✓ Generated: {files[0]}")
            else:
                print(f"⚠ No files generated for {name}")
        except Exception as e:
            print(f"❌ Error generating {name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print(f"\nCheck the output in: {output_dir}")
    print("\nNext steps:")
    print("1. Review the generated JSON files")
    print("2. Check conversation quality and realism")
    print("3. If satisfied, scale up with more conversations")
    print("\nExample command for larger generation:")
    print("  python generate_conversations.py --scam_type grandparent --num_conversations 50")
    
    return True


if __name__ == "__main__":
    # Try to load .env file
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
            print(f"Loaded environment from {env_path}")
    except ImportError:
        pass
    
    success = run_quick_test()
    sys.exit(0 if success else 1)
