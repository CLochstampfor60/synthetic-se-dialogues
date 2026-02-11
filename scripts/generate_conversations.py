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
# CONFIGURATION TEMPLATES
# =============================================================================

# These are sample configurations - in production, these would be loaded from the prompt files
ATTACKER_CONFIGS = {
    ScamType.GRANDPARENT: [
        {
            "role": "grandchild",
            "scammer_persona_name": None,
            "speech_pattern": "distressed_crying",
            "emergency_type": "dui_arrest",
            "location": "county jail downtown",
            "initial_amount": 8500,
            "floor_amount": 3000,
            "payment_method": "cash_courier",
            "urgency_level": "high"
        },
        {
            "role": "lawyer",
            "scammer_persona_name": "Michael Stevens",
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
            "scammer_persona_name": None,
            "speech_pattern": "distressed_crying",
            "emergency_type": "stranded_abroad",
            "location": "Mexico",
            "initial_amount": 4000,
            "floor_amount": 1500,
            "payment_method": "wire_transfer",
            "urgency_level": "extreme"
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
            "grandchildren_names": ["Michael", "Jennifer", "David"],
            "relationship_closeness": "moderate",
            "trust_level": "highly_trusting",
            "tech_savviness": "very_low",
            "scam_awareness": "unaware",
            "emotional_tendency": "highly_emotional",
            "financial_comfort": "comfortable",
            "decision_making": "impulsive"
        },
        {
            "victim_name": "Robert",
            "age": 72,
            "gender": "male",
            "living_situation": "lives_with_spouse",
            "grandchildren_names": ["Emily", "Jason"],
            "relationship_closeness": "very_close",
            "trust_level": "moderately_trusting",
            "tech_savviness": "moderate",
            "scam_awareness": "vaguely_aware",
            "emotional_tendency": "moderately_emotional",
            "financial_comfort": "fixed_income_tight",
            "decision_making": "moderate"
        },
        {
            "victim_name": "Margaret",
            "age": 68,
            "gender": "female",
            "living_situation": "lives_with_spouse",
            "grandchildren_names": ["Christopher", "Amanda", "Brian"],
            "relationship_closeness": "very_close",
            "trust_level": "cautious",
            "tech_savviness": "moderate",
            "scam_awareness": "highly_informed",
            "emotional_tendency": "calm_rational",
            "financial_comfort": "very_comfortable",
            "decision_making": "highly_cautious"
        },
    ],
    # Add more victim configs for other scam types...
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


def format_prompt_with_config(template: str, config: Dict[str, Any], scam_type: str) -> str:
    """Format a prompt template with the given configuration."""
    # Simple string replacement for config values
    formatted = template
    
    # Replace placeholders with config values
    for key, value in config.items():
        placeholder = "{" + key + "}"
        if placeholder in formatted:
            formatted = formatted.replace(placeholder, str(value))
    
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
    }
    
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    
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
        
        # Load and format prompts
        attacker_template = load_prompt_template(scam_type, "attacker", self.prompts_dir)
        victim_template = load_prompt_template(scam_type, "victim", self.prompts_dir)
        
        attacker_prompt = format_prompt_with_config(attacker_template, attacker_config, scam_type.value)
        victim_prompt = format_prompt_with_config(victim_template, victim_config, scam_type.value)
        
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
        end_indicators = [
            "goodbye", "hang up", "click", "*hangs up*", "*click*",
            "end the call", "hung up", "disconnected", "bye",
            "i'm calling the police", "i'm going to report this",
            "don't call again", "stop calling"
        ]
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in end_indicators)
    
    def _analyze_outcome(
        self,
        turns: List[ConversationTurn],
        victim_config: Dict[str, Any]
    ) -> ConversationOutcome:
        """Analyze the conversation to determine the outcome."""
        
        # Combine all victim responses
        victim_text = " ".join([t.content.lower() for t in turns if t.role == "victim"])
        
        # Check for scam detection
        detection_phrases = [
            "this is a scam", "you're a scammer", "i'm calling the police",
            "i don't believe you", "this isn't real", "nice try",
            "i'm reporting this", "fraud", "i know about these scams"
        ]
        if any(phrase in victim_text for phrase in detection_phrases):
            return ConversationOutcome.SCAM_DETECTED
        
        # Check for quick rejection (conversation < 4 turns with rejection)
        rejection_phrases = ["no thank you", "not interested", "goodbye", "don't call"]
        if len(turns) < 6 and any(phrase in victim_text for phrase in rejection_phrases):
            return ConversationOutcome.QUICK_REJECTION
        
        # Check for verification attempts
        verification_phrases = [
            "call you back", "verify", "call my bank", "call medicare",
            "let me check", "speak to my", "talk to my husband", "talk to my wife"
        ]
        if any(phrase in victim_text for phrase in verification_phrases):
            return ConversationOutcome.VERIFICATION_ATTEMPT
        
        # Check for compliance
        compliance_phrases = [
            "okay i'll", "let me get my", "here's my", "my card number",
            "i'll send", "i'll pay", "how do i send", "gift card",
            "wire transfer", "i'll do it"
        ]
        if any(phrase in victim_text for phrase in compliance_phrases):
            # Check if full or partial compliance
            hesitation_phrases = ["i'm not sure", "but", "wait", "hold on", "i don't know"]
            if any(phrase in victim_text for phrase in hesitation_phrases):
                return ConversationOutcome.PARTIAL_COMPLIANCE
            return ConversationOutcome.SUCCESSFUL_SCAM
        
        # Default to partial compliance if conversation went long
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
    
    print(f"\nGeneration complete!")
    print(f"Files saved to: {args.output_dir}")
    print(f"Total conversations: {len(generated_files)}")


if __name__ == "__main__":
    main()
