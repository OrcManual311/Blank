#!/usr/bin/env python3
"""
Text Breakdown Tool

A recursive, top-down text breakdown tool that deconstructs text sections
into their constituent parts, matching the specific style shown in the example.
"""

import re
import sys
from typing import List, Set

class TextBreakdown:
    def __init__(self):
        # Common stop words to exclude when appearing alone
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'been', 'by', 'for', 'from', 
            'has', 'have', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'or', 'that', 
            'the', 'to', 'was', 'were', 'will', 'with', 'can', 'may', 'do', 'does'
        }
        
    def identify_sections(self, text: str) -> List[str]:
        """
        Identify top-level sections based on double line breaks or clear section headers.
        """
        # Split by double newlines and clean up
        sections = []
        parts = re.split(r'\n\s*\n\s*\n+', text.strip())
        
        for part in parts:
            part = part.strip()
            if part:
                sections.append(part)
        
        return sections
    
    def extract_sentences_and_bullets(self, text: str) -> List[str]:
        """
        Extract sentences and bullet points as distinct units.
        """
        sentences = []
        lines = text.split('\n')
        
        current_sentence = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a bullet point or numbered item
            if re.match(r'^[-*•]\s+', line) or re.match(r'^\d+\.\s+', line):
                if current_sentence:
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
                sentences.append(line)
            elif line.endswith(':'):
                # Headers or labels
                if current_sentence:
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
                sentences.append(line)
            else:
                # Regular sentence content
                if current_sentence:
                    current_sentence += " " + line
                else:
                    current_sentence = line
                
                # Check if sentence ends
                if re.search(r'[.!?]\s*$', line):
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
        
        # Add any remaining sentence
        if current_sentence:
            sentences.append(current_sentence.strip())
        
        return [s for s in sentences if s.strip()]
    
    def break_down_sentence(self, sentence: str) -> List[str]:
        """
        Break down a sentence into progressively smaller parts following the example pattern.
        """
        parts = []
        seen = set()
        
        def add_if_new(item):
            item = item.strip()
            if item and item.lower() not in seen:
                parts.append(item)
                seen.add(item.lower())
        
        # Clean the sentence
        clean_sentence = re.sub(r'^[-*•]\s*', '', sentence)
        clean_sentence = re.sub(r'^\d+\.\s*', '', clean_sentence)
        
        add_if_new(sentence)
        
        # Split by major conjunctions and punctuation
        major_splits = re.split(r'[,;:]\s+|(?:\s+and\s+)|(?:\s+or\s+)|(?:\s+but\s+)', clean_sentence, flags=re.IGNORECASE)
        
        for split in major_splits:
            split = split.strip()
            if len(split.split()) >= 2:  # Multi-word phrases only
                add_if_new(split)
        
        # Extract parenthetical expressions
        parentheticals = re.findall(r'\([^)]+\)', sentence)
        for p in parentheticals:
            add_if_new(p.strip('()'))
            add_if_new(p)  # Keep with parentheses too
        
        # Break down into smaller phrases (2-4 words)
        words = re.findall(r'\b\w+\b', clean_sentence)
        
        # Create meaningful 2-3 word phrases
        for i in range(len(words) - 1):
            two_word = f"{words[i]} {words[i+1]}"
            if not all(w.lower() in self.stop_words for w in [words[i], words[i+1]]):
                add_if_new(two_word)
            
            if i < len(words) - 2:
                three_word = f"{words[i]} {words[i+1]} {words[i+2]}"
                # Only add if it contains non-stop words and is meaningful
                if any(w.lower() not in self.stop_words for w in [words[i], words[i+1], words[i+2]]):
                    add_if_new(three_word)
        
        # Add individual significant words
        for word in words:
            if word.lower() not in self.stop_words and len(word) > 1:
                add_if_new(word.lower())
        
        # Handle special technical terms
        technical_terms = re.findall(r'\.well-known|https?://[^\s]+|[A-Z]{2,}|[\w-]+\.[\w-]+', sentence)
        for term in technical_terms:
            add_if_new(term)
        
        return parts
    
    def breakdown_section(self, section_text: str) -> List[str]:
        """
        Perform complete breakdown of a section.
        """
        breakdown = []
        seen = set()
        
        def add_unique(item):
            if item and item.lower() not in seen:
                breakdown.append(item)
                seen.add(item.lower())
        
        # 1. Add the entire section
        add_unique(section_text.strip())
        
        # 2. Process each sentence/bullet
        sentences = self.extract_sentences_and_bullets(section_text)
        
        for sentence in sentences:
            sentence_parts = self.break_down_sentence(sentence)
            for part in sentence_parts:
                add_unique(part)
        
        return breakdown
    
    def process_text(self, text: str) -> dict:
        """
        Process the entire text and return numbered sections with breakdowns.
        """
        sections = self.identify_sections(text)
        result = {}
        
        for i, section in enumerate(sections, 1):
            result[i] = self.breakdown_section(section)
        
        return result
    
    def format_output(self, breakdown_dict: dict) -> str:
        """
        Format the output to match the expected style.
        """
        output_lines = []
        
        for section_num, breakdown_list in breakdown_dict.items():
            # Format each item with single quotes and join with commas
            formatted_items = [f"'{item}'" for item in breakdown_list]
            output_lines.append(f"{section_num}. {', '.join(formatted_items)}")
        
        return '\n'.join(output_lines)


