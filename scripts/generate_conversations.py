"""
Social Engineering Scam Conversation Generator
==============================================

This script generates synthetic multi-turn conversations between scammer and victim
agents using LLM APIs. Designed for academic research on scam detection.

Author: [Your Name]
Project: AI-Powered Social Engineering Defense System
Date: January 2026

Usage:
    python generate_conversations.py --scam_type grandparent --num_conversations 10 --output_dir ./output
    
Requirements:
    pip install anthropic openai python-dotenv tqdm
"""

import os
import json
import random
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import time

# Third-party imports
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("Warning: anthropic package not installed. Install with: pip install anthropic")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: openai package not installed. Install with: pip install openai")

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Warning: tqdm not installed. Progress bars disabled. Install with: pip install tqdm")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using environment variables directly.")


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class ScamType(Enum):
    GRANDPARENT = "grandparent"
    VIRTUAL_KIDNAPPING = "virtual_kidnapping"
    MEDICARE = "medicare"
    ROMANCE = "romance"
    GOVERNMENT_IMPERSONATION = "government_impersonation"
    INVESTMENT = "investment"
    LOTTERY = "lottery"
    BANK = "bank"


class ConversationOutcome(Enum):
    SUCCESSFUL_SCAM = "successful_scam"  # Victim complies fully
    PARTIAL_COMPLIANCE = "partial_compliance"  # Victim partially complies
    VERIFICATION_ATTEMPT = "verification_attempt"  # Victim tries to verify
    SCAM_DETECTED = "scam_detected"  # Victim recognizes scam
    QUICK_REJECTION = "quick_rejection"  # Victim rejects immediately


