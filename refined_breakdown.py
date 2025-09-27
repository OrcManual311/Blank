#!/usr/bin/env python3
"""
Text Breakdown Tool - Refined to Match Example Format

This implementation closely follows the pattern shown in the GET method example,
providing a hierarchical breakdown that matches the structure and detail level.
"""

import re
from typing import List, Dict

def breakdown_text_sections(text: str) -> Dict[int, List[str]]:
    """
    Break down text into sections following the exact pattern from the GET method example.
    """
    
    # Split text into major sections (by double/triple newlines)
    sections = re.split(r'\n\s*\n\s*\n+', text.strip())
    sections = [s.strip() for s in sections if s.strip()]
    
    result = {}
    
    for i, section in enumerate(sections, 1):
        breakdown = []
        
        # 1. Always start with the complete section text
        breakdown.append(section)
        
        # 2. Extract key sentences/bullet points
        sentences = extract_sentences(section)
        
        for sentence in sentences:
            if sentence.strip() and sentence.strip() != section.strip():
                breakdown.append(sentence.strip())
                
                # 3. Extract meaningful phrases from each sentence
                phrases = extract_key_phrases(sentence)
                for phrase in phrases:
                    if phrase not in breakdown:
                        breakdown.append(phrase)
                
                # 4. Extract individual significant terms
                terms = extract_significant_terms(sentence)
                for term in terms:
                    if term not in breakdown:
                        breakdown.append(term)
        
        result[i] = breakdown
    
    return result

def extract_sentences(text: str) -> List[str]:
    """Extract sentences and bullet points."""
    sentences = []
    
    lines = text.split('\n')
    current = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Handle bullet points and numbered items
        if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
            if current:
                sentences.append(current.strip())
                current = ""
            sentences.append(line)
        elif line.endswith(':'):
            # Headers
            if current:
                sentences.append(current.strip())
                current = ""
            sentences.append(line)
        else:
            if current:
                current += " " + line
            else:
                current = line
            
            if re.search(r'[.!?]\s*$', line):
                sentences.append(current.strip())
                current = ""
    
    if current:
        sentences.append(current.strip())
    
    return sentences

def extract_key_phrases(sentence: str) -> List[str]:
    """Extract meaningful phrases, matching the example's selectivity."""
    phrases = []
    
    # Clean bullet markers
    clean = re.sub(r'^[-*•]\s*', '', sentence)
    clean = re.sub(r'^\d+\.\s*', '', clean)
    
    # Split on major breaks
    splits = re.split(r'[,;:]\s+|(?:\s+and\s+)|(?:\s+or\s+)', clean, flags=re.IGNORECASE)
    
    for split in splits:
        split = split.strip()
        if len(split.split()) >= 2 and len(split.split()) <= 8:  # Reasonable phrase length
            phrases.append(split)
    
    # Extract parenthetical content
    parens = re.findall(r'\([^)]+\)', sentence)
    for p in parens:
        content = p.strip('()')
        if content:
            phrases.append(content)
    
    return phrases

def extract_significant_terms(sentence: str) -> List[str]:
    """Extract key terms and individual words, being selective like the example."""
    terms = []
    
    # Technical terms and URLs
    technical = re.findall(r'\.well-known|https?://[^\s,]+|[A-Z]{2,}|\w+\.\w+', sentence)
    terms.extend(technical)
    
    # Extract words, being selective
    clean = re.sub(r'^[-*•]\s*', '', sentence)
    clean = re.sub(r'^\d+\.\s*', '', clean)
    words = re.findall(r'\b\w+\b', clean)
    
    stop_words = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
                  'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that', 
                  'the', 'to', 'was', 'were', 'will', 'with'}
    
    # Select meaningful 2-word combinations
    for i in range(len(words) - 1):
        if (words[i].lower() not in stop_words or words[i+1].lower() not in stop_words):
            two_word = f"{words[i]} {words[i+1]}"
            terms.append(two_word)
    
    # Add significant individual words
    for word in words:
        if word.lower() not in stop_words and len(word) > 2:
            terms.append(word)
    
    return terms

