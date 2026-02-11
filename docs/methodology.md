# Research Methodology

## Author

**Carl Lochstampfor**  
Old Dominion University (ODU)

## Overview

This document outlines the methodology for generating synthetic social engineering conversation datasets using multi-agent LLM simulation.

## Research Gap

Existing publicly available scam conversation datasets have significant limitations:

1. **Scale**: Most datasets contain only hundreds of conversations
2. **Diversity**: Limited scam types and victim profiles
3. **Outcomes**: Overrepresentation of successful scams, underrepresentation of detection
4. **Privacy**: Real conversations require heavy anonymization
5. **Accessibility**: Telecom companies hold the largest datasets but don't share them

## Our Approach

### Multi-Agent Generation

Unlike single-prompt generation (where one LLM writes an entire conversation), we use two separate LLM instances that take turns:

```
┌─────────────────┐         ┌─────────────────┐
│  Attacker LLM   │ ──────► │   Victim LLM    │
│                 │ ◄────── │                 │
│  - Scam tactics │         │  - Personality  │
│  - Persona      │         │  - Susceptibility│
│  - Goals        │         │  - Background   │
└─────────────────┘         └─────────────────┘
```

**Benefits:**
- More natural turn-taking dynamics
- Realistic resistance and objection patterns
- Emergent conversation flows (not scripted)
- Better handling of edge cases

### Parameterization

Each conversation is generated with randomized parameters:

**Attacker Parameters:**
- Scam type and variant
- Persona (name, claimed role, backstory)
- Tactics (urgency level, emotional manipulation style)
- Payment method and amounts
- Handling of resistance

**Victim Parameters:**
- Demographics (age, gender, living situation)
- Family context (relevant for grandparent/kidnapping scams)
- Personality traits (trust level, emotional tendency)
- Scam awareness level
- Financial situation
- Decision-making style

### Outcome Targeting

We generate conversations with a target distribution of outcomes:

| Outcome | Target % | Selection Criteria |
|---------|----------|-------------------|
| Successful Scam | 20-25% | High trust, low awareness, emotional |
| Partial Compliance | 25-30% | Moderate traits |
| Verification Attempt | 20-25% | Cautious, informed |
| Scam Detected | 15-20% | Skeptical, aware |
| Quick Rejection | 10-15% | Very informed, decisive |

This ensures the dataset is balanced for training detection models.

## Data Quality Considerations

### Realism Factors

- Prompts based on documented scam patterns (FBI, FTC reports)
- Victim profiles reflect actual vulnerable population demographics
- Conversation length varies naturally based on outcome
- Includes realistic elements (hearing difficulties, confusion, family consultation)

### Limitations

- Synthetic conversations may lack some nuances of real interactions
- Cultural and regional variations may be underrepresented
- AI-generated text has detectable patterns
- No actual audio/prosodic features (text only)

## Ethical Framework

### Defensive Purpose

This research is conducted solely for defensive purposes:
- Training scam detection systems
- Developing AI-mediated protection tools
- Understanding social engineering tactics for education

### Safeguards

1. **No novel attacks**: All tactics are already publicly documented
2. **Synthetic data**: No real victim information used
3. **Academic oversight**: Research conducted under faculty supervision
4. **Restricted distribution**: Dataset shared responsibly with researchers

## Validation Strategy

### Phase 1: Prompt Validation
- Generate 50-100 conversations per scam type
- Manual review for realism and quality
- Iterate on prompts based on findings

### Phase 2: Scale Generation
- Generate 300+ conversations per scam type
- Automated quality checks
- Outcome distribution verification

### Phase 3: Model Training
- Train detection models on synthetic data
- Evaluate on held-out synthetic data
- Cross-validate with available real conversation samples

## Future Directions

1. **Multi-modal**: Adding voice synthesis for audio datasets
2. **Interactive**: Real-time detection during simulated calls
3. **Personalization**: Tailored protection based on user profiles
4. **Cross-cultural**: Expanding to non-English scam patterns

## References

[To be populated with academic citations]

- FBI Internet Crime Complaint Center (IC3) Reports
- FTC Consumer Sentinel Network Data
- Academic literature on social engineering
- Existing scam conversation datasets (BothBosu, Zenodo Scam Conversation Corpus)
