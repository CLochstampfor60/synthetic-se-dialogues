# Generated Data

This directory contains generated synthetic scam conversation datasets.

## Author

**Carl Lochstampfor**  
Old Dominion University (ODU)

## Directory Structure

```
data/
├── README.md           # This file
├── samples/            # Small sample files (committed to repo)
├── grandparent/        # Generated grandparent scam conversations
├── virtual_kidnapping/ # Generated virtual kidnapping conversations
├── medicare/           # Generated Medicare scam conversations
├── romance/            # Generated romance scam conversations
├── government/         # Generated government impersonation conversations
├── investment/         # Generated investment scam conversations
├── lottery/            # Generated lottery scam conversations
└── bank/               # Generated bank scam conversations
```

## Note on Large Files

Generated conversation files can become large. By default, the `data/` directory (except `samples/`) is excluded from git via `.gitignore`.

For dataset sharing:
- Use Git LFS for large files
- Host on external platforms (Zenodo, Hugging Face Datasets)
- Keep only samples in the repository

## Data Format

Each JSON file contains one conversation:

```json
{
  "conversation_id": "string",
  "scam_type": "string",
  "attacker_config": { },
  "victim_config": { },
  "turns": [
    {
      "role": "victim|attacker",
      "content": "string",
      "turn_number": 0,
      "timestamp": "ISO-8601"
    }
  ],
  "outcome": "successful_scam|partial_compliance|verification_attempt|scam_detected|quick_rejection",
  "total_turns": 14,
  "model_used": "string",
  "generation_timestamp": "ISO-8601"
}
```

## Outcome Categories

| Outcome | Description |
|---------|-------------|
| `successful_scam` | Victim complies with scammer's requests |
| `partial_compliance` | Victim partially engages but doesn't fully comply |
| `verification_attempt` | Victim attempts to verify through official channels |
| `scam_detected` | Victim recognizes and calls out the scam |
| `quick_rejection` | Victim rejects the scammer quickly |

## Usage

### Loading Conversations (Python)

```python
import json
from pathlib import Path

def load_conversations(data_dir):
    """Load all conversations from a directory."""
    conversations = []
    for file in Path(data_dir).glob("*.json"):
        with open(file, 'r') as f:
            conversations.append(json.load(f))
    return conversations

# Example
grandparent_convos = load_conversations("data/grandparent")
print(f"Loaded {len(grandparent_convos)} conversations")
```

### Converting to DataFrame

```python
import pandas as pd

def conversations_to_dataframe(conversations):
    """Convert conversations to a flat DataFrame."""
    rows = []
    for conv in conversations:
        for turn in conv['turns']:
            rows.append({
                'conversation_id': conv['conversation_id'],
                'scam_type': conv['scam_type'],
                'outcome': conv['outcome'],
                'turn_number': turn['turn_number'],
                'role': turn['role'],
                'content': turn['content']
            })
    return pd.DataFrame(rows)

df = conversations_to_dataframe(grandparent_convos)
```

## Samples Directory

The `samples/` directory contains a small number of example conversations that are committed to the repository for reference. These demonstrate the output format and conversation quality.
