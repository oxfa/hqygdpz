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
import os


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
    
    Args:
        domains: List of domain pattern strings
    
    Returns:
        String content for yaml file
    """
    if not domains:
        return "payload:\n"
    
    lines = ["payload:"]
    for domain in domains:
        lines.append(f"  - {domain}")
    
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(
        description="Generate mhm format files for fakeip_filter in domain mode"
    )
    parser.add_argument(
        "input_file",
        help="Input file (customization/fakeip_filter.txt)"
    )
    parser.add_argument(
        "-txt",
        "--output_txt",
        help="Output txt file (default: release/mhm/rule-provider/txt/fakeip_filter.txt)"
    )
    parser.add_argument(
        "-yaml",
        "--output_yaml",
        help="Output yaml file (default: release/mhm/rule-provider/yaml/fakeip_filter.yaml)"
    )
    
    args = parser.parse_args()
    
    # Extract domains from input file
    domains = extract_domains(args.input_file)
    
    # Determine output file paths
    output_txt = args.output_txt or os.path.join(
        os.path.dirname(args.input_file),
        '..',
        'release',
        'mhm',
        'rule-provider',
        'txt',
        'fakeip_filter.txt'
    )
    
    output_yaml = args.output_yaml or os.path.join(
        os.path.dirname(args.input_file),
        '..',
        'release',
        'mhm',
        'rule-provider',
        'yaml',
        'fakeip_filter.yaml'
    )
    
    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_txt), exist_ok=True)
    os.makedirs(os.path.dirname(output_yaml), exist_ok=True)
    
    # Write txt format
    txt_content = generate_txt_format(domains)
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    print(f"✓ Generated {output_txt} ({len(domains)} domains)")
    
    # Write yaml format
    yaml_content = generate_yaml_format(domains)
    with open(output_yaml, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    print(f"✓ Generated {output_yaml} ({len(domains)} domains)")
    
    return 0


if __name__ == '__main__':
    exit(main())
