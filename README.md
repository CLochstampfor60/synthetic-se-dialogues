# Synthetic Social Engineering Dialogues

A research project for generating synthetic multi-turn conversations between social engineering attackers and potential victims. Designed to create training data for scam detection systems that protect vulnerable populations.

## Author

**Carl Lochstampfor**  
Old Dominion University (ODU)  
Department of Cybersecurity

## Project Overview

This project addresses a critical gap in social engineering defense research: the lack of publicly available, diverse conversation datasets for training detection models. Existing datasets are either proprietary (held by telecom companies) or limited in scope.

Our approach uses **multi-agent LLM simulation** to generate realistic scam conversations with:
- Parameterized attacker tactics and personas
- Diverse victim personality profiles
- Multiple conversation outcomes (successful scam, detection, verification, etc.)
- Coverage of 8 major scam categories targeting vulnerable populations

## Scam Categories Covered

| Category | Description | Key Tactics |
|----------|-------------|-------------|
| Grandparent Scam | Impersonating grandchild in emergency | Emotional manipulation, urgency |
| Virtual Kidnapping | Fake kidnapping with AI voice cloning | Terror, ransom demands |
| Medicare/Health Insurance | Fake Medicare representatives | Authority, trust exploitation |
| Romance Scam | Long-term romantic manipulation | Emotional bonding, gradual extraction |
| Government Impersonation | IRS/SSA/law enforcement threats | Fear of legal consequences |
| Investment/Cryptocurrency | Fake investment opportunities | Greed, FOMO, fake profits |
| Lottery/Sweepstakes | Fake prize notifications | Excitement, fee extraction |
| Bank/Financial Services | Fake fraud alerts | Trust in institutions, urgency |

## Repository Structure

```
synthetic-se-dialogues/
├── README.md                       # This file
├── LICENSE
├── .gitignore
│
├── prompts/                        # LLM prompt templates
│   ├── README.md                   # Prompt documentation
│   ├── grandparent_scam_attacker_v1.md
│   ├── grandparent_scam_victim_v1.md
│   ├── virtual_kidnapping_attacker_v1.md
│   ├── virtual_kidnapping_victim_v1.md
│   ├── medicare_scam_attacker_v1.md
│   ├── medicare_scam_victim_v1.md
│   ├── romance_scam_attacker_v1.md
│   ├── romance_scam_victim_v1.md
│   ├── government_impersonation_attacker_v1.md
│   ├── government_impersonation_victim_v1.md
│   ├── investment_scam_attacker_v1.md
│   ├── investment_scam_victim_v1.md
│   ├── lottery_scam_attacker_v1.md
│   ├── lottery_scam_victim_v1.md
│   ├── bank_scam_attacker_v1.md
│   └── bank_scam_victim_v1.md
│
├── scripts/                        # Generation and utility scripts
│   ├── README.md                   # Script documentation
│   ├── generate_conversations.py   # Main generation script
│   ├── quick_test.py              # Quick validation script
│   ├── setup_ollama.py            # Local model setup helper
│   └── requirements.txt           # Python dependencies
│
├── configs/                        # Configuration files
│   └── .env.example               # Environment variable template
│
├── data/                          # Generated datasets
│   ├── README.md                  # Data documentation
│   └── samples/                   # Small sample files for reference
│
└── docs/                          # Additional documentation
    └── methodology.md             # Research methodology notes
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/synthetic-se-dialogues.git
cd synthetic-se-dialogues
```

### 2. Set Up Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r scripts/requirements.txt

# Configure API key
cp configs/.env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run Quick Test

```bash
cd scripts
python quick_test.py
```

### 4. Generate Conversations

```bash
python generate_conversations.py \
    --scam_type grandparent \
    --num_conversations 50 \
    --output_dir ../data/grandparent
```

See [scripts/README.md](scripts/README.md) for detailed usage instructions.

## Methodology

### Multi-Agent Generation

Unlike single-prompt generation, our approach uses two separate LLM instances:

1. **Attacker Agent**: Configured with scam type, tactics, persona, and goals
2. **Victim Agent**: Configured with personality traits, susceptibility factors, and background

The agents take turns generating responses, creating natural conversation dynamics with realistic resistance patterns and outcomes.

### Parameterization

Each conversation is generated with randomized parameters:

**Attacker Parameters:**
- Scam variant and tactics
- Persona (name, role, backstory)
- Payment method and amounts
- Urgency level

**Victim Parameters:**
- Demographics (age, living situation)
- Personality traits (trust level, skepticism)
- Scam awareness level
- Financial situation
- Decision-making style

### Outcome Distribution

Conversations are generated to match realistic outcome distributions:

| Outcome | Target % | Description |
|---------|----------|-------------|
| Successful Scam | 20-25% | Victim complies with scammer |
| Partial Compliance | 25-30% | Victim partially engages |
| Verification Attempt | 20-25% | Victim tries to verify legitimacy |
| Scam Detected | 15-20% | Victim recognizes the scam |
| Quick Rejection | 10-15% | Victim rejects immediately |

## Output Format

Generated conversations are saved as JSON files:

```json
{
  "conversation_id": "grandparent_20260131_143022_4721",
  "scam_type": "grandparent",
  "attacker_config": { ... },
  "victim_config": { ... },
  "turns": [
    {"role": "victim", "content": "Hello?", "turn_number": 0},
    {"role": "attacker", "content": "Grandma? It's me...", "turn_number": 1},
    ...
  ],
  "outcome": "successful_scam",
  "total_turns": 14,
  "model_used": "claude-sonnet-4-20250514",
  "generation_timestamp": "2026-01-31T14:35:44.123456"
}
```

## Ethical Considerations

This research is conducted for **defensive purposes only** — to develop systems that protect vulnerable populations from social engineering attacks.

- Generated conversations are clearly marked as synthetic
- No real personal information is used
- Prompt templates do not provide actionable attack instructions beyond what is publicly documented
- Research conducted under academic supervision at Old Dominion University

## Citation

If you use this dataset or methodology in your research, please cite:

```bibtex
@misc{lochstampfor2026synthetic,
  author = {Lochstampfor, Carl},
  title = {Synthetic Social Engineering Dialogues: A Multi-Agent Approach to Scam Conversation Generation},
  year = {2026},
  institution = {Old Dominion University},
  url = {https://github.com/USERNAME/synthetic-se-dialogues}
}
```

## License

MIT License

## Acknowledgments

- Old Dominion University, Department of Cybersecurity
- Faculty mentor guidance and support: Professor Ayan Roy, PhD (from Christopher Newport University, CNU)
- FBI/FTC public resources on elder fraud patterns

## Contact

Carl Lochstampfor  
Old Dominion University  
