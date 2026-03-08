import argparse

def split_line(line):
    if "," not in line:
        raise ValueError("Invalid content detected:" + line)
    exp_type, expression = line.split(",", 1)
    return exp_type, expression

def parse_domain_suffix_entry(line):
    """
    Parse a DOMAIN-SUFFIX entry with optional strategy suffix.
    
    NOTE: Strategy configuration (exact/cascade) is ONLY supported for DOMAIN-SUFFIX and DOMAIN-KEYWORD
          entries in customization files (# REMOVE sections). This is NOT supported for DOMAIN entries.
    
    Format: DOMAIN-SUFFIX,expression or DOMAIN-SUFFIX,expression:strategy
    
    Args:
        line: A line string like "DOMAIN-SUFFIX,example.com" or "DOMAIN-SUFFIX,example.com:cascade"
    
    Strategy choices:
        - "exact" (default): Remove only DOMAIN-SUFFIX entries where expression matches exactly
        - "cascade": Remove DOMAIN entries ending with suffix AND DOMAIN-SUFFIX entries matching suffix/subdomains
    
    Returns:
        Tuple of (expression, strategy) where strategy is "exact" or "cascade"
        Example: "DOMAIN-SUFFIX,example.com:cascade" -> ("example.com", "cascade")
                 "DOMAIN-SUFFIX,example.com" -> ("example.com", "exact")
    
    Raises:
        ValueError: If strategy is invalid or not in ["exact", "cascade"]
    """
    if "," not in line:
        raise ValueError("Invalid DOMAIN-SUFFIX entry: " + line)
    
    _, domain_part = line.split(",", 1)
    
    # Check if there's a strategy suffix
    if ":" in domain_part:
        expression, strategy = domain_part.rsplit(":", 1)
        strategy = strategy.strip()
        
        # Check for empty strategy first
        if not strategy:  # Empty strategy (e.g., "example.com:")
            raise ValueError(f"Empty strategy in line: {line}. Must specify 'exact' or 'cascade'.")
        
        # Validate strategy is one of the allowed values
        if strategy not in ["exact", "cascade"]:
            raise ValueError(f"Invalid strategy '{strategy}' in line: {line}. Must be 'exact' or 'cascade'.")
    else:
        expression = domain_part
        strategy = "exact"  # Default strategy
    
    return expression.strip(), strategy

def remove_domain_suffix_entry(lines_file, expression, strategy, entry_type="DOMAIN-SUFFIX"):
    """
    Remove DOMAIN-SUFFIX entries based on strategy.
    
    NOTE: Strategy configuration (exact/cascade) is ONLY supported for DOMAIN-SUFFIX and DOMAIN-KEYWORD
          entries in customization files (# REMOVE sections). Other entry types use simple matching.
    
    Args:
        lines_file: List of rule lines to filter
        expression: Domain expression (without DOMAIN-SUFFIX prefix)
        strategy: "exact" or "cascade" (only for DOMAIN-SUFFIX in customization files)
                  - "exact": Remove only lines where type matches AND expression matches exactly
                  - "cascade": Remove matching DOMAIN entries AND DOMAIN-SUFFIX entries with suffix/subdomain matching
        entry_type: The type to match (default "DOMAIN-SUFFIX"). Type must match for removal.
    
    Returns:
        Filtered lines_file based on strategy
    """
    if strategy == "exact":
        # Remove only lines where type matches AND expression matches exactly
        return [line for line in lines_file if not (split_line(line)[0] == entry_type and line.endswith("," + expression))]
    elif strategy == "cascade":
        # Remove DOMAIN entries ending with expression, and DOMAIN-SUFFIX entries matching expression or subdomains
        filtered = []
        for line in lines_file:
            line_type, line_expr = split_line(line)
            
            # Remove DOMAIN entries ending with the expression (e.g., "DOMAIN,sub.example.com" matches "example.com")
            if line_type == "DOMAIN" and (line_expr.endswith("." + expression) or line_expr == expression):
                continue
            
            # Remove DOMAIN-SUFFIX entries matching expression or subdomains
            if line_type == "DOMAIN-SUFFIX" and (line.endswith("." + expression) or line.endswith("," + expression)):
                continue
            
            filtered.append(line)
        return filtered
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

def parse_domain_keyword_entry(line):
    """
    Parse a DOMAIN-KEYWORD entry with optional strategy suffix.
    
    NOTE: Strategy configuration (exact/cascade) is ONLY supported for DOMAIN-SUFFIX and DOMAIN-KEYWORD
          entries in customization files (# REMOVE sections). This is NOT supported for DOMAIN entries.
    
    Format: DOMAIN-KEYWORD,expression or DOMAIN-KEYWORD,expression:strategy
    
    Args:
        line: A line string like "DOMAIN-KEYWORD,google" or "DOMAIN-KEYWORD,google:cascade"
    
    Strategy choices:
        - "exact" (default): Remove only DOMAIN-KEYWORD entries where expression matches exactly
        - "cascade": Remove DOMAIN, DOMAIN-SUFFIX, and DOMAIN-KEYWORD entries containing keyword as substring
    
    Returns:
        Tuple of (expression, strategy) where strategy is "exact" or "cascade"
        Example: "DOMAIN-KEYWORD,google:cascade" -> ("google", "cascade")
                 "DOMAIN-KEYWORD,google" -> ("google", "exact")
    
    Raises:
        ValueError: If strategy is invalid or not in ["exact", "cascade"]
    """
    if "," not in line:
        raise ValueError("Invalid DOMAIN-KEYWORD entry: " + line)
    
    _, keyword_part = line.split(",", 1)
    
    # Check if there's a strategy suffix
    if ":" in keyword_part:
        expression, strategy = keyword_part.rsplit(":", 1)
        strategy = strategy.strip()
        
        # Check for empty strategy first
        if not strategy:  # Empty strategy (e.g., "google:")
            raise ValueError(f"Empty strategy in line: {line}. Must specify 'exact' or 'cascade'.")
        
        # Validate strategy is one of the allowed values
        if strategy not in ["exact", "cascade"]:
            raise ValueError(f"Invalid strategy '{strategy}' in line: {line}. Must be 'exact' or 'cascade'.")
    else:
        expression = keyword_part
        strategy = "exact"  # Default strategy
    
    return expression.strip(), strategy

