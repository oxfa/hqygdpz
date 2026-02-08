import argparse

def split_line(line):
    if "," not in line:
        raise ValueError("Invalid content detected:" + line)
    exp_type, expression = line.split(",", 1)
    return exp_type, expression

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
            if exp_type == "DOMAIN-KEYWORD":
                lines_file = [line for line in lines_file if expression not in split_line(line)[1]]
            elif exp_type == "DOMAIN-SUFFIX":
                lines_file = [line for line in lines_file if not (line.endswith("." + expression) or line.endswith("," + expression))]
            else:
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
