#!/usr/bin/env python3
"""
Batch Scanner for Chinese Text Contamination
Author: Carl Lochstampfor

Scans all JSON conversation files in a directory and identifies those
containing Chinese/CJK characters that indicate model language leakage.

Usage:
    python scan_contamination.py <directory_path>
    
Example:
    python scan_contamination.py ..\data\grandparent
"""

import json
import os
import sys
import re
from pathlib import Path


def contains_chinese(text: str) -> bool:
    """
    Check if text contains Chinese/CJK characters.
    
    CJK Unicode ranges:
    - 4E00-9FFF: CJK Unified Ideographs
    - 3400-4DBF: CJK Unified Ideographs Extension A
    - 20000-2A6DF: CJK Unified Ideographs Extension B
    - 2A700-2B73F: CJK Unified Ideographs Extension C
    - 2B740-2B81F: CJK Unified Ideographs Extension D
    - F900-FAFF: CJK Compatibility Ideographs
    - 2F800-2FA1F: CJK Compatibility Ideographs Supplement
    """
    if not text:
        return False
    
    # Pattern for CJK characters
    cjk_pattern = re.compile(
        r'[\u4e00-\u9fff'    # CJK Unified Ideographs
        r'\u3400-\u4dbf'     # CJK Unified Ideographs Extension A
        r'\uf900-\ufaff'     # CJK Compatibility Ideographs
        r'\u3000-\u303f'     # CJK Punctuation
        r'\uff00-\uffef]'    # Fullwidth Forms
    )
    
    return bool(cjk_pattern.search(text))


def scan_conversation_file(filepath: str) -> dict:
    """
    Scan a single conversation JSON file for contamination.
    
    Returns dict with:
    - filename: name of file
    - contaminated: bool
    - chinese_turns: list of turn numbers with Chinese text
    - sample_text: sample of contaminated text (first 100 chars)
    """
    result = {
        "filename": os.path.basename(filepath),
        "filepath": filepath,
        "contaminated": False,
        "chinese_turns": [],
        "sample_text": None
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        turns = data.get("turns", [])
        
        for turn in turns:
            content = turn.get("content", "")
            turn_num = turn.get("turn_number", "?")
            
            if contains_chinese(content):
                result["contaminated"] = True
                result["chinese_turns"].append(turn_num)
                
                # Capture sample of first contaminated text
                if result["sample_text"] is None:
                    # Find the Chinese portion
                    cjk_match = re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]+', content)
                    if cjk_match:
                        start = max(0, cjk_match.start() - 20)
                        end = min(len(content), cjk_match.end() + 50)
                        result["sample_text"] = content[start:end]
    
    except Exception as e:
        result["error"] = str(e)
    
    return result


def scan_directory(directory: str) -> list:
    """Scan all JSON files in directory for contamination."""
    results = []
    
    json_files = list(Path(directory).glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {directory}")
        return results
    
    print(f"Scanning {len(json_files)} files in {directory}...\n")
    
    for filepath in sorted(json_files):
        result = scan_conversation_file(str(filepath))
        results.append(result)
        
        # Progress indicator
        if result["contaminated"]:
            print(f"  ❌ CONTAMINATED: {result['filename']} (turns: {result['chinese_turns']})")
    
    return results


def print_summary(results: list):
    """Print summary of scan results."""
    total = len(results)
    contaminated = [r for r in results if r["contaminated"]]
    clean = total - len(contaminated)
    
    print("\n" + "="*60)
    print("SCAN SUMMARY")
    print("="*60)
    print(f"Total files scanned:  {total}")
    print(f"Clean files:          {clean} ({100*clean/total:.1f}%)")
    print(f"Contaminated files:   {len(contaminated)} ({100*len(contaminated)/total:.1f}%)")
    
    if contaminated:
        print("\n" + "-"*60)
        print("CONTAMINATED FILES (need regeneration):")
        print("-"*60)
        for r in contaminated:
            print(f"\n  File: {r['filename']}")
            print(f"  Turns with Chinese: {r['chinese_turns']}")
            if r['sample_text']:
                print(f"  Sample: {r['sample_text'][:80]}...")
        
        print("\n" + "-"*60)
        print("FILES TO DELETE/REGENERATE:")
        print("-"*60)
        for r in contaminated:
            print(f"  {r['filename']}")
        
        # Generate delete command
        print("\n" + "-"*60)
        print("POWERSHELL COMMAND TO DELETE CONTAMINATED FILES:")
        print("-"*60)
        filenames = [r['filename'] for r in contaminated]
        print(f"Remove-Item {', '.join(filenames)}")
    
    else:
        print("\n✅ All files are clean! No contamination detected.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scan_contamination.py <directory_path>")
        print("Example: python scan_contamination.py ..\\data\\grandparent")
        sys.exit(1)
    
    directory = sys.argv[1]
    
    if not os.path.isdir(directory):
        print(f"Error: '{directory}' is not a valid directory")
        sys.exit(1)
    
    results = scan_directory(directory)
    
    if results:
        print_summary(results)


if __name__ == "__main__":
    main()
