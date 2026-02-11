# Generation Scripts

This directory contains Python scripts for generating synthetic scam conversations.

## Author

**Carl Lochstampfor**  
Old Dominion University (ODU)

## Files

| File | Purpose |
|------|---------|
| `generate_conversations.py` | Main generation script with multi-agent orchestration |
| `quick_test.py` | Quick validation script to test setup |
| `setup_ollama.py` | Helper script for local model setup |
| `requirements.txt` | Python package dependencies |

## Installation

```bash
# From the repository root
cd scripts

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the `configs/` directory (or copy from `.env.example`):

```bash
# For Anthropic Claude
ANTHROPIC_API_KEY=your-api-key-here

# For OpenAI (optional)
OPENAI_API_KEY=your-api-key-here
```

## Quick Start

### 1. Test Your Setup

```bash
python quick_test.py
```

This will:
- Verify your API key is configured
- Generate 2 test conversations
- Save them to `test_output/`

### 2. Generate Conversations

```bash
python generate_conversations.py \
    --scam_type grandparent \
    --num_conversations 50 \
    --output_dir ../data/grandparent
```

## Command Line Options

```
generate_conversations.py

Required:
  --scam_type TYPE        Scam type to generate
                          Options: grandparent, virtual_kidnapping, medicare,
                                   romance, government_impersonation, investment,
                                   lottery, bank

Optional:
  --num_conversations N   Number of conversations (default: 10)
  --output_dir DIR        Output directory (default: ./generated_conversations)
  --provider PROVIDER     LLM provider: anthropic, openai, ollama (default: anthropic)
  --model MODEL           Specific model name (uses provider default if not set)
  --prompts_dir DIR       Directory containing prompt templates (default: ./prompts)
  --max_turns N           Maximum turns per conversation (default: 20)
  --ollama_url URL        Ollama API URL (default: http://localhost:11434/v1)
```

## Examples

### Generate with Claude (Recommended for Validation)

```bash
python generate_conversations.py \
    --scam_type medicare \
    --num_conversations 100 \
    --provider anthropic \
    --model claude-sonnet-4-20250514
```

### Generate with Local Ollama (Recommended for Bulk)

```bash
# First, ensure Ollama is running with a model
ollama serve
ollama pull llama3.1:70b-instruct-q4_K_M

# Then generate
python generate_conversations.py \
    --scam_type grandparent \
    --num_conversations 500 \
    --provider ollama \
    --model llama3.1:70b-instruct-q4_K_M
```

### Generate All Scam Types

```bash
#!/bin/bash
TYPES=("grandparent" "virtual_kidnapping" "medicare" "romance" \
       "government_impersonation" "investment" "lottery" "bank")

for type in "${TYPES[@]}"; do
    python generate_conversations.py \
        --scam_type $type \
        --num_conversations 300 \
        --output_dir ../data/$type
done
```

## LLM Providers

### Anthropic (Claude)

- **Best for**: Initial validation, high-quality generation
- **Models**: `claude-sonnet-4-20250514` (default), `claude-opus-4-20250514`
- **Cost**: ~$0.10-0.20 per conversation

### OpenAI

- **Best for**: Alternative cloud option
- **Models**: `gpt-4o` (default), `gpt-4o-mini`
- **Cost**: Similar to Anthropic

### Ollama (Local)

- **Best for**: Bulk generation, no API costs
- **Models**: `llama3.1:70b-instruct-q4_K_M`, `qwen2.5:72b-instruct-q4_K_M`
- **Requirements**: GPU with 16GB+ VRAM for 70B models
- **Setup**: Run `python setup_ollama.py` for guided installation

## Output Format

Each conversation is saved as a JSON file:

```json
{
  "conversation_id": "grandparent_20260131_143022_4721",
  "scam_type": "grandparent",
  "attacker_config": {
    "role": "grandchild",
    "emergency_type": "dui_arrest",
    "initial_amount": 8500
  },
  "victim_config": {
    "victim_name": "Dorothy",
    "age": 78,
    "trust_level": "highly_trusting"
  },
  "turns": [
    {"role": "victim", "content": "Hello?", "turn_number": 0},
    {"role": "attacker", "content": "Grandma? It's me...", "turn_number": 1}
  ],
  "outcome": "successful_scam",
  "total_turns": 14,
  "model_used": "claude-sonnet-4-20250514",
  "generation_timestamp": "2026-01-31T14:35:44.123456"
}
```

## Estimated Generation Times

| Provider | Model | Time/Conversation | 2,500 Total |
|----------|-------|-------------------|-------------|
| Anthropic | Claude Sonnet | ~30-60 sec | ~20-40 hours |
| OpenAI | GPT-4o | ~30-60 sec | ~20-40 hours |
| Ollama | Llama 70B Q4 | ~45-90 sec | ~30-60 hours |

## Troubleshooting

### "API key not found"
- Ensure `.env` file exists in `configs/` directory
- Or set environment variable: `export ANTHROPIC_API_KEY=your-key`

### "Module not found"
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Ollama connection refused
- Start Ollama server: `ollama serve`
- Check URL matches your setup

### Conversations too short
- Increase `--max_turns`
- Check victim profiles aren't all "quick_rejection" types

### Rate limiting
- Script includes 1-second delays
- For heavy usage, increase delays or use local models
