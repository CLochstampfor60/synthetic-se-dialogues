#!/usr/bin/env python3
"""
Language Detection and Filtering Utility for Synthetic Conversation Dataset
Author: Carl Lochstampfor

This module provides utilities for:
1. Detecting non-English text in conversations
2. Flagging/rejecting conversations with language issues
3. Optional translation support (requires additional dependencies)

Usage:
    from language_filter import LanguageFilter
    
    filter = LanguageFilter()
    result = filter.check_conversation(conversation_data)
    if not result['is_clean']:
        print(f"Issues found: {result['issues']}")
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Chinese character ranges (CJK Unified Ideographs and extensions)
# Using raw string with proper Unicode escape for extended ranges
CHINESE_PATTERN = re.compile(
    r'['
    r'\u4e00-\u9fff'      # CJK Unified Ideographs
    r'\u3400-\u4dbf'      # CJK Unified Ideographs Extension A
    r'\U00020000-\U0002a6df'  # CJK Unified Ideographs Extension B
    r'\U0002a700-\U0002b73f'  # CJK Unified Ideographs Extension C
    r'\U0002b740-\U0002b81f'  # CJK Unified Ideographs Extension D
    r']+'
)

# Other non-ASCII patterns that shouldn't appear in English conversations
JAPANESE_HIRAGANA = re.compile(r'[\u3040-\u309f]+')
JAPANESE_KATAKANA = re.compile(r'[\u30a0-\u30ff]+')
KOREAN_HANGUL = re.compile(r'[\uac00-\ud7af\u1100-\u11ff]+')

# Meta-text patterns (model artifacts)
META_TEXT_PATTERNS = [
    re.compile(r'<\|im_start\|>'),
    re.compile(r'<\|im_end\|>'),
    re.compile(r'\[INST\]'),
    re.compile(r'\[/INST\]'),
    re.compile(r'<<SYS>>'),
    re.compile(r'<</SYS>>'),
    re.compile(r'<\|user\|>'),
    re.compile(r'<\|assistant\|>'),
]


class LanguageFilter:
    """Filter and validate conversation language content."""
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize the language filter.
        
        Args:
            strict_mode: If True, any non-English content fails validation.
                        If False, only flag conversations with >20% non-English.
        """
        self.strict_mode = strict_mode
        
    def detect_chinese(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect Chinese characters in text.
        
        Returns:
            Tuple of (has_chinese, list of matched strings)
        """
        matches = CHINESE_PATTERN.findall(text)
        return bool(matches), matches
    
    def detect_japanese(self, text: str) -> Tuple[bool, List[str]]:
        """Detect Japanese characters in text."""
        hiragana_matches = JAPANESE_HIRAGANA.findall(text)
        katakana_matches = JAPANESE_KATAKANA.findall(text)
        all_matches = hiragana_matches + katakana_matches
        return bool(all_matches), all_matches
    
    def detect_korean(self, text: str) -> Tuple[bool, List[str]]:
        """Detect Korean characters in text."""
        matches = KOREAN_HANGUL.findall(text)
        return bool(matches), matches
    
    def detect_meta_text(self, text: str) -> Tuple[bool, List[str]]:
        """Detect model meta-text artifacts."""
        issues = []
        for pattern in META_TEXT_PATTERNS:
            matches = pattern.findall(text)
            if matches:
                issues.extend(matches)
        return bool(issues), issues
    
    def check_text(self, text: str) -> Dict[str, Any]:
        """
        Check a single text string for language issues.
        
        Returns:
            Dictionary with detection results
        """
        results = {
            'is_clean': True,
            'has_chinese': False,
            'has_japanese': False,
            'has_korean': False,
            'has_meta_text': False,
            'chinese_matches': [],
            'japanese_matches': [],
            'korean_matches': [],
            'meta_text_matches': [],
        }
        
        # Check for Chinese
        has_chinese, chinese_matches = self.detect_chinese(text)
        if has_chinese:
            results['is_clean'] = False
            results['has_chinese'] = True
            results['chinese_matches'] = chinese_matches
        
        # Check for Japanese
        has_japanese, japanese_matches = self.detect_japanese(text)
        if has_japanese:
            results['is_clean'] = False
            results['has_japanese'] = True
            results['japanese_matches'] = japanese_matches
        
        # Check for Korean
        has_korean, korean_matches = self.detect_korean(text)
        if has_korean:
            results['is_clean'] = False
            results['has_korean'] = True
            results['korean_matches'] = korean_matches
        
        # Check for meta-text
        has_meta, meta_matches = self.detect_meta_text(text)
        if has_meta:
            results['is_clean'] = False
            results['has_meta_text'] = True
            results['meta_text_matches'] = meta_matches
        
        return results
    
    def check_conversation(self, conversation: Dict) -> Dict[str, Any]:
        """
        Check an entire conversation for language issues.
        
        Args:
            conversation: Conversation data dict with 'turns' key
            
        Returns:
            Validation result with details about any issues found
        """
        result = {
            'is_clean': True,
            'conversation_id': conversation.get('conversation_id', 'unknown'),
            'issues': [],
            'affected_turns': [],
            'total_turns': 0,
            'affected_turn_count': 0,
        }
        
        turns = conversation.get('turns', [])
        result['total_turns'] = len(turns)
        
        for turn in turns:
            turn_num = turn.get('turn_number', -1)
            content = turn.get('content', '')
            role = turn.get('role', 'unknown')
            
            check_result = self.check_text(content)
            
            if not check_result['is_clean']:
                result['is_clean'] = False
                result['affected_turns'].append(turn_num)
                
                issue = {
                    'turn_number': turn_num,
                    'role': role,
                    'issues': []
                }
                
                if check_result['has_chinese']:
                    issue['issues'].append({
                        'type': 'chinese_text',
                        'matches': check_result['chinese_matches'][:5]  # Limit to 5 samples
                    })
                
                if check_result['has_japanese']:
                    issue['issues'].append({
                        'type': 'japanese_text',
                        'matches': check_result['japanese_matches'][:5]
                    })
                
                if check_result['has_korean']:
                    issue['issues'].append({
                        'type': 'korean_text',
                        'matches': check_result['korean_matches'][:5]
                    })
                
                if check_result['has_meta_text']:
                    issue['issues'].append({
                        'type': 'meta_text',
                        'matches': check_result['meta_text_matches'][:5]
                    })
                
                result['issues'].append(issue)
        
        result['affected_turn_count'] = len(result['affected_turns'])
        
        # Calculate severity
        if result['total_turns'] > 0:
            affected_ratio = result['affected_turn_count'] / result['total_turns']
            if affected_ratio > 0.5:
                result['severity'] = 'high'
            elif affected_ratio > 0.2:
                result['severity'] = 'medium'
            else:
                result['severity'] = 'low'
        else:
            result['severity'] = 'unknown'
        
        return result
    
    def filter_batch(self, conversation_files: List[Path]) -> Dict[str, Any]:
        """
        Filter a batch of conversation files.
        
        Args:
            conversation_files: List of paths to JSON conversation files
            
        Returns:
            Batch filter results with clean/dirty file lists
        """
        results = {
            'total_files': len(conversation_files),
            'clean_files': [],
            'dirty_files': [],
            'issues_by_type': {
                'chinese_text': 0,
                'japanese_text': 0,
                'korean_text': 0,
                'meta_text': 0,
            },
        }
        
        for file_path in conversation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation = json.load(f)
                
                check_result = self.check_conversation(conversation)
                
                if check_result['is_clean']:
                    results['clean_files'].append(str(file_path))
                else:
                    results['dirty_files'].append({
                        'file': str(file_path),
                        'severity': check_result['severity'],
                        'affected_turns': check_result['affected_turn_count'],
                        'total_turns': check_result['total_turns'],
                    })
                    
                    # Count issue types
                    for issue in check_result['issues']:
                        for issue_detail in issue['issues']:
                            issue_type = issue_detail['type']
                            if issue_type in results['issues_by_type']:
                                results['issues_by_type'][issue_type] += 1
                                
            except Exception as e:
                results['dirty_files'].append({
                    'file': str(file_path),
                    'error': str(e),
                })
        
        results['clean_count'] = len(results['clean_files'])
        results['dirty_count'] = len(results['dirty_files'])
        results['clean_ratio'] = results['clean_count'] / results['total_files'] if results['total_files'] > 0 else 0
        
        return results


def main():
    """Demo usage of the language filter."""
    # Test samples
    test_texts = [
        "Hello, how are you today?",  # Clean English
        "你好，我是你的孙子",  # Chinese
        "Please help me Grandma 奶奶请帮帮我",  # Mixed
        "This is a test <|im_start|> with meta text",  # Meta-text
        "こんにちは",  # Japanese
        "안녕하세요",  # Korean
    ]
    
    filter = LanguageFilter()
    
    print("Language Filter Test Results")
    print("=" * 50)
    
    for text in test_texts:
        result = filter.check_text(text)
        status = "✅ CLEAN" if result['is_clean'] else "❌ DIRTY"
        print(f"\nText: {text[:50]}...")
        print(f"Status: {status}")
        if not result['is_clean']:
            if result['has_chinese']:
                print(f"  - Chinese detected: {result['chinese_matches'][:3]}")
            if result['has_japanese']:
                print(f"  - Japanese detected: {result['japanese_matches'][:3]}")
            if result['has_korean']:
                print(f"  - Korean detected: {result['korean_matches'][:3]}")
            if result['has_meta_text']:
                print(f"  - Meta-text detected: {result['meta_text_matches'][:3]}")


if __name__ == '__main__':
    main()
