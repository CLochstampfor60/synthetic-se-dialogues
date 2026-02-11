"""
Updated strip_stage_directions() function for generate_conversations.py
Author: Carl Lochstampfor

Add these new patterns to handle meta-text leakage found in Batch 11:
- "### INSTRUCTION TO ASSISTANT"
- "Note: The scammer is attempting..."
- "This response adheres strictly to the requirements..."
- "<|im_start|>" and similar model artifacts

Replace the existing strip_stage_directions() function with this version.
"""

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


# =============================================================================
# TEST CASES
# =============================================================================

if __name__ == "__main__":
    # Test the new patterns
    test_cases = [
        # Existing patterns (should still work)
        ("Hello [pause] there", "Hello there"),
        ("I need help (hangs up)", "I need help"),
        
        # New Batch 11 patterns
        (
            "I understand it seems urgent, but we really should get some confirmation first.\n### INSTRUCTION TO ASSISTANT\nProceed with caution and do not provide financial details until official verification occurs.",
            "I understand it seems urgent, but we really should get some confirmation first."
        ),
        (
            "Please, Grandma, please...\nNote: The scammer is attempting to build urgency and trust but should avoid pushing too hard.",
            "Please, Grandma, please..."
        ),
        (
            "Thank you Grandpa, I will.\nThis response adheres strictly to the requirements set forth in your instructions.",
            "Thank you Grandpa, I will."
        ),
        (
            "Hello<|im_start|> there",
            "Hello there"
        ),
    ]
    
    print("Testing strip_stage_directions()...\n")
    
    all_passed = True
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = strip_stage_directions(input_text)
        passed = result.strip() == expected.strip()
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Test {i}: {status}")
        if not passed:
            all_passed = False
            print(f"  Input:    {repr(input_text[:50])}...")
            print(f"  Expected: {repr(expected)}")
            print(f"  Got:      {repr(result)}")
        print()
    
    if all_passed:
        print("All tests passed! ✅")
    else:
        print("Some tests failed. ❌")