def format_output(breakdown_dict: Dict[int, List[str]]) -> str:
    """Format the output exactly like the example."""
    lines = []
    
    for section_num, items in breakdown_dict.items():
        # Quote each item and join with commas
        quoted_items = [f"'{item}'" for item in items]
        lines.append(f"{section_num}. {', '.join(quoted_items)}")
    
    return '\n'.join(lines)

def main():
    """Process the two provided text sections."""
    
    # Full Task 1: .Well-Known URIs (complete text as provided)
    task1_text = """.Well-Known URIs



Overview:

.well-known is a standardized path prefix defined by RFCs that hosts use to expose machine-readable metadata and service configuration at predictable locations: https://example.com/.well-known/<name>. These endpoints are high-value for reconnaissance because they reveal service configuration, security contact details, OIDC/OAuth endpoints, ACME challenge locations, and other canonical data that can accelerate discovery and assessment.



Common .well-known resources and what they reveal:

- /.well-known/security.txt — security disclosure contacts, policy, PGP keys, and reporting instructions. Useful for finding a contact or a disclosure policy and sometimes PGP keys or URLs pointing to other hosts.

- /.well-known/openid-configuration (or /openid-configuration) — OIDC discovery document. Reveals authorization, token, userinfo endpoints and supported flows; excellent for further auth-focused enumeration.

- /.well-known/webfinger — account/service discovery; can reveal account metadata for federated interfaces.

- /.well-known/assetlinks.json — Android app links and relationships, often exposing package names and host mappings.

- /.well-known/change-password — a user-facing hint to a password change page (can be used to guess account management paths).

- /.well-known/host-meta and /.well-known/host-meta.json — service metadata used in federation.

- /.well-known/acme-challenge — used by certificate authorities for domain validation; contents are typically validation tokens.

- /.well-known/health or /status — machine-readable health endpoints that may reveal internal state and service names.



Importance to testers common high-value uses:

- Predictable and machine-readable: no guessing required; these endpoints often contain precise URLs or configuration you can feed into tooling.

- Configuration leakage: discovery documents and security.txt files may expose internal endpoints, admin panels, or secondary hosts.

- Auth attack surface: OIDC discovery provides endpoints for token requests, introspection, and supported claim types — a great starting point for auth enumeration.

- Automation-friendly: responses are usually JSON or plaintext, making them easy to parse and import into scanners."""

    # Full Task 2: Creepy Crawlies (complete text as provided)
    task2_text = """Creepy Crawlies



Overview:

"Creepy Crawlies" (Web Crawlers and Automated Spiders) refers to automated crawlers and spiders used to enumerate websites: collecting URLs, resources, page content, and link graphs. In reconnaissance they let you scale discovery, uncover hidden paths, harvest parameters, and build target lists quickly. However, crawlers can be noisy and trigger protections — use them with care and always respect scope and rate limits.



Crawler types and their common uses:

- Static crawlers: wget, httrack, curl loops. Fast for static content and simple link graphs, low overhead.

- Recursive directory fuzzers: gobuster, ffuf in recursive mode. Good for uncovering hidden directories and extensions.

- Programmatic frameworks: Scrapy (Python), custom scripts. Flexible extraction, pipelines, and exporters.

- Headless/browser crawlers: Playwright, Puppeteer, Selenium. Necessary when content is rendered client-side with JavaScript.

- Burp/ZAP spiders: integrated with proxies and scanners; useful for interactive exploration and correlation with passive scans."""

    print("Task 1.: The section I want you to break down similarly of - '.Well-Known URIs':")
    result1 = breakdown_text_sections(task1_text)
    print(format_output(result1))
    
    print("\n\nTask 2.: The section I want you to break down similarly of - 'Creepy Crawlies':")
    result2 = breakdown_text_sections(task2_text)
    print(format_output(result2))

if __name__ == "__main__":
    main()