def remove_domain_keyword_entry(lines_file, expression, strategy, entry_type="DOMAIN-KEYWORD"):
    """
    Remove DOMAIN-KEYWORD entries based on strategy.
    
    NOTE: Strategy configuration (exact/cascade) is ONLY supported for DOMAIN-SUFFIX and DOMAIN-KEYWORD
          entries in customization files (# REMOVE sections). Other entry types use simple matching.
    
    Args:
        lines_file: List of rule lines to filter
        expression: Keyword expression (without DOMAIN-KEYWORD prefix)
        strategy: "exact" or "cascade" (only for DOMAIN-KEYWORD in customization files)
                  - "exact": Remove only lines where type matches AND expression matches exactly
                  - "cascade": Remove DOMAIN, DOMAIN-SUFFIX, and DOMAIN-KEYWORD entries containing keyword as substring
        entry_type: The type to match (default "DOMAIN-KEYWORD"). Type must match for removal.
    
    Returns:
        Filtered lines_file based on strategy
    """
    if strategy == "exact":
        # Remove only entries where type matches AND expression matches exactly
        return [line for line in lines_file if not (split_line(line)[0] == entry_type and split_line(line)[1] == expression)]
    elif strategy == "cascade":
        # Remove DOMAIN, DOMAIN-SUFFIX, and DOMAIN-KEYWORD entries containing keyword as substring
        filtered = []
        for line in lines_file:
            line_type, line_expr = split_line(line)
            
            # Remove if keyword appears as substring in any of DOMAIN, DOMAIN-SUFFIX, or DOMAIN-KEYWORD
            if line_type in ("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD") and expression in line_expr:
                continue
            
            filtered.append(line)
        return filtered
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

def process_file(inputFile, patchFile, mode):
    add_lines = []
    remove_lines = set()
    current_section = None

    with open(inputFile, "r") as fd_file:
        lines_file = [line.strip() for line in fd_file.read().splitlines() if line.strip() and not line.strip().startswith("#")]
    if mode in ("add_and_remove", "remove_from_adding_list"):
        with open(patchFile, "r") as file_patch:
            lines_patch = [line.strip() for line in file_patch.read().splitlines() if line.strip() and not line.strip().startswith("##")]
            for line_patch in lines_patch:
                if line_patch == "# ADD":
                    current_section = "add"
                elif line_patch == "# REMOVE":
                    current_section = "remove"
                else:
                    if current_section == "add":
                        if mode == "remove_from_adding_list":
                            remove_lines.add(line_patch)
                        else:
                            # add_and_remove case
                            exp_type, expression = split_line(line_patch)
                            if all(split_line(line_file)[1] != expression for line_file in lines_file):
                                add_lines.append(line_patch)
                    elif current_section == "remove":
                        if mode == "add_and_remove":
                            remove_lines.add(line_patch)
                        else:
                            # this case for remove_from_adding_list mode when some pathFiles have # REMOVE section
                            break
                    else:
                        pass

        for remove_line in remove_lines:
            exp_type, expression = split_line(remove_line)
            # NOTE: Only DOMAIN-SUFFIX and DOMAIN-KEYWORD support exact/cascade strategy modes.
            # Strategy configuration: "expression" or "expression:exact" (default) or "expression:cascade"
            # Other entry types (e.g., DOMAIN) use simple exact-match removal only.
            if exp_type == "DOMAIN-KEYWORD":
                parsed_expr, strategy = parse_domain_keyword_entry(remove_line)
                lines_file = remove_domain_keyword_entry(lines_file, parsed_expr, strategy, exp_type)
            elif exp_type == "DOMAIN-SUFFIX":
                parsed_expr, strategy = parse_domain_suffix_entry(remove_line)
                lines_file = remove_domain_suffix_entry(lines_file, parsed_expr, strategy, exp_type)
            else:
                # For other entry types (e.g., DOMAIN): simple exact-match removal (no strategy options)
                lines_file = [line for line in lines_file if expression != split_line(line)[1]]
        lines_file.extend(add_lines)
    elif mode == "remove_redundancy":
        domain_lines = [line for line in lines_file if split_line(line)[0] == "DOMAIN"]
        domain_suffix_lines = [line for line in lines_file if split_line(line)[0] == "DOMAIN-SUFFIX"]
        for line in domain_lines:
            _, domain = split_line(line)
            domain_parts = domain.split(".")
            for i in range(len(domain_parts)):
                subdomain = ".".join(domain_parts[i:])
                if "DOMAIN-SUFFIX," + subdomain in domain_suffix_lines:
                    lines_file.remove(line)
                    break
    else:
        pass
    with open(inputFile, "w") as fd_file:
        fd_file.write("\n".join(lines_file) + "\n" if lines_file else "")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputFile", help="input file")
    parser.add_argument("-p", "--patchFile", help="customization file", default=None)
    # TODO Do type check
    parser.add_argument("-m", "--mode", help="mode")
    args = parser.parse_args()

    process_file(args.inputFile, args.patchFile, args.mode)
