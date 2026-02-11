# Prompt Templates

This directory contains the LLM prompt templates for generating synthetic scam conversations.

## Author

**Carl Lochstampfor**  
Old Dominion University (ODU)

## Overview

Each scam type has two prompt templates:
- **Attacker Prompt**: Instructs the LLM to roleplay as a scammer with specific tactics
- **Victim Prompt**: Instructs the LLM to roleplay as a potential victim with specific characteristics

## Prompt Files

| Scam Type | Attacker Prompt | Victim Prompt |
|-----------|-----------------|---------------|
| Grandparent Scam | `grandparent_scam_attacker_v1.md` | `grandparent_scam_victim_v1.md` |
| Virtual Kidnapping | `virtual_kidnapping_attacker_v1.md` | `virtual_kidnapping_victim_v1.md` |
| Medicare/Health Insurance | `medicare_scam_attacker_v1.md` | `medicare_scam_victim_v1.md` |
| Romance Scam | `romance_scam_attacker_v1.md` | `romance_scam_victim_v1.md` |
| Government Impersonation | `government_impersonation_attacker_v1.md` | `government_impersonation_victim_v1.md` |
| Investment/Cryptocurrency | `investment_scam_attacker_v1.md` | `investment_scam_victim_v1.md` |
| Lottery/Sweepstakes | `lottery_scam_attacker_v1.md` | `lottery_scam_victim_v1.md` |
| Bank/Financial Services | `bank_scam_attacker_v1.md` | `bank_scam_victim_v1.md` |

## Prompt Structure

### Attacker Prompts

Each attacker prompt contains:

1. **Overview**: Description of the scam type and research context
2. **Scammer Profile Parameters**: Configurable persona attributes
   - Role/identity claimed
   - Communication style
   - Backstory elements
3. **Scenario Parameters**: Configurable scam variables
   - Scam variant
   - Payment method and amounts
   - Urgency level
4. **Tactical Instructions**: Specific manipulation techniques
   - Trust building
   - Urgency creation
   - Handling resistance
   - Payment extraction
5. **Example Configurations**: Ready-to-use parameter sets
6. **Conversation Rules**: Behavior guidelines

### Victim Prompts

Each victim prompt contains:

1. **Overview**: Description of the victim role and research context
2. **Victim Profile Parameters**: Configurable demographic attributes
   - Name, age, gender
   - Living situation
   - Family context
3. **Personality Traits**: Susceptibility factors
   - Trust level
   - Scam awareness
   - Emotional tendency
   - Decision-making style
4. **Behavioral Guidelines**: How different profiles should respond
5. **Example Configurations**: Ready-to-use victim profiles
6. **Outcome Distribution**: Target percentages for each outcome type

## Parameterization

Prompts use `{parameter_name}` placeholders that are replaced at generation time. This allows creating diverse conversations from the same template.

Example attacker parameters:
```json
{
  "role": "grandchild",
  "emergency_type": "dui_arrest",
  "initial_amount": 8500,
  "payment_method": "cash_courier",
  "urgency_level": "high"
}
```

Example victim parameters:
```json
{
  "victim_name": "Dorothy",
  "age": 78,
  "trust_level": "highly_trusting",
  "scam_awareness": "unaware",
  "decision_making": "impulsive"
}
```

## Usage

The generation script (`scripts/generate_conversations.py`) loads these prompts, substitutes parameters, and uses them to drive multi-agent conversations.

```python
# Prompts are loaded automatically by the generator
python generate_conversations.py --scam_type grandparent --num_conversations 50
```

## Versioning

Prompts are versioned (v1, v2, etc.) to track improvements:
- `v1`: Initial research version
- Future versions will incorporate learnings from generated data quality

## Extending

To add a new scam type:

1. Create `{scam_type}_attacker_v1.md` with attacker tactics
2. Create `{scam_type}_victim_v1.md` with victim profiles
3. Add configurations to `scripts/generate_conversations.py`
4. Test with `quick_test.py`

## Research Notes

These prompts are based on:
- FBI Internet Crime Complaint Center (IC3) reports
- FTC consumer protection resources
- Academic literature on social engineering
- Publicly documented scam patterns

No novel attack techniques are introduced — all tactics are already publicly known and documented by law enforcement.
