# Text Breakdown Tool

This repository contains a Python tool that implements hierarchical text breakdown functionality as demonstrated in the provided example.

## Overview

The text breakdown tool takes sections of text and recursively breaks them down from large blocks to individual words and concepts, following a top-down approach.

## Usage

Run the main script to see the breakdown of the two provided text sections:

```bash
python3 refined_breakdown.py
```

## Features

- **Hierarchical Breakdown**: Starts with complete sections and progressively breaks down to individual terms
- **Technical Term Recognition**: Identifies URLs, acronyms, and dotted notation (like .well-known)
- **Phrase Extraction**: Extracts meaningful multi-word phrases
- **Stop Word Filtering**: Excludes common stop words when they appear alone
- **Formatted Output**: Produces output with single-quoted items separated by commas

## Example Output Format

Each numbered section contains a breakdown like:
```
1. 'Complete section text', 'Individual sentences', 'key phrases', 'technical terms', 'individual words'
```

## Files

- `refined_breakdown.py` - Main implementation with the two test cases
- `text_breakdown.py` - Earlier version with more verbose output  
- `text_breakdown_v2.py` - Second iteration
- `final_text_breakdown.py` - Alternative implementation approach

The `refined_breakdown.py` is the recommended version that most closely matches the example pattern.