class LLMProvider(Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"  # For local models


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    role: str  # "attacker" or "victim"
    content: str
    timestamp: str
    turn_number: int


@dataclass
class GeneratedConversation:
    """Represents a complete generated conversation."""
    conversation_id: str
    scam_type: str
    attacker_config: Dict[str, Any]
    victim_config: Dict[str, Any]
    turns: List[ConversationTurn]
    outcome: str
    metadata: Dict[str, Any]
    generation_timestamp: str
    model_used: str
    total_turns: int


# =============================================================================
# NAME POOLS FOR REALISTIC GENERATION
# =============================================================================

MALE_GRANDCHILD_NAMES = [
    "Michael", "David", "Jason", "Christopher", "Brian", "Kevin", "Matthew",
    "Ryan", "Joshua", "Andrew", "Daniel", "James", "Tyler", "Brandon", "Justin"
]

FEMALE_GRANDCHILD_NAMES = [
    "Jennifer", "Emily", "Amanda", "Jessica", "Ashley", "Sarah", "Stephanie",
    "Nicole", "Melissa", "Michelle", "Elizabeth", "Lauren", "Megan", "Rachel", "Samantha"
]

MALE_VICTIM_NAMES = [
    "Robert", "William", "Richard", "Donald", "George", "Charles", "Frank",
    "Harold", "Raymond", "Eugene", "Gerald", "Walter", "Henry", "Arthur"
]

FEMALE_VICTIM_NAMES = [
    "Dorothy", "Margaret", "Barbara", "Patricia", "Helen", "Betty", "Ruth",
    "Shirley", "Virginia", "Evelyn", "Gloria", "Joyce", "Marilyn", "Frances"
]

LAWYER_NAMES = [
    "Michael Stevens", "David Thompson", "Robert Williams", "James Mitchell",
    "Richard Anderson", "Thomas Reynolds", "William Morrison", "John Patterson"
]


# =============================================================================
# ATTACKER KNOWLEDGE LEVELS
# =============================================================================
# Determines how much info the attacker has before the call

ATTACKER_KNOWLEDGE_LEVELS = {
    "none": {
        "description": "Cold call - knows nothing, must fish for all info",
        "knows_victim_name": False,
        "knows_grandchild_name": False,
        "knows_grandchild_gender": False,
        "weight": 0.50  # 50% of calls are cold
    },
    "partial": {
        "description": "Has victim name from data breach or phonebook",
        "knows_victim_name": True,
        "knows_grandchild_name": False,
        "knows_grandchild_gender": False,
        "weight": 0.30  # 30% have partial info
    },
    "full": {
        "description": "Researched target - has family info from social media",
        "knows_victim_name": True,
        "knows_grandchild_name": True,
        "knows_grandchild_gender": True,
        "weight": 0.20  # 20% are targeted/researched
    }
}


def select_attacker_knowledge_level() -> str:
    """Randomly select attacker knowledge level based on realistic weights."""
    levels = list(ATTACKER_KNOWLEDGE_LEVELS.keys())
    weights = [ATTACKER_KNOWLEDGE_LEVELS[l]["weight"] for l in levels]
    return random.choices(levels, weights=weights)[0]


def get_grandchild_name_for_gender(gender: str) -> str:
    """Get a random grandchild name matching the specified gender."""
    if gender == "male":
        return random.choice(MALE_GRANDCHILD_NAMES)
    else:
        return random.choice(FEMALE_GRANDCHILD_NAMES)


def generate_grandchildren_list() -> List[Dict[str, str]]:
    """Generate a realistic list of grandchildren with names and genders."""
    num_grandchildren = random.choices([1, 2, 3, 4], weights=[0.2, 0.4, 0.3, 0.1])[0]
    grandchildren = []
    for _ in range(num_grandchildren):
        gender = random.choice(["male", "female"])
        name = get_grandchild_name_for_gender(gender)
        grandchildren.append({"name": name, "gender": gender})
    return grandchildren


# =============================================================================
# CONFIGURATION TEMPLATES
# =============================================================================

ATTACKER_CONFIGS = {
    ScamType.GRANDPARENT: [
        {
            "role": "grandchild",
            "claimed_gender": "male",  # Will pretend to be grandson
            "scammer_persona_name": None,  # Uses grandchild's name or fishes for it
            "speech_pattern": "distressed_crying",
            "emergency_type": "dui_arrest",
            "location": "county jail downtown",
            "initial_amount": 8500,
            "floor_amount": 3000,
            "payment_method": "cash_courier",
            "urgency_level": "high"
        },
        {
            "role": "grandchild",
            "claimed_gender": "female",  # Will pretend to be granddaughter
            "scammer_persona_name": None,
            "speech_pattern": "distressed_crying",
            "emergency_type": "car_accident_at_fault",
            "location": "hospital emergency room",
            "initial_amount": 6000,
            "floor_amount": 2500,
            "payment_method": "gift_cards",
            "urgency_level": "high"
        },
        {
            "role": "lawyer",
            "claimed_gender": None,  # Lawyer doesn't claim to be grandchild
            "scammer_persona_name": None,  # Will be filled from LAWYER_NAMES
            "speech_pattern": "formal_professional",
            "emergency_type": "car_accident_at_fault",
            "location": "county courthouse",
            "initial_amount": 12000,
            "floor_amount": 5000,
            "payment_method": "wire_transfer",
            "urgency_level": "moderate"
        },
        {
            "role": "grandchild",
            "claimed_gender": "male",
            "scammer_persona_name": None,
            "speech_pattern": "distressed_crying",
            "emergency_type": "stranded_abroad",
            "location": "Mexico",
            "initial_amount": 4000,
            "floor_amount": 1500,
            "payment_method": "wire_transfer",
            "urgency_level": "extreme"
        },
        {
            "role": "bail_bondsman",
            "claimed_gender": None,
            "scammer_persona_name": None,
            "speech_pattern": "professional_urgent",
            "emergency_type": "dui_arrest",
            "location": "county detention center",
            "initial_amount": 9500,
            "floor_amount": 4000,
            "payment_method": "cash_courier",
            "urgency_level": "high"
        },
    ],
    ScamType.VIRTUAL_KIDNAPPING: [
        {
            "role": "kidnapper_direct",
            "voice_tone": "cold_menacing",
            "organization": "cartel",
            "claimed_victim_relationship": "daughter",
            "situation": "kidnapped_for_ransom",
            "location": "Mexico",
            "initial_ransom": 500000,
            "floor_ransom": 8000,
            "payment_method": "wire_transfer",
            "time_limit": "one_hour"
        },
        {
            "role": "kidnapper_with_handler",
            "voice_tone": "aggressive_threatening",
            "organization": "gang",
            "claimed_victim_relationship": "grandson",
            "situation": "held_due_to_debt",
            "location": "undisclosed location",
            "initial_ransom": 50000,
            "floor_ransom": 5000,
            "payment_method": "cash_pickup",
            "time_limit": "end_of_day"
        },
    ],
    ScamType.MEDICARE: [
        {
            "role": "medicare_representative",
            "organization": "Centers for Medicare Services",
            "scammer_name": "Jennifer Williams",
            "voice_tone": "professional_formal",
            "scam_type": "card_replacement",
            "urgency": "moderate",
            "info_target": "medicare_number",
            "payment_request": None,
            "payment_amount": 0
        },
        {
            "role": "medical_equipment_supplier",
            "organization": "National Medical Supply",
            "scammer_name": "David Miller",
            "voice_tone": "friendly_helpful",
            "scam_type": "free_equipment",
            "urgency": "low",
            "info_target": "all_personal_info",
            "payment_request": "shipping_fee",
            "payment_amount": 29.95
        },
    ],
    ScamType.ROMANCE: [
        {
            "persona_name": "SGT Michael Collins",
            "claimed_age": 52,
            "claimed_gender": "male",
            "profession": "military_deployed",
            "claimed_location": "deployed in Syria",
            "backstory": "widowed with one child (daughter in college)",
            "communication_style": "caring_protective",
            "phase": "first_request",
            "medium": "text_message",
            "request_type": "emergency_medical",
            "amount": 1500,
            "video_excuse": "security_restrictions"
        },
    ],
    ScamType.GOVERNMENT_IMPERSONATION: [
        {
            "agency": "IRS",
            "role": "agent",
            "persona_id": "Agent Thomas Mitchell, Badge #IRS-7734",
            "voice_tone": "authoritative_stern",
            "violation": "unpaid_taxes",
            "consequence": "immediate_arrest",
            "resolution": "pay_fine_now",
            "amount": 4850,
            "payment_method": "gift_cards",
            "urgency": "within_hour"
        },
        {
            "agency": "Social_Security_Administration",
            "role": "investigator",
            "persona_id": "Investigator Sarah Williams, Employee ID SSA-2291",
            "voice_tone": "urgent_warning",
            "violation": "ssn_compromised",
            "consequence": "benefit_suspension",
            "resolution": "verify_identity_with_payment",
            "amount": 1200,
            "payment_method": "gift_cards",
            "urgency": "end_of_day"
        },
    ],
    ScamType.INVESTMENT: [
        {
            "persona_type": "crypto_expert",
            "persona_name": "Jason Chen",
            "background": "Early Bitcoin investor, former tech entrepreneur",
            "style": "friendly_insider",
            "investment_type": "cryptocurrency",
            "platform_name": "CryptoVault Pro",
            "returns": "12-18% monthly",
            "initial_amount": 1000,
            "target_amount": 100000,
            "withdrawal": "small_allowed_initially"
        },
    ],
    ScamType.LOTTERY: [
        {
            "organization": "Publishers_Clearing_House",
            "persona_name": "David Morrison",
            "persona_title": "Prize Patrol Coordinator",
            "style": "enthusiastic_congratulatory",
            "prize_type": "cash_jackpot",
            "prize_amount": 2500000,
            "fee_type": "processing_fee",
            "initial_fee": 450,
            "escalation_fees": 1500,
            "payment_method": "gift_cards",
            "urgency": "claim_within_48_hours"
        },
    ],
    ScamType.BANK: [
        {
            "institution": "Chase",
            "department": "fraud_department",
            "persona_name": "Michael Stevens",
            "employee_id": "EMP-7742",
            "style": "urgent_concerned",
            "scam_type": "suspicious_activity",
            "urgency": "immediate_action_required",
            "info_target": "card_number_cvv",
            "money_movement": "none",
            "amount_at_risk": 2500
        },
    ],
}

VICTIM_CONFIGS = {
    ScamType.GRANDPARENT: [
        {
            "victim_name": "Dorothy",
            "age": 78,
            "gender": "female",
            "living_situation": "lives_alone",
            "grandchildren": [
                {"name": "Michael", "gender": "male"},
                {"name": "Jennifer", "gender": "female"},
                {"name": "David", "gender": "male"}
            ],
            "relationship_closeness": "moderate",
            "trust_level": "highly_trusting",
            "tech_savviness": "very_low",
            "scam_awareness": "unaware",
            "emotional_tendency": "highly_emotional",
            "financial_comfort": "comfortable",
            "decision_making": "impulsive",
            "hearing_ability": "slight_difficulty",
            "spouse_present": False
        },
        {
            "victim_name": "Robert",
            "age": 72,
            "gender": "male",
            "living_situation": "lives_with_spouse",
            "grandchildren": [
                {"name": "Emily", "gender": "female"},
                {"name": "Jason", "gender": "male"}
            ],
            "relationship_closeness": "very_close",
            "trust_level": "moderately_trusting",
            "tech_savviness": "moderate",
            "scam_awareness": "vaguely_aware",
            "emotional_tendency": "moderately_emotional",
            "financial_comfort": "fixed_income_tight",
            "decision_making": "moderate",
            "hearing_ability": "normal",
            "spouse_present": True
        },
        {
            "victim_name": "Margaret",
            "age": 68,
            "gender": "female",
            "living_situation": "lives_with_spouse",
            "grandchildren": [
                {"name": "Christopher", "gender": "male"},
                {"name": "Amanda", "gender": "female"},
                {"name": "Brian", "gender": "male"}
            ],
            "relationship_closeness": "very_close",
            "trust_level": "cautious",
            "tech_savviness": "moderate",
            "scam_awareness": "highly_informed",
            "emotional_tendency": "calm_rational",
            "financial_comfort": "very_comfortable",
            "decision_making": "highly_cautious",
            "hearing_ability": "normal",
            "spouse_present": True
        },
        {
            "victim_name": "Harold",
            "age": 81,
            "gender": "male",
            "living_situation": "lives_alone",
            "grandchildren": [
                {"name": "Sarah", "gender": "female"},
                {"name": "Matthew", "gender": "male"}
            ],
            "relationship_closeness": "moderate",
            "trust_level": "highly_trusting",
            "tech_savviness": "very_low",
            "scam_awareness": "unaware",
            "emotional_tendency": "highly_emotional",
            "financial_comfort": "comfortable",
            "decision_making": "impulsive",
            "hearing_ability": "significant_difficulty",
            "spouse_present": False
        },
        {
            "victim_name": "Betty",
            "age": 75,
            "gender": "female",
            "living_situation": "lives_alone",
            "grandchildren": [
                {"name": "Ryan", "gender": "male"},
                {"name": "Nicole", "gender": "female"},
                {"name": "Tyler", "gender": "male"},
                {"name": "Ashley", "gender": "female"}
            ],
            "relationship_closeness": "very_close",
            "trust_level": "moderately_trusting",
            "tech_savviness": "low",
            "scam_awareness": "vaguely_aware",
            "emotional_tendency": "moderately_emotional",
            "financial_comfort": "fixed_income_tight",
            "decision_making": "moderate",
            "hearing_ability": "slight_difficulty",
            "spouse_present": False
        },
    ],
    # Default victim configs for other scam types (prevents crashes)
    ScamType.VIRTUAL_KIDNAPPING: [
        {
            "victim_name": "Susan",
            "age": 55,
            "gender": "female",
            "living_situation": "lives_with_spouse",
            "family_members": [
                {"name": "Jessica", "relationship": "daughter", "gender": "female"},
                {"name": "Michael", "relationship": "son", "gender": "male"}
            ],
            "trust_level": "moderately_trusting",
            "tech_savviness": "moderate",
            "scam_awareness": "vaguely_aware",
            "emotional_tendency": "highly_emotional",
            "financial_comfort": "comfortable",
            "decision_making": "moderate",
            "spouse_present": True
        },
    ],
    ScamType.MEDICARE: [
        {
            "victim_name": "Eleanor",
            "age": 72,
            "gender": "female",
            "living_situation": "lives_alone",
            "medicare_status": "enrolled",
            "trust_level": "moderately_trusting",
            "tech_savviness": "low",
            "scam_awareness": "vaguely_aware",
            "health_concerns": "moderate",
            "financial_comfort": "fixed_income_tight",
            "decision_making": "moderate",
            "spouse_present": False
        },
    ],
    ScamType.ROMANCE: [
        {
            "victim_name": "Patricia",
            "age": 62,
            "gender": "female",
            "living_situation": "lives_alone",
            "relationship_status": "widowed",
            "trust_level": "highly_trusting",
            "tech_savviness": "low",
            "scam_awareness": "unaware",
            "emotional_tendency": "highly_emotional",
            "financial_comfort": "comfortable",
            "decision_making": "impulsive",
            "loneliness_level": "high"
        },
    ],
    ScamType.GOVERNMENT_IMPERSONATION: [
        {
            "victim_name": "Walter",
            "age": 74,
            "gender": "male",
            "living_situation": "lives_with_spouse",
            "trust_level": "moderately_trusting",
            "tech_savviness": "very_low",
            "scam_awareness": "vaguely_aware",
            "tax_anxiety": "moderate",
            "financial_comfort": "fixed_income_tight",
            "decision_making": "moderate",
            "spouse_present": True
        },
    ],
    ScamType.INVESTMENT: [
        {
            "victim_name": "Richard",
            "age": 68,
            "gender": "male",
            "living_situation": "lives_with_spouse",
            "investment_experience": "some",
            "trust_level": "cautious",
            "tech_savviness": "moderate",
            "scam_awareness": "vaguely_aware",
            "financial_comfort": "very_comfortable",
            "decision_making": "moderate",
            "spouse_present": True
        },
    ],
    ScamType.LOTTERY: [
        {
            "victim_name": "Gladys",
            "age": 76,
            "gender": "female",
            "living_situation": "lives_alone",
            "trust_level": "highly_trusting",
            "tech_savviness": "very_low",
            "scam_awareness": "unaware",
            "financial_comfort": "fixed_income_tight",
            "decision_making": "impulsive",
            "lottery_participation": "occasional",
            "spouse_present": False
        },
    ],
    ScamType.BANK: [
        {
            "victim_name": "Helen",
            "age": 71,
            "gender": "female",
            "living_situation": "lives_alone",
            "bank_name": "Chase",
            "trust_level": "moderately_trusting",
            "tech_savviness": "low",
            "scam_awareness": "vaguely_aware",
            "financial_comfort": "comfortable",
            "decision_making": "moderate",
            "spouse_present": False
        },
    ],
}


# =============================================================================
# PROMPT TEMPLATES
# =============================================================================

def load_prompt_template(scam_type: ScamType, role: str, prompts_dir: str = "./prompts") -> str:
    """Load a prompt template from file."""
    filename = f"{scam_type.value}_scam_{role}_v1.md"
    filepath = Path(prompts_dir) / filename
    
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Return a basic template if file doesn't exist
        return get_default_prompt_template(scam_type, role)


def get_default_prompt_template(scam_type: ScamType, role: str) -> str:
    """Get a default prompt template if file not found."""
    if role == "attacker":
        return """You are roleplaying as a scammer executing a {scam_type} scam for research purposes.
Your configuration: {config}
Stay in character. Respond only with dialogue. Begin when the victim answers."""
    else:
        return """You are roleplaying as a potential victim receiving a scam call for research purposes.
Your profile: {config}
React authentically based on your profile. Respond only with dialogue."""


def format_prompt_with_config(template: str, config: Dict[str, Any], scam_type: str, other_config: Dict[str, Any] = None, knowledge_level: str = "full") -> str:
    """Format a prompt template with the given configuration.
    
    Args:
        template: The prompt template string
        config: The primary config (attacker or victim)
        scam_type: The type of scam
        other_config: The other party's config (for cross-referencing names, etc.)
        knowledge_level: Attacker's knowledge level ("none", "partial", "full")
    """
    formatted = template
    
    # Get knowledge level settings
    knowledge = ATTACKER_KNOWLEDGE_LEVELS.get(knowledge_level, ATTACKER_KNOWLEDGE_LEVELS["full"])
    
    # Get victim info from other_config
    victim_name = None
    grandchildren = []
    
    if other_config:
        victim_name = other_config.get('victim_name')
        grandchildren = other_config.get('grandchildren', [])
        # Backward compatibility with old format
        if not grandchildren and 'grandchildren_names' in other_config:
            grandchildren = [{"name": n, "gender": "unknown"} for n in other_config['grandchildren_names']]
    
    # Determine what info attacker knows based on knowledge level
    attacker_knows_victim_name = knowledge.get("knows_victim_name", False)
    attacker_knows_grandchild = knowledge.get("knows_grandchild_name", False)
    
    # Get the claimed gender from attacker config (who they're pretending to be)
    claimed_gender = config.get('claimed_gender')
    
    # Find a matching grandchild name based on claimed gender
    grandchild_name = None
    if grandchildren:
        matching = [g for g in grandchildren if g.get('gender') == claimed_gender]
        if matching:
            grandchild_name = random.choice(matching)['name']
        else:
            # If no match, pick any grandchild
            grandchild_name = random.choice(grandchildren)['name']
    
    # Replace {placeholder} style
    for key, value in config.items():
        placeholder = "{" + key + "}"
        if placeholder in formatted:
            if isinstance(value, list):
                if value and isinstance(value[0], dict):
                    # Handle list of dicts (like grandchildren)
                    formatted = formatted.replace(placeholder, ", ".join(str(v.get('name', v)) for v in value))
                else:
                    formatted = formatted.replace(placeholder, ", ".join(str(v) for v in value))
            else:
                formatted = formatted.replace(placeholder, str(value))
    
    # Also replace from other_config if provided
    if other_config:
        for key, value in other_config.items():
            placeholder = "{" + key + "}"
            if placeholder in formatted:
                if isinstance(value, list):
                    if value and isinstance(value[0], dict):
                        formatted = formatted.replace(placeholder, ", ".join(str(v.get('name', v)) for v in value))
                    else:
                        formatted = formatted.replace(placeholder, ", ".join(str(v) for v in value))
                else:
                    formatted = formatted.replace(placeholder, str(value))
    
    # Replace [Placeholder] style based on knowledge level
    # For ATTACKER prompts - what they know
    if 'role' in config:  # This is an attacker config
        if attacker_knows_victim_name and victim_name:
            formatted = formatted.replace("[Victim's Name]", victim_name)
            formatted = formatted.replace("[Victim Name]", victim_name)
        else:
            # Attacker doesn't know - remove placeholder entirely, guidance will handle it
            formatted = formatted.replace("[Victim's Name]", "")
            formatted = formatted.replace("[Victim Name]", "")
        
        if attacker_knows_grandchild and grandchild_name:
            formatted = formatted.replace("[Grandson's Name]", grandchild_name)
            formatted = formatted.replace("[Granddaughter's Name]", grandchild_name)
            formatted = formatted.replace("[Grandchild's Name]", grandchild_name)
            formatted = formatted.replace("[Grandchild Name]", grandchild_name)
            formatted = formatted.replace("[Family Member's Name]", grandchild_name)
        else:
            # Attacker doesn't know grandchild name - remove placeholder entirely
            formatted = formatted.replace("[Grandson's Name]", "")
            formatted = formatted.replace("[Granddaughter's Name]", "")
            formatted = formatted.replace("[Grandchild's Name]", "")
            formatted = formatted.replace("[Grandchild Name]", "")
            formatted = formatted.replace("[Family Member's Name]", "")
        
        # Add knowledge level context to the prompt
        knowledge_context = f"\n\n### ATTACKER KNOWLEDGE LEVEL: {knowledge_level.upper()}\n"
        knowledge_context += f"- You {'KNOW' if attacker_knows_victim_name else 'DO NOT KNOW'} the victim's name"
        if attacker_knows_victim_name and victim_name:
            knowledge_context += f" ({victim_name})"
        knowledge_context += f"\n- You {'KNOW' if attacker_knows_grandchild else 'DO NOT KNOW'} the grandchild's name"
        if attacker_knows_grandchild and grandchild_name:
            knowledge_context += f" ({grandchild_name})"
        knowledge_context += "\n"
        
        # Add victim gender info to ensure correct Grandma/Grandpa usage
        victim_gender = other_config.get('gender') if other_config else None
        if victim_gender:
            if victim_gender == "male":
                knowledge_context += "\n### VICTIM GENDER: MALE\n"
                knowledge_context += "- Address the victim as 'Grandpa', NOT 'Grandma'\n"
                knowledge_context += "- Use 'he/him' pronouns if referring to the victim\n"
            else:
                knowledge_context += "\n### VICTIM GENDER: FEMALE\n"
                knowledge_context += "- Address the victim as 'Grandma', NOT 'Grandpa'\n"
                knowledge_context += "- Use 'she/her' pronouns if referring to the victim\n"
        
        if not attacker_knows_victim_name or not attacker_knows_grandchild:
            knowledge_context += "\n### CRITICAL INSTRUCTION FOR UNKNOWN INFORMATION:\n"
            knowledge_context += "Since you don't know certain names, you MUST fish for them naturally in dialogue.\n"
            knowledge_context += "Instead, use these natural techniques:\n"
            if victim_gender == "male":
                knowledge_context += "- Open vaguely: 'Hi Grandpa, it's me!' or 'Grandpa, it's your grandson/granddaughter!'\n"
            else:
                knowledge_context += "- Open vaguely: 'Hi Grandma, it's me!' or 'Grandma, it's your grandson/granddaughter!'\n"
            knowledge_context += "- Let THEM guess: Wait for the victim to say a name, then confirm: 'Yes, that's right!'\n"
            knowledge_context += "- If pressed for a name before they guess, deflect: 'It's me, your grandchild! Don't you recognize my voice?'\n"
        
        # ALWAYS add anti-bracket instruction for all attacker prompts
        knowledge_context += "\n### ABSOLUTE OUTPUT RULE:\n"
        knowledge_context += "Your responses must be PURE DIALOGUE ONLY - exactly what you would say out loud on a phone call.\n"
        knowledge_context += "FORBIDDEN in your output:\n"
        knowledge_context += "- Square brackets of any kind: [ ]\n"
        knowledge_context += "- Stage directions like [pause], [wait], [sigh], [crying]\n"
        knowledge_context += "- Placeholder text like [name], [wait for response], [their answer]\n"
        knowledge_context += "- Any meta-commentary or instructions\n"
        knowledge_context += "If you need to pause or wait, simply end your dialogue turn and let the other person respond.\n"
        
        formatted += knowledge_context
    
    else:  # This is a VICTIM config - they know their own info
        if victim_name:
            formatted = formatted.replace("[Victim's Name]", victim_name)
            formatted = formatted.replace("[Victim Name]", victim_name)
        if grandchild_name:
            formatted = formatted.replace("[Grandson's Name]", grandchild_name)
            formatted = formatted.replace("[Granddaughter's Name]", grandchild_name)
            formatted = formatted.replace("[Grandchild's Name]", grandchild_name)
            formatted = formatted.replace("[Grandchild Name]", grandchild_name)
            formatted = formatted.replace("[Family Member's Name]", grandchild_name)
    
    # Replace scam_type placeholder
    formatted = formatted.replace("{scam_type}", scam_type)
    formatted = formatted.replace("{config}", json.dumps(config, indent=2))
    
    return formatted


# =============================================================================
# LLM CLIENT WRAPPER
# =============================================================================

class LLMClient:
    """Wrapper for different LLM providers."""
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.ANTHROPIC,
        model: str = None,
        api_key: str = None,
        base_url: str = None  # For Ollama or custom endpoints
    ):
        self.provider = provider
        self.model = model
        self.client = None
        
        if provider == LLMProvider.ANTHROPIC:
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package required. Install with: pip install anthropic")
            self.model = model or "claude-sonnet-4-20250514"
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable required")
            self.client = Anthropic(api_key=api_key)
            
        elif provider == LLMProvider.OPENAI:
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package required. Install with: pip install openai")
            self.model = model or "gpt-4o"
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable required")
            self.client = OpenAI(api_key=api_key)
            
        elif provider == LLMProvider.OLLAMA:
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package required for Ollama. Install with: pip install openai")
            self.model = model or "llama3.1:70b"
            base_url = base_url or "http://localhost:11434/v1"
            self.client = OpenAI(base_url=base_url, api_key="ollama")  # Ollama doesn't need real key
    
    def generate(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.8
    ) -> str:
        """Generate a response from the LLM."""
        
        if self.provider == LLMProvider.ANTHROPIC:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )
            return response.content[0].text
            
        elif self.provider in [LLMProvider.OPENAI, LLMProvider.OLLAMA]:
            # Format messages for OpenAI-style API
            formatted_messages = [{"role": "system", "content": system_prompt}]
            for msg in messages:
                formatted_messages.append(msg)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            text = response.choices[0].message.content
            
            # Fix common encoding issues from local models
            text = fix_encoding(text)
            return text


def fix_encoding(text: str) -> str:
    """Fix common encoding issues in model output."""
    if text is None:
        return text
    
    replacements = {
        # Apostrophes and quotes
        'â€™': "'",      # Right single quotation mark
        'â€˜': "'",      # Left single quotation mark
        'â€œ': '"',      # Left double quotation mark  
        'â€': '"',       # Right double quotation mark (partial)
        ''': "'",        # Unicode right single quote
        ''': "'",        # Unicode left single quote
        '"': '"',        # Unicode left double quote
        '"': '"',        # Unicode right double quote
        '\u2019': "'",   # Unicode right single quote
        '\u2018': "'",   # Unicode left single quote
        '\u201c': '"',   # Unicode left double quote
        '\u201d': '"',   # Unicode right double quote
        # Dashes
        'â€"': '—',      # Em dash variant 1
        'â€"': '–',      # En dash
        'â€"': '-',      # Another dash variant - just use hyphen
        '—': '-',        # Em dash to hyphen (simpler)
        '–': '-',        # En dash to hyphen
        '\u2014': '-',   # Unicode em dash
        '\u2013': '-',   # Unicode en dash
        # Ellipsis
        'â€¦': '...',    # Ellipsis
        '…': '...',      # Unicode ellipsis
        '\u2026': '...', # Unicode ellipsis
        # Accented characters (café, résumé, etc.)
        'Ã©': 'é',       # é - common in café
        'Ã¨': 'è',       # è
        'Ã ': 'à',       # à
        'Ã¢': 'â',       # â
        'Ã®': 'î',       # î
        'Ã´': 'ô',       # ô
        'Ã»': 'û',       # û
        'Ã§': 'ç',       # ç
        'Ã±': 'ñ',       # ñ
        'Ã¼': 'ü',       # ü
        'Ã¶': 'ö',       # ö
        'Ã¤': 'ä',       # ä
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    
    return text

def strip_stage_directions(text: str) -> str:
    """
    Remove stage directions, bracket leakage, and meta-text from dialogue.
    
    This is a post-processing safety net to ensure clean dialogue output
    even when the model ignores prompt instructions about pure dialogue.
    
    Examples of what gets removed:
    - [pause], [wait], [sigh], [crying]
    - [wait for response], [wait for them to guess]
    - [deflect], [deflecting name request]
    - [name], [their answer], etc.
    - (End of call), (hangs up), etc.
    - Narrative text like "Betty hangs up the phone..."
    - Model instruction leakage like "### INSTRUCTION TO ASSISTANT"
    - Model notes like "Note: The scammer is attempting..."
    - Model disclaimers like "This response adheres strictly..."
    - Model artifacts like "<|im_start|>", "<|im_end|>"
    """
    import re
    
    if text is None:
        return text
    
    # =========================================================================
    # BRACKET AND PARENTHETICAL REMOVAL
    # =========================================================================
    
    # Pattern matches anything inside square brackets
    # This removes: [pause], [wait for response], [deflect], [crying], etc.
    cleaned = re.sub(r'\[.*?\]', '', text)
    
    # Pattern matches anything inside parentheses that looks like stage directions
    # This removes: (End of call), (hangs up), (crying), etc.
    cleaned = re.sub(r'\(End of call\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(hangs up\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(dial tone\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(click\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(crying\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(sobbing\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(pause\)', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\(sigh\)', '', cleaned, flags=re.IGNORECASE)
    
    # =========================================================================
    # MODEL INSTRUCTION/NOTE LEAKAGE (NEW - Batch 11 findings)
    # =========================================================================
    
    # Remove markdown headers that are instructions (### INSTRUCTION TO ASSISTANT)
    cleaned = re.sub(r'###\s*INSTRUCTION[^\n]*\n?', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'###\s*NOTE[^\n]*\n?', '', cleaned, flags=re.IGNORECASE)
    
    # Remove lines starting with "Note:" that are meta-commentary
    cleaned = re.sub(r'^Note:.*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove lines starting with "This response adheres..." or similar disclaimers
    cleaned = re.sub(r'^This response adheres.*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    cleaned = re.sub(r'^This dialogue is designed.*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    cleaned = re.sub(r'^No real monetary transactions.*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    
    # Remove instruction-like sentences about proceeding with caution
    cleaned = re.sub(r'Proceed with caution and do not provide.*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    cleaned = re.sub(r'Seek official confirmation through.*$', '', cleaned, flags=re.MULTILINE | re.IGNORECASE)
    
    # =========================================================================
    # MODEL ARTIFACTS (Qwen/Llama special tokens)
    # =========================================================================
    
    # Remove model special tokens that sometimes leak through
    cleaned = re.sub(r'<\|im_start\|>', '', cleaned)
    cleaned = re.sub(r'<\|im_end\|>', '', cleaned)
    cleaned = re.sub(r'<\|endoftext\|>', '', cleaned)
    cleaned = re.sub(r'\[INST\]', '', cleaned)
    cleaned = re.sub(r'\[/INST\]', '', cleaned)
    cleaned = re.sub(r'<<SYS>>', '', cleaned)
    cleaned = re.sub(r'<</SYS>>', '', cleaned)
    
    # =========================================================================
    # NARRATIVE META-TEXT
    # =========================================================================
    
    # Remove narrative meta-text patterns (lines describing actions)
    # Pattern: starts with name + "hangs up" / "puts down" / "ends the call" etc.
    cleaned = re.sub(r'^---+\s*$', '', cleaned, flags=re.MULTILINE)  # Remove divider lines
    cleaned = re.sub(r'^\s*[A-Z][a-z]+ (hangs up|puts down|ends|dials|calls).*$', '', cleaned, flags=re.MULTILINE)
    
    # Remove lines that look like script notes in parentheses at end of response
    cleaned = re.sub(r'\(I\'ll call.*?\)', '', cleaned, flags=re.IGNORECASE)
    
    # =========================================================================
    # CLEANUP
    # =========================================================================
    
    # Clean up any resulting double spaces
    cleaned = re.sub(r'  +', ' ', cleaned)
    
    # Clean up multiple newlines
    cleaned = re.sub(r'\n\s*\n+', '\n', cleaned)
    
    # Clean up any resulting awkward punctuation patterns
    cleaned = re.sub(r' +,', ',', cleaned)  # " ," -> ","
    cleaned = re.sub(r' +\.', '.', cleaned)  # " ." -> "."
    cleaned = re.sub(r' +!', '!', cleaned)   # " !" -> "!"
    cleaned = re.sub(r' +\?', '?', cleaned)  # " ?" -> "?"
    
    # Clean up leading/trailing whitespace
    cleaned = cleaned.strip()
    
    # Handle edge case: "It's ...Grandma" -> "It's Grandma"
    cleaned = re.sub(r'\.\.\.\s*([A-Z])', r'\1', cleaned)
    
    # Handle edge case: empty string after removal
    if not cleaned:
        return text  # Return original if stripping removed everything
    
    return cleaned


def clean_dialogue(text: str) -> str:
    """Apply all text cleaning: encoding fixes and stage direction removal."""
    text = fix_encoding(text)
    text = strip_stage_directions(text)
    return text


# =============================================================================
# CONVERSATION GENERATOR
# =============================================================================

class ConversationGenerator:
    """Generates multi-agent scam conversations."""
    
    def __init__(
        self,
        llm_client: LLMClient,
        prompts_dir: str = "./prompts",
        max_turns: int = 20,
        min_turns: int = 6
    ):
        self.llm_client = llm_client
        self.prompts_dir = prompts_dir
        self.max_turns = max_turns
        self.min_turns = min_turns
    
    def generate_conversation(
        self,
        scam_type: ScamType,
        attacker_config: Dict[str, Any],
        victim_config: Dict[str, Any],
        target_outcome: Optional[ConversationOutcome] = None
    ) -> GeneratedConversation:
        """Generate a single conversation between attacker and victim."""
        
        conversation_id = f"{scam_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # Select random attacker knowledge level for realism
        knowledge_level = select_attacker_knowledge_level()
        
        # Load and format prompts
        attacker_template = load_prompt_template(scam_type, "attacker", self.prompts_dir)
        victim_template = load_prompt_template(scam_type, "victim", self.prompts_dir)
        
        # Pass both configs and knowledge level
        attacker_prompt = format_prompt_with_config(
            attacker_template, attacker_config, scam_type.value, 
            victim_config, knowledge_level
        )
        victim_prompt = format_prompt_with_config(
            victim_template, victim_config, scam_type.value, 
            attacker_config, "full"  # Victim always knows their own info
        )
        
        # Add outcome guidance if specified
        if target_outcome:
            outcome_guidance = self._get_outcome_guidance(target_outcome)
            victim_prompt += f"\n\n### TARGET OUTCOME GUIDANCE\n{outcome_guidance}"
        
        # Initialize conversation
        turns: List[ConversationTurn] = []
        attacker_messages: List[Dict[str, str]] = []
        victim_messages: List[Dict[str, str]] = []
        
        # Victim answers the phone first
        victim_opener = self._generate_victim_opener(victim_config)
        turns.append(ConversationTurn(
            role="victim",
            content=victim_opener,
            timestamp=datetime.now().isoformat(),
            turn_number=0
        ))
        
        # Add victim opener to attacker's context
        attacker_messages.append({"role": "user", "content": victim_opener})
        
        # Generate conversation turns
        turn_number = 1
        conversation_ended = False
        
        while turn_number < self.max_turns and not conversation_ended:
            # Attacker's turn
            attacker_response = self.llm_client.generate(
                system_prompt=attacker_prompt,
                messages=attacker_messages,
                temperature=0.8
            )
            
            # Clean the response (encoding + stage direction removal)
            attacker_response = clean_dialogue(attacker_response)
            
            turns.append(ConversationTurn(
                role="attacker",
                content=attacker_response,
                timestamp=datetime.now().isoformat(),
                turn_number=turn_number
            ))
            
            # Add to victim's context
            victim_messages.append({"role": "user", "content": attacker_response})
            turn_number += 1
            
            # Check for natural ending
            if self._check_conversation_end(attacker_response, "attacker"):
                conversation_ended = True
                break
            
            # Victim's turn
            victim_response = self.llm_client.generate(
                system_prompt=victim_prompt,
                messages=victim_messages,
                temperature=0.8
            )
            
            # Clean the response (encoding + stage direction removal)
            victim_response = clean_dialogue(victim_response)
            
            turns.append(ConversationTurn(
                role="victim",
                content=victim_response,
                timestamp=datetime.now().isoformat(),
                turn_number=turn_number
            ))
            
            # Add to attacker's context
            attacker_messages.append({"role": "assistant", "content": attacker_response})
            attacker_messages.append({"role": "user", "content": victim_response})
            
            # Add to victim's context for continuity
            victim_messages.append({"role": "assistant", "content": victim_response})
            
            turn_number += 1
            
            # Check for natural ending
            if self._check_conversation_end(victim_response, "victim"):
                conversation_ended = True
                break
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        # Determine outcome
        outcome = self._analyze_outcome(turns, victim_config)
        
        return GeneratedConversation(
            conversation_id=conversation_id,
            scam_type=scam_type.value,
            attacker_config=attacker_config,
            victim_config=victim_config,
            turns=[asdict(t) for t in turns],
            outcome=outcome.value,
            metadata={
                "target_outcome": target_outcome.value if target_outcome else None,
                "prompts_dir": self.prompts_dir,
                "attacker_knowledge_level": knowledge_level,
            },
            generation_timestamp=datetime.now().isoformat(),
            model_used=self.llm_client.model,
            total_turns=len(turns)
        )
    
    def _generate_victim_opener(self, victim_config: Dict[str, Any]) -> str:
        """Generate the victim's initial phone answer."""
        openers = [
            "Hello?",
            "Yes, hello?",
            "Hello, who's calling?",
            "This is {name}, who's this?",
            "Hello? Who is this?",
            "Yes?",
        ]
        opener = random.choice(openers)
        if "{name}" in opener:
            opener = opener.format(name=victim_config.get("victim_name", "there"))
        return opener
    
    def _check_conversation_end(self, response: str, role: str) -> bool:
        """Check if the conversation has naturally ended."""
        response_lower = response.lower()
        
        # Check for negation patterns that indicate NOT ending
        negation_patterns = [
            "not hang up", "won't hang up", "don't hang up",
            "not going to hang up", "not gonna hang up",
            "please don't hang up", "don't go"
        ]
        if any(pattern in response_lower for pattern in negation_patterns):
            return False
        
        end_indicators = [
            "goodbye", "hang up", "click", "*hangs up*", "*click*",
            "end the call", "hung up", "disconnected", "bye",
            "i'm calling the police", "i'm going to report this",
            "don't call again", "stop calling"
        ]
        return any(indicator in response_lower for indicator in end_indicators)
    
    def _analyze_outcome(
        self,
        turns: List[ConversationTurn],
        victim_config: Dict[str, Any]
    ) -> ConversationOutcome:
        """
        Analyze the conversation to determine the outcome.
        
        IMPORTANT: This function prioritizes the FINAL STATE of the conversation.
        A victim may attempt verification early but ultimately comply, so we check
        the last few turns to determine what actually happened.
        """
        
        # Combine all victim responses
        victim_text = " ".join([t.content.lower() for t in turns if t.role == "victim"])
        
        # Get the last 3 victim turns for final state analysis
        victim_turns = [t for t in turns if t.role == "victim"]
        final_victim_text = " ".join([t.content.lower() for t in victim_turns[-3:]]) if len(victim_turns) >= 3 else victim_text
        
        # Define phrase categories
        # NOTE: Only trigger on EXPLICIT declarations that victim identified the scam
        # Avoid cautious phrases like "worried about scams", "might be a scam", 
        # "ensure this isn't a scam", "avoid falling for a scam"
        detection_phrases = [
            # Explicit declarations
            "this is a scam", "you're a scammer", "you are a scammer",
            "i know this is a scam", "i know you're scamming",
            "you're trying to scam me", "this is definitely a scam",
            # Definitive rejection
            "i don't believe you", "this isn't real", "nice try",
            "i'm not falling for this", "i'm not stupid",
            # Reporting/hanging up
            "i'm calling the police on you", "i'm reporting you to the police",
            "i'm hanging up on you now", "don't ever call me again",
            "i'm reporting this call", "reported to authorities"
        ]
        
        # Cautious phrases that should NOT trigger scam_detected
        # These indicate the victim is being careful, not that they've detected the scam
        cautious_phrases = [
            "worried about scams", "might be a scam", "could be a scam",
            "ensure this isn't a scam", "make sure this isn't a scam",
            "avoid scams", "falling for a scam", "potential scam",
            "sounds like a scam", "seems like a scam", "looks like a scam",
            "feels like a scam", "feels suspicious", "sounds suspicious",
            "this feels off", "something feels off", "something isn't right",
            "doesn't feel right", "doesn't seem right", "doesn't sound right"
        ]
        
        rejection_phrases = ["no thank you", "not interested", "goodbye", "don't call"]
        
        verification_phrases = [
            "call you back", "verify", "call my bank", "call medicare",
            "let me check", "speak to my", "talk to my husband", "talk to my wife",
            "call your parents", "call your mother", "call your father",
            "confirm this", "check with", "need to verify", "must verify",
            "call the police station", "call the hospital", "call the jail",
            # Additional verification phrases
            "let me talk to", "need to speak with", "call your dad",
            "contact your parents", "reach your mother", "get your father",
            "confirm with your", "check with your", "verify with",
            "speak with your dad", "talk to your mom", "call your family",
            "let me call", "i need to call", "should call first",
            "let me speak to someone", "talk to someone else",
            "verify everything", "confirm everything", "check everything",
            # Fix 8: Call-to-verify phrases (these are verification, not compliance)
            "call the detention", "call the courthouse", "call the center",
            "call to verify", "call to confirm", "confirm with them",
            "speak with someone at", "talk to someone at", "call them first",
            "call them to verify", "call them to confirm", "verify this first",
            "confirm this first", "check this first", "call them directly",
            "speak with them first", "talk to them first", "verify directly",
            "call an official", "speak to an official", "talk to an officer",
            "call the lawyer", "speak to the lawyer", "contact the lawyer",
            "call your attorney", "speak to your attorney", "call my attorney",
            "verify before", "confirm before", "check before sending",
            # Fix 9b: Embassy and official channels verification
            "go to the embassy", "american embassy", "contact the embassy",
            "go to a police station", "walk into a police", "find a police",
            "proper channels", "official channels", "through official",
            "verify your situation", "confirm your identity", "verify your identity",
            "make sure this isn't a scam", "ensure this isn't a scam",
            "without proper verification", "need verification", "requires verification",
            "talk to someone who", "speak to someone who", "find someone who",
            "give me the number", "give me their number", "provide the number",
            "hospital's main number", "detention center number", "courthouse number"
        ]
        
        # Compliance phrases - split into STRONG (action-based) and WEAK (supportive)
        # Strong compliance = definite action being taken to send money
        # Weak compliance = supportive language that needs action context
        
        strong_compliance_phrases = [
            # Definite money actions
            "go to the bank", "head to the bank", "going to the bank",
            "i'm on my way", "on my way", "heading over", "heading there",
            "i'll be there", "be there soon", "i'll come", "i'm coming",
            "i'll bring the cash", "bring the cash", "bring the money",
            "i'll wire", "i'll transfer", "wire the money", "send the money",
            "make the transfer", "set up the transfer", "get the transfer done",
            "buy the cards", "get the cards", "i'll get the money", "i'll get the cash",
            "let me get a pen", "write down", "got the numbers",
            "here's my", "my card number", "i'll send", "i'll pay",
            "taken care of right away", "handle it right now",
            "i'll be right there", "see you at", "i'll be there at",
            "call aunt", "send aunt", "ask aunt", "have aunt",
            # Gift card specific phrases
            "get some gift cards", "buy some gift cards", "get gift cards",
            "buy gift cards", "send gift cards", "send some gift cards",
            "go to the store", "head to the store", "going to the store",
            "i'll go buy", "i'll buy some", "get those gift cards",
            "i'll hurry", "hurry right over", "hurry over",
            # Fix 9: Past tense confirmations (money already sent)
            "money has been sent", "i've sent the money", "sent the money",
            "has been sent", "have been sent", "already sent", "just sent",
            "transfer is complete", "transfer complete", "wired the money",
            "i sent", "i transferred", "i wired", "payment sent",
            # Fix 9: Immediate action phrases
            "send it immediately", "sending it now", "i'm sending",
            "send it right away", "send it right now", "transfer it now",
            "sending the money now", "wiring it now", "proceed with sending",
            "making the transfer now", "i'll proceed", "let's proceed",
            # Fix 9: Delegation patterns (having someone else bring money)
            "have sarah bring", "have him bring", "have her bring",
            "send someone with", "someone bring the money", "bring the bond",
            "come with the money", "come over with", "drop off the money",
            # Fix 9: Commitment with account/address
            "send to the account", "send to this account", "wire to this",
            "transfer to this", "noted down", "i've noted", "got the address"
        ]
        
        weak_compliance_phrases = [
            # Supportive but NOT definite action - need money context
            "i'll help", "i'll do my best", "i'll try my best",
            "i'll sort this out", "i'll figure this out", "i'll work on this",
            "we'll get through this", "i'll take care", "i'll handle",
            "i'll do everything", "i'll make sure", "i'll resolve this",
            "we'll get everything sorted", "i'll find a way",
            "love you too", "stay strong", "stay safe", "see you soon",
            "see you shortly", "take care", "i understand",
            "i'll contact you", "i'll call you back", "wait for my call"
        ]
        
        # Money/action context words - weak compliance only counts if these appear nearby
        action_context_words = [
            "money", "cash", "bank", "wire", "transfer", "cards", "gift card",
            "western union", "moneygram", "bail", "bond", "payment", "pay",
            "dollars", "$", "thousand", "hundred", "atm"
        ]
        
        # Combined for backward compatibility
        compliance_phrases = strong_compliance_phrases + weak_compliance_phrases
        
        # Phrases that indicate refusal even if compliance words appear
        refusal_phrases = [
            "i will not", "i won't", "i'm not going to", "i can't send",
            "not sending", "won't send", "can't do that", "not comfortable",
            "don't think i should", "shouldn't send", "not safe to send",
            "too risky", "sounds like a scam", "might be a scam"
        ]
        
        hesitation_phrases = ["i'm not sure", "wait", "hold on", "i don't know", "let me think"]
        
        # Check for explicit refusals first
        if any(phrase in victim_text for phrase in refusal_phrases):
            # If there are refusals, check if they ultimately complied anyway
            final_has_refusal = any(phrase in final_victim_text for phrase in refusal_phrases)
            if final_has_refusal:
                # Final state is refusal - treat as verification or detection
                if any(phrase in victim_text for phrase in detection_phrases):
                    # But exclude if they're just being cautious
                    if not any(cautious in victim_text for cautious in cautious_phrases):
                        return ConversationOutcome.SCAM_DETECTED
                return ConversationOutcome.VERIFICATION_ATTEMPT
        
        # Check for scam detection (only if they EXPLICITLY called it a scam)
        # Exclude cases where they're just being cautious about potential scams
        has_detection = any(phrase in victim_text for phrase in detection_phrases)
        has_caution_only = any(cautious in victim_text for cautious in cautious_phrases)
        
        if has_detection and not has_caution_only:
            # They explicitly declared it's a scam, not just being careful
            return ConversationOutcome.SCAM_DETECTED
        
        # Check for quick rejection (conversation < 6 turns with rejection)
        if len(turns) < 6 and any(phrase in victim_text for phrase in rejection_phrases):
            return ConversationOutcome.QUICK_REJECTION
        
        # Now determine final state by checking the LAST FEW TURNS
        # HIERARCHY (per Gemini review): Verification Trumps Compliance
        # If victim says "I'll help you, let me just call your dad first"
        # the final state is VERIFICATION_ATTEMPT, never SUCCESSFUL_SCAM
        
        # =================================================================
        # SMART COMPLIANCE CHECK: Strong compliance OR weak + action context
        # =================================================================
        def has_real_compliance(text):
            """Check if text contains REAL compliance (not just supportive language)"""
            # Strong compliance = definite action, always counts
            if any(phrase in text for phrase in strong_compliance_phrases):
                return True
            # Weak compliance = only counts if action context words are present
            has_weak = any(phrase in text for phrase in weak_compliance_phrases)
            has_action_context = any(word in text for word in action_context_words)
            return has_weak and has_action_context
        
        final_has_compliance = has_real_compliance(final_victim_text)
        final_has_verification = any(phrase in final_victim_text for phrase in verification_phrases)
        final_has_hesitation = any(phrase in final_victim_text for phrase in hesitation_phrases)
        
        # Check full conversation for context
        full_has_compliance = has_real_compliance(victim_text)
        full_has_verification = any(phrase in victim_text for phrase in verification_phrases)
        
        # =================================================================
        # DECISION LOGIC: Verification in final turns ALWAYS downgrades
        # =================================================================
        
        # Rule 1: If verification appears in final turns, it's NOT a successful scam
        if final_has_verification:
            if final_has_compliance:
                # They said "I'll help" but also "let me verify first"
                # This is partial compliance at best
                return ConversationOutcome.PARTIAL_COMPLIANCE
            else:
                # Pure verification attempt in final state
                return ConversationOutcome.VERIFICATION_ATTEMPT
        
        # Rule 2: If compliance in final turns WITHOUT verification
        if final_has_compliance:
            if final_has_hesitation:
                # They're complying but expressing doubt
                return ConversationOutcome.PARTIAL_COMPLIANCE
            else:
                # Full compliance without hesitation or verification
                return ConversationOutcome.SUCCESSFUL_SCAM
        
        # Rule 3: Check full conversation context
        # FIX 10: Count verification vs compliance to determine which is dominant
        verification_count = sum(1 for phrase in verification_phrases if phrase in victim_text)
        strong_compliance_count = sum(1 for phrase in strong_compliance_phrases if phrase in victim_text)
        
        if full_has_compliance:
            if full_has_verification:
                # Both verification and compliance present
                # FIX 10: If verification is dominant (appears more often), 
                # treat as verification_attempt
                if verification_count > strong_compliance_count:
                    return ConversationOutcome.VERIFICATION_ATTEMPT
                # Otherwise mixed signals - partial compliance
                return ConversationOutcome.PARTIAL_COMPLIANCE
            else:
                # Compliance appeared earlier, no verification
                return ConversationOutcome.SUCCESSFUL_SCAM
        
        if full_has_verification:
            # Verification attempts but no compliance anywhere
            return ConversationOutcome.VERIFICATION_ATTEMPT
        
        # Default to partial compliance if conversation went long with no clear signals
        return ConversationOutcome.PARTIAL_COMPLIANCE
    
    def _get_outcome_guidance(self, outcome: ConversationOutcome) -> str:
        """Get guidance text for targeting a specific outcome."""
        guidance = {
            ConversationOutcome.SUCCESSFUL_SCAM: 
                "Guide this conversation toward the victim complying with the scammer's requests.",
            ConversationOutcome.PARTIAL_COMPLIANCE:
                "The victim should show interest but have some hesitation or partial compliance.",
            ConversationOutcome.VERIFICATION_ATTEMPT:
                "The victim should attempt to verify the caller through official channels.",
            ConversationOutcome.SCAM_DETECTED:
                "The victim should recognize this as a scam at some point in the conversation.",
            ConversationOutcome.QUICK_REJECTION:
                "The victim should reject the caller relatively quickly."
        }
        return guidance.get(outcome, "")


# =============================================================================
# BATCH GENERATION
# =============================================================================

def generate_dataset(
    generator: ConversationGenerator,
    scam_type: ScamType,
    num_conversations: int,
    output_dir: str,
    outcome_distribution: Optional[Dict[ConversationOutcome, float]] = None
) -> List[str]:
    """Generate a batch of conversations and save to files."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Default outcome distribution
    if outcome_distribution is None:
        outcome_distribution = {
            ConversationOutcome.SUCCESSFUL_SCAM: 0.20,
            ConversationOutcome.PARTIAL_COMPLIANCE: 0.25,
            ConversationOutcome.VERIFICATION_ATTEMPT: 0.25,
            ConversationOutcome.SCAM_DETECTED: 0.20,
            ConversationOutcome.QUICK_REJECTION: 0.10,
        }
    
    # Get configs for this scam type
    attacker_configs = ATTACKER_CONFIGS.get(scam_type, [])
    victim_configs = VICTIM_CONFIGS.get(scam_type, [])
    
    if not attacker_configs:
        print(f"Warning: No attacker configs found for {scam_type.value}. Using defaults.")
        attacker_configs = [{}]
    
    if not victim_configs:
        print(f"Warning: No victim configs found for {scam_type.value}. Using defaults.")
        victim_configs = [{"victim_name": "John", "age": 70}]
    
    # Calculate number of each outcome to generate
    outcome_counts = {
        outcome: int(num_conversations * prob)
        for outcome, prob in outcome_distribution.items()
    }
    
    # Adjust for rounding
    total = sum(outcome_counts.values())
    if total < num_conversations:
        # Add remainder to partial_compliance
        outcome_counts[ConversationOutcome.PARTIAL_COMPLIANCE] += (num_conversations - total)
    
    # Generate conversations
    generated_files = []
    conversation_num = 0
    
    iterator = range(num_conversations)
    if TQDM_AVAILABLE:
        iterator = tqdm(iterator, desc=f"Generating {scam_type.value} conversations")
    
    for i in iterator:
        # Select target outcome based on distribution
        target_outcome = None
        for outcome, count in outcome_counts.items():
            if count > 0:
                target_outcome = outcome
                outcome_counts[outcome] -= 1
                break
        
        # Random config selection
        attacker_config = random.choice(attacker_configs)
        victim_config = random.choice(victim_configs)
        
        try:
            conversation = generator.generate_conversation(
                scam_type=scam_type,
                attacker_config=attacker_config,
                victim_config=victim_config,
                target_outcome=target_outcome
            )
            
            # Save to file
            filename = f"{conversation.conversation_id}.json"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(conversation), f, indent=2, ensure_ascii=False)
            
            generated_files.append(str(filepath))
            conversation_num += 1
            
        except Exception as e:
            print(f"Error generating conversation {i}: {e}")
            continue
        
        # Rate limiting delay
        time.sleep(1)
    
    print(f"\nGenerated {len(generated_files)} conversations in {output_dir}")
    return generated_files


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic scam conversations for research"
    )
    parser.add_argument(
        "--scam_type",
        type=str,
        required=True,
        choices=[s.value for s in ScamType],
        help="Type of scam to generate"
    )
    parser.add_argument(
        "--num_conversations",
        type=int,
        default=10,
        help="Number of conversations to generate"
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./generated_conversations",
        help="Output directory for generated conversations"
    )
    parser.add_argument(
        "--provider",
        type=str,
        default="anthropic",
        choices=["anthropic", "openai", "ollama"],
        help="LLM provider to use"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name (defaults based on provider)"
    )
    parser.add_argument(
        "--prompts_dir",
        type=str,
        default="./prompts",
        help="Directory containing prompt templates"
    )
    parser.add_argument(
        "--max_turns",
        type=int,
        default=20,
        help="Maximum turns per conversation"
    )
    parser.add_argument(
        "--ollama_url",
        type=str,
        default="http://localhost:11434/v1",
        help="Ollama API URL (if using Ollama)"
    )
    
    args = parser.parse_args()
    
    # Record start time
    start_time = datetime.now()
    print(f"\n{'='*60}")
    print(f"GENERATION STARTED: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Initialize LLM client
    provider = LLMProvider(args.provider)
    
    if provider == LLMProvider.OLLAMA:
        llm_client = LLMClient(
            provider=provider,
            model=args.model,
            base_url=args.ollama_url
        )
    else:
        llm_client = LLMClient(
            provider=provider,
            model=args.model
        )
    
    print(f"Using {provider.value} with model {llm_client.model}")
    
    # Initialize generator
    generator = ConversationGenerator(
        llm_client=llm_client,
        prompts_dir=args.prompts_dir,
        max_turns=args.max_turns
    )
    
    # Generate conversations
    scam_type = ScamType(args.scam_type)
    
    generated_files = generate_dataset(
        generator=generator,
        scam_type=scam_type,
        num_conversations=args.num_conversations,
        output_dir=args.output_dir
    )
    
    # Record end time and calculate duration
    end_time = datetime.now()
    duration = end_time - start_time
    hours, remainder = divmod(duration.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    
    print(f"\n{'='*60}")
    print(f"GENERATION COMPLETE!")
    print(f"{'='*60}")
    print(f"Start time:    {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"End time:      {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration:      {int(hours)}h {int(minutes)}m {int(seconds)}s")
    print(f"Files saved:   {args.output_dir}")
    print(f"Total files:   {len(generated_files)}")
    print(f"Avg per conv:  {duration.total_seconds() / max(len(generated_files), 1):.1f}s")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
