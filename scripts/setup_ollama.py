"""
Ollama Setup Script for Local Generation
=========================================

This script helps set up Ollama for local model inference on your
RTX 4080 Super. Use this for bulk generation after validating prompts
with Claude.

Prerequisites:
    1. Install Ollama: https://ollama.ai/download
    2. Ensure CUDA drivers are installed for GPU acceleration
"""

import subprocess
import sys
import time
import os


def run_command(cmd, check=True):
    """Run a shell command and return output."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout


def check_ollama_installed():
    """Check if Ollama is installed."""
    result = run_command("ollama --version", check=False)
    return result is not None and "ollama" in result.lower()


def check_ollama_running():
    """Check if Ollama server is running."""
    try:
        import urllib.request
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
        return True
    except:
        return False


def get_available_models():
    """Get list of downloaded models."""
    result = run_command("ollama list", check=False)
    if result:
        return result
    return "No models found"


def pull_model(model_name):
    """Pull a model from Ollama registry."""
    print(f"\nPulling model: {model_name}")
    print("This may take a while for large models...")
    
    # Use subprocess.Popen for real-time output
    process = subprocess.Popen(
        f"ollama pull {model_name}",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    return process.returncode == 0


def test_model(model_name):
    """Test a model with a simple prompt."""
    print(f"\nTesting model: {model_name}")
    
    test_prompt = "Say 'Hello, I am working correctly!' and nothing else."
    result = run_command(f'ollama run {model_name} "{test_prompt}"', check=False)
    
    if result:
        print(f"Model response: {result[:200]}...")
        return True
    return False


def main():
    print("=" * 60)
    print("OLLAMA SETUP FOR LOCAL SCAM CONVERSATION GENERATION")
    print("=" * 60)
    
    # Check Ollama installation
    print("\n1. Checking Ollama installation...")
    if not check_ollama_installed():
        print("❌ Ollama is not installed!")
        print("\nTo install Ollama:")
        print("  - Windows: Download from https://ollama.ai/download")
        print("  - Linux: curl -fsSL https://ollama.ai/install.sh | sh")
        print("  - macOS: brew install ollama")
        return False
    print("✓ Ollama is installed")
    
    # Check if server is running
    print("\n2. Checking Ollama server...")
    if not check_ollama_running():
        print("⚠ Ollama server is not running")
        print("Starting Ollama server...")
        subprocess.Popen("ollama serve", shell=True, 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        
        if not check_ollama_running():
            print("❌ Failed to start Ollama server")
            print("Try running 'ollama serve' manually in another terminal")
            return False
    print("✓ Ollama server is running")
    
    # Show current models
    print("\n3. Currently downloaded models:")
    print(get_available_models())
    
    # Recommend models for RTX 4080 Super (16GB VRAM)
    print("\n4. Recommended models for RTX 4080 Super (16GB VRAM):")
    print("-" * 50)
    
    recommended_models = [
        ("llama3.1:8b", "Fast, fits easily in VRAM, good for testing"),
        ("llama3.1:70b-instruct-q4_K_M", "Best quality at 4-bit quantization"),
        ("qwen2.5:72b-instruct-q4_K_M", "Alternative to Llama, strong reasoning"),
        ("mistral:7b", "Fast and efficient for simpler tasks"),
    ]
    
    for model, description in recommended_models:
        print(f"  • {model}")
        print(f"    {description}")
    
    # Ask user which model to pull
    print("\n" + "-" * 50)
    print("Which model would you like to download?")
    print("(For your RTX 4080 Super, I recommend llama3.1:70b-instruct-q4_K_M)")
    print("\nOptions:")
    print("  1. llama3.1:8b (fast, ~5GB)")
    print("  2. llama3.1:70b-instruct-q4_K_M (best quality, ~40GB)")
    print("  3. qwen2.5:72b-instruct-q4_K_M (alternative, ~40GB)")
    print("  4. Skip - I'll download manually")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    model_choices = {
        "1": "llama3.1:8b",
        "2": "llama3.1:70b-instruct-q4_K_M",
        "3": "qwen2.5:72b-instruct-q4_K_M",
    }
    
    if choice in model_choices:
        model = model_choices[choice]
        if pull_model(model):
            print(f"\n✓ Successfully pulled {model}")
            
            # Test the model
            print("\n5. Testing the model...")
            if test_model(model):
                print("✓ Model is working correctly!")
            else:
                print("⚠ Model test failed - may still work")
        else:
            print(f"\n❌ Failed to pull {model}")
    else:
        print("\nSkipping model download")
    
    # Print usage instructions
    print("\n" + "=" * 60)
    print("SETUP COMPLETE")
    print("=" * 60)
    
    print("\nTo generate conversations with Ollama:")
    print("-" * 50)
    print("""
# Make sure Ollama is running
ollama serve

# Generate conversations using local model
python generate_conversations.py \\
    --scam_type grandparent \\
    --num_conversations 100 \\
    --provider ollama \\
    --model llama3.1:70b-instruct-q4_K_M \\
    --output_dir ./output/grandparent
""")
    
    print("\nTips for RTX 4080 Super:")
    print("-" * 50)
    print("• 70B models at 4-bit quantization should fit in 16GB VRAM")
    print("• Expect ~45-90 seconds per conversation")
    print("• You can run other light tasks while generating")
    print("• Monitor VRAM usage with: nvidia-smi")
    print("• For faster generation, use 8B models (lower quality)")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