def main():
    """Main function to demonstrate the text breakdown tool."""
    
    # Test with the first section: .Well-Known URIs
    well_known_text = """.Well-Known URIs



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

- Automation-friendly: responses are usually JSON or plaintext, making them easy to parse and import into scanners.



Reconnaissance common workflow example:

1. Fetch the typical set of well-known endpoints for the target host. Use an allowlist of common names to avoid noisy blind fuzzing.

   - curl -sS -D - https://TARGET/.well-known/security.txt

   - curl -sS -D - https://TARGET/.well-known/openid-configuration

2. Parse JSON discovery docs (openid-configuration) to extract endpoints and supported features. Save them for follow-up tests.

   - jq '.' openid.json

3. If security.txt is present, note contact methods, disclosure instructions, and any referenced URLs or PGP keys.

4. Check /.well-known/acme-challenge for public tokens (do not interfere with tokens; only observe). These rarely contain secret data but confirm CA usage and can indicate automated cert issuance.

5. Add discovered endpoints to your target list: token endpoints, introspection endpoints, password/change URLs, and any admin-like paths.



Commands and lightweight automation:

- Single-run fetch for a list of names (safe and targeted):

  - for p in security.txt openid-configuration webfinger assetlinks.json change-password acme-challenge host-meta; do curl -sS -o "/tmp/$p" "https://TARGET/.well-known/$p" && echo "Saved /tmp/$p"; done

- Parse openid discovery quickly (example):

  - curl -sS https://TARGET/.well-known/openid-configuration | jq '{issuer,authorization_endpoint,token_endpoint,introspection_endpoint,userinfo_endpoint}' > /tmp/oidc_endpoints.json

- Use a small wordlist for .well-known names if you need more coverage, but prefer a curated list to reduce noise.



Interpreting results and next actions:

- security.txt: If it lists a contact and PGP key, keep the key for verifying signed communications in disclosure. If it references a private host or subdomain, add that host to your enumeration.

- openid-configuration: Feed the token and authorization endpoints into safe, read-only discovery (requesting metadata only). Avoid automated credential attacks unless in-scope.

- assetlinks.json and app-claim files: map mobile app package names to hosts; this can reveal mobile-specific endpoints or backend hosts.

- health/status endpoints: If the response includes internal service names, ports, or versions, correlate those with fingerprinting results to prioritize targets.



Edge cases and common recommended measures:

- Redirection and host headers: some well-known endpoints behave differently depending on Host header or HTTP->HTTPS redirects. Test both schemes and consider probing via an IP with Host header only when in-scope and authorized.

- Canonical vs non-canonical paths: some servers expose both /well-known/<x> and /.well-known/<x> or accept alternate spellings. Stick to standardized paths first.

- Rate limits and CA hooks: do not flood /.well-known/acme-challenge; those interact with CA tooling and can create noise or break validation.

- Not a replacement for broad brute force: .well-known is a precision-first technique; it complements directory fuzzing rather than replacing it.



Common practical examples and key targets:

- Example: discovery reveals an openid token endpoint at https://auth.example.com/oauth/token. This gives you a focused host to check for exposed metadata, misconfigured CORS, or weak client credentials (in-scope only).

- Example: security.txt lists a staging host like staging.example.com. Add that host to your subdomain enumeration and check for weaker protections.

- Example: assetlinks.json shows an android package and an API host — use that to search for mobile-specific endpoints and parameters.



Common recommended measures:

- Expose minimal necessary data in .well-known endpoints. Avoid pointing to internal hostnames or providing excessive debug information.

- Rate-limit and monitor access to machine-readable discovery endpoints. Logging access patterns to these predictable paths helps detect mass enumeration.

- If using security.txt, include a clear disclosure policy and an abuse/contact email; keep keys updated and validated.

- Always fetch the common .well-known names first: security.txt, openid-configuration, assetlinks.json, webfinger, acme-challenge, change-password.

- Parse machine-readable outputs into your scanner: these are high-quality seeds for targeted enumeration.

- Be careful with CA challenge paths and avoid noisy, inauthentic requests.



Practical exercise: .well-known hands-on:

- 1. Objective: safely extract actionable endpoints from .well-known resources, verify their status, and prioritize follow-ups.

- 2. Prerequisites:

- Use an authorized test domain or a local test server (do NOT run against out-of-scope targets).

- Tools: curl or httpie, jq, a small directory bruteforcer (gobuster or ffuf), and optionally xmllint or python for parsing.

- 3. Step-by-step exercise:

1. Save robots and well-known fetch script scaffold locally:

  Create a directory: mkdir -p ~/recon/well-known && cd ~/recon/well-known

2. Fetch the common .well-known files (replace TARGET with your test host):

  curl -sS -o ./security.txt "https://TARGET/.well-known/security.txt" || true

  curl -sS -o ./openid.json "https://TARGET/.well-known/openid-configuration" || true

  curl -sS -o ./assetlinks.json "https://TARGET/.well-known/assetlinks.json" || true

  curl -sS -o ./webfinger "https://TARGET/.well-known/webfinger" || true

3. Quickly inspect and record what exists:

  ls -l

  grep -i "contact\\|policy\\|Sitemap\\|PGP" ./security.txt || true

  jq -r '.issuer, .authorization_endpoint, .token_endpoint, .userinfo_endpoint' ./openid.json 2>/dev/null || true

4. Normalize and verify endpoints discovered in `openid.json` (if present):

  jq -r 'to_entries[] | select(.key|test("endpoint|url";"i")) | .value' ./openid.json 2>/dev/null | sort -u > ./oidc_endpoints.txt

  while read -r u; do echo "Checking: $u"; curl -s -I -L "$u" | head -n 1; done < ./oidc_endpoints.txt > ./oidc_status.txt || true

5. Check assetlinks and security.txt for referenced hosts and add them to a simple host list:

  jq -r '..|.site?|select(type=="string")' ./assetlinks.json 2>/dev/null | sed 's|https\\?://||' | cut -d'/' -f1 > ./well_known_hosts.txt || true

  grep -Eo "https?://[A-Za-z0-9._:-]+" ./security.txt | sed 's|https\\?://||' | cut -d'/' -f1 >> ./well_known_hosts.txt || true

  sort -u ./well_known_hosts.txt -o ./well_known_hosts.txt || true

6. Perform light, targeted checks on discovered hosts (DNS and simple HTTP status):

  while read -r h; do echo "Host: $h"; host $h || true; curl -s -I -m 10 "https://$h/" | head -n 1 || true; done < ./well_known_hosts.txt > ./hosts_report.txt || true

7. Seed a focused directory check using any Discovered path prefixes (do this only on in-scope hosts):

  # Example using gobuster with a small wordlist

  gobuster dir -u https://TARGET -w ~/wordlists/small.txt -t 20 -s 200,301,302,401,403 -o ./gobuster_well_known.txt || true



Practical exercise expected results:

- security.txt often contains a contact or link pointing to another host; note and add it to enumeration.

- openid-configuration will produce precise endpoints; token and authorization URLs are high-value for auth enumeration.

- assetlinks.json may list mobile app packages and backend hosts; add those hosts to your list.



Challenges:

- Use the `oidc_endpoints.txt` list and check for permissive CORS on the token or userinfo endpoints (read-only checks only).

- Cross-reference hosts in `well_known_hosts.txt` with certificate SANs to find overlap or hidden hosts.



Common recommended safety measures:

- Do not post or use sensitive data found outside scope. Treat any contact information responsibly.

- Keep request volume low; avoid automated credential attacks unless explicitly authorized.

- Store raw files and command outputs to reproduce your steps during reporting."""
    
    # Test with the second section: Creepy Crawlies  
    creepy_crawlies_text = """Creepy Crawlies



Overview:

"Creepy Crawlies" (Web Crawlers and Automated Spiders) refers to automated crawlers and spiders used to enumerate websites: collecting URLs, resources, page content, and link graphs. In reconnaissance they let you scale discovery, uncover hidden paths, harvest parameters, and build target lists quickly. However, crawlers can be noisy and trigger protections — use them with care and always respect scope and rate limits.



Crawler types and their common uses:

- Static crawlers: wget, httrack, curl loops. Fast for static content and simple link graphs, low overhead.

- Recursive directory fuzzers: gobuster, ffuf in recursive mode. Good for uncovering hidden directories and extensions.

- Programmatic frameworks: Scrapy (Python), custom scripts. Flexible extraction, pipelines, and exporters.

- Headless/browser crawlers: Playwright, Puppeteer, Selenium. Necessary when content is rendered client-side with JavaScript.

- Burp/ZAP spiders: integrated with proxies and scanners; useful for interactive exploration and correlation with passive scans.



Common objectives and common outputs:

- Primary outputs: URL lists, link graph, page snapshots (HTML), resource inventory (JS, CSS, images), and extracted parameters.

- Useful export formats: JSON lines, CSV, WARC (archival), HAR (browser-level traffic).

- Success criteria: comprehensive URL list, minimal duplicates, preserved context (referrer, status codes), and a reproducible crawl run.



Basic crawling workflow example:

1. Start conservative: low concurrency, small rate, short depth. Confirm you don't hit defenses.

2. Respect robots.txt and the site's terms; treat Disallow entries as reconnaissance leads, not blockers.

3. Seed the crawler with high-quality entry points: homepage, sitemap, common index pages, known subdomains.

4. Use sitemaps and .well-known endpoints as high-quality seeds rather than blind recursion.

5. Record metadata per URL: status code, content-type, content-length, referrer, snapshot path.



Common recommended measures:

- Rate limits: set crawl-delay and concurrency to avoid DoS and to reduce detection.

- User-Agent: use a descriptive UA string and rotate only when in-scope; some targets block default scanner UAs.

- Time windows: run heavier crawls during agreed windows in your engagement.

- Error handling: back off on 429, 503 and log retries. Respect retry-after headers.

- Keep logs of all commands, timestamps, and raw outputs. Do not flood the target. Escalate if defenses are triggered.



Handling dynamic content and JavaScript:

- Only use headless crawling when needed; rendering increases resource use and noise.

- Strategy: pre-run a static crawl to collect candidate pages, then render only the high-priority paths.

- Capture rendered HTML and HAR files for later offline analysis and precise parameter extraction.



Common crawler issues recommended common measures:

- Infinite calendars, numeric ID ranges, and calendar pagination — detect repeating patterns and limit ranges.

- Session-dependent links (logout, one-time tokens) — avoid following links that contain obvious one-time tokens.

- Redirect loops and mirrors — normalize URLs and maintain a visited set with canonicalization to avoid loops.

- Query parameter explosion — dedupe using sorted parameter keys, or limit parameter permutations per path.



Data enrichment and pipelines:

- Enrich URLs with certificate SANs, resolved IPs, DNS records, robot/sitemap context, and historical snapshots.

- Store crawl outputs in a small database (SQLite) or as ndjson for easy querying and deduplication.

- Post-process to extract parameters, endpoints (APIs), JavaScript endpoints, and interesting file types (.env, .git, .bak searches should be in-scope only).



Common tooling examples (safe, read-only commands):

- wget recursive (careful with recursion depth):

  wget --mirror --convert-links --no-parent --wait=2 --limit-rate=100k https://TARGET/

- httrack quick mirror:

  httrack https://TARGET/ -O ./httrack_target '-* +https://TARGET/*'

- Scrapy (project scaffold) to collect links and export JSON lines:

  scrapy startproject recon

  # create a simple spider that yields request.url and response.status, then run: scrapy crawl target -o urls.jl

- Playwright (node/python) render single page and save HAR/screenshot for an endpoint:

  # Use Playwright to open page, wait for network idle, save HAR and screenshot (see Playwright docs).



Common inputs/outputs, success modes, organizations structure:

- Inputs: seed URLs, crawl depth, rate limits, authentication creds (if in-scope), rendering flag.

- Outputs: URL list (ndjson), crawled resource inventory, status code map, optional HAR/WARC artifacts.

- Error modes: network timeouts, rate limiting, CAPTCHAs, authentication gates. Success = usable, de-duped URL list with context.



Edge cases and common recommended measures:

- Empty or very large sitemaps: treat large sitemaps as prioritized seeds; chunk processing to avoid timeouts.

- CAPTCHAs and WAF blocks: stop further automation when encountering CAPTCHAs; escalate to manual testing.

- Distributed crawling: when scaling, centralize dedupe and throttle per host to avoid accidental overloading.



Practical exercise: Creepy Crawlies lab:

- 1. Objective: run a safe, scoped crawl, collect a deduplicated URL list, and identify 5 interesting endpoints for manual review.

- 2. Prerequisites:

- An authorized test domain or local webserver. Tools: wget, Scrapy (or python requests), jq, and optionally Playwright for JS rendering.

- 3. Exercise steps:

1. Create workspace and seed list:

   mkdir -p ~/recon/creepy && cd ~/recon/creepy

   printf "https://TARGET/\\nhttps://TARGET/sitemap.xml\\n" > seeds.txt

2. Run a conservative wget mirror to fetch the static graph:

   wget --mirror --no-parent --wait=2 --limit-rate=50k -i seeds.txt -P ./raw || true

3. Extract links from downloaded HTML (simple):

   grep -rhoP "href=\\"\\K[^\\"]+" ./raw | sort -u > urls_static.txt || true

4. For each URL, request headers and record status:

   while read -r u; do echo "$u"; curl -s -I -L "$u" | head -n 1; done < urls_static.txt > url_statuses.txt || true

5. Optional: render top 20 URLs with Playwright to capture dynamic endpoints (replace with guidance if not installed).

6. Prioritize URLs that: return 200 and include query parameters, return unexpected content-types (JSON/html mixed), or point to different subdomains. Document 5 leads.



Practical exercise expected results:

- Produce a de-duped URL list, see how static crawling differs from rendered crawling, and identify paths worth manual testing.



Summary:

Crawlers accelerate discovery but bring scale and risk. Use staged crawling (static -> rendered), prioritize seeds, enforce politeness, and pipeline results into structured exports for analysis."""

    breakdowner = TextBreakdown()
    
    print("Task 1.: The section breakdown of - '.Well-Known URIs':")
    result1 = breakdowner.process_text(well_known_text)
    print(breakdowner.format_output(result1))
    
    print("\n\nTask 2.: The section breakdown of - 'Creepy Crawlies':")
    result2 = breakdowner.process_text(creepy_crawlies_text)
    print(breakdowner.format_output(result2))


if __name__ == "__main__":
    main()