#!/usr/bin/env python
"""
Generate mhm format (txt and yaml) for fakeip_filter.txt in domain mode.

Domain mode format: lists domain patterns directly without rule type prefixes.
This differs from classical mode which uses prefixes like DOMAIN, DOMAIN-SUFFIX.

Input: customization/fakeip_filter.txt (DNS filter format with special prefixes)
Output:
  - release/mhm/rule-provider/txt/fakeip_filter.txt (one domain per line)
  - release/mhm/rule-provider/yaml/fakeip_filter.yaml (yaml payload format)
"""

import argparse

def extract_domains(input_file):
    """
    Extract domain patterns from fakeip_filter.txt format.
    
    Skips:
    - Comment lines (starting with #)
    - Empty lines
    
    Returns:
    - List of domain pattern strings
    """
    domains = []
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Skip comment lines
                if line.startswith('#'):
                    continue
                
                # Add the domain pattern as-is
                domains.append(line)
    except FileNotFoundError:
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    return domains


def generate_txt_format(domains):
    """
    Generate domain mode txt format (one domain per line).
    
    Args:
        domains: List of domain pattern strings
    
    Returns:
        String content for txt file
    """
    return '\n'.join(domains) + ('\n' if domains else '')


def generate_yaml_format(domains):
    """
    Generate domain mode yaml format with payload section.
    
    All domain entries are single-quoted to ensure they are treated as literal strings
    and to escape special characters like *, +, etc.
    
    Args:
        domains: List of domain pattern strings
    
    Returns:
        String content for yaml file
    """
    if not domains:
        return "payload:\n"
    
    lines = ["payload:"]
    for domain in domains:
        # Single-quote domains to ensure special characters are preserved
        lines.append(f"  - '{domain}'")
    
    return '\n'.join(lines) + '\n'


def generate_sr_format(domains):
    """
    Generate sr host list format.
    
    Conversion logic from mhm Wildcard to sr:
    1. * -> Skip (mhm match-all is different from sr behavior)
    2. .example.com -> *.example.com (mhm multi-level subdomains only, no domain)
    3. +.example.com -> *example.com (mhm domain + multi-level subdomains)
    4. *.example.com -> *.example.com (mhm single-level vs sr greedy wildcard)
    5. example.com -> example.com (Exact match)
    
    Args:
        domains: List of domain pattern strings from mhm format
    
    Returns:
        String content for sr host list
    """
    sr_domains = []
    for domain in domains:
        if domain == "*":
            # 1. * -> nothing
            continue
        elif domain.startswith("."):
            # 2. .example.com -> *.example.com
            sr_domains.append("*." + domain[1:])
        elif domain.startswith("+."):
            # 3. +.example.com -> *example.com
            sr_domains.append("*" + domain[2:])
        elif domain.startswith("*."):
            # 4. *.example.com -> *.example.com
            sr_domains.append(domain)
        else:
            # 5. example.com -> example.com (and internal wildcards like time.*.com)
            sr_domains.append(domain)
    
    return '\n'.join(sr_domains) + ('\n' if sr_domains else '')


def main():
    parser = argparse.ArgumentParser(
        description="Generate mhm format files for fakeip_filter in domain mode"
    )
    parser.add_argument(
        "input_file",
        help="Input file (customization/fakeip_filter.txt)"
    )
    parser.add_argument(
        "-mt",
        "--mhm_txt",
        help="Output txt file (default: release/mhm/rule-provider/txt/fakeip_filter.txt)"
    )
    parser.add_argument(
        "-my",
        "--mhm_yaml",
        help="Output yaml file (default: release/mhm/rule-provider/yaml/fakeip_filter.yaml)"
    )
    parser.add_argument(
        "-st",
        "--sr_txt",
        help="Output sr txt file (default: release/sr/rule-set/fakeip_filter.txt)"
    )
    
    args = parser.parse_args()
    
    # Extract domains from input file
    domains = extract_domains(args.input_file)

    
    # Ensure output directories exist
    # os.makedirs(os.path.dirname(mhm_txt), exist_ok=True)
    # os.makedirs(os.path.dirname(mhm_yaml), exist_ok=True)
    
   
    # Generate and save formats
    if args.mhm_txt:
        with open(args.mhm_txt, 'w', encoding='utf-8') as f:
            f.write(generate_txt_format(domains))
    
    if args.sr_txt:
        with open(args.sr_txt, 'w', encoding='utf-8') as f:
            f.write(generate_sr_format(domains))
            
    if args.mhm_yaml:
        with open(args.mhm_yaml, 'w', encoding='utf-8') as f:
            f.write(generate_yaml_format(domains))
    
    return 0


if __name__ == '__main__':
    exit(main())
