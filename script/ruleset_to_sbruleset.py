"""
Generate rulesets based on provided configurations.
"""
import os
import json
import logging
import argparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class SBRuleset(dict):
    """
    SBRuleset
    """
    def __init__(self, domain, domain_keyword, domain_suffix, domain_regex, ip_cidr, process_name):
        super().__init__()
        self["version"] = 3
        self["rules"] = []
        rule = {}

        if domain:
            rule["domain"] = list(set(domain))
        if domain_keyword:
            rule["domain_keyword"] = list(set(domain_keyword))
        if domain_suffix:
            rule["domain_suffix"] = list(set(domain_suffix))
        if domain_regex:
            rule["domain_regex"] = list(set(domain_regex))
        if ip_cidr:
            rule["ip_cidr"] = list(set(ip_cidr))
        if process_name:
            rule["process_name"] = list(set(process_name))
        self["rules"].append(rule)


    @classmethod
    def from_yaml(cls, source_file, asn_json_obj=None):
        """
        from_yaml
        """
        domain = []
        domain_keyword = []
        domain_suffix = []
        domain_regex = []
        ip_cidr = []
        process_name = []

        found_payload = False
        with open(source_file, "r", encoding="utf-8") as file:
            for line in file:
                if "payload:" in line.strip():
                    found_payload = True
                    continue
                if not found_payload:
                    continue
                splits = line.strip()[2:].split(",")
                rule_type = splits[0]
                rule_content = splits[1]
                if rule_type == "DOMAIN":
                    domain.append(rule_content)
                elif rule_type == "DOMAIN-SUFFIX":
                    domain_suffix.append("." + rule_content)
                elif rule_type == "DOMAIN-KEYWORD":
                    domain_keyword.append(rule_content)
                elif rule_type == "DOMAIN-REGEX":
                    domain_regex.append(rule_content)
                elif rule_type == "IP-CIDR":
                    ip_cidr.append(rule_content)
                elif rule_type == "IP-ASN":
                    try:
                        ip_cidr.extend(asn_json_obj[rule_content])
                    except KeyError:
                        raise KeyError("No such ASN number " + rule_content + " in GeoLite2-ASN-CSV, Please consider to remove in the customization list.")
                elif rule_type == "PROCESS-NAME":
                    process_name.append(rule_content)
                else:
                    logging.warning("Unknown rule type %s", rule_type)

        return cls(domain, domain_keyword, domain_suffix, domain_regex, ip_cidr, process_name)

    @classmethod
    def from_txt(cls, source_file, asn_json_obj=None):
        """
        from_txt
        """
        domain = []
        domain_keyword = []
        domain_suffix = []
        domain_regex = []
        ip_cidr = []
        process_name = []

        with open(source_file, "r", encoding="utf-8") as file:
            for line in file:
                if len(line.strip()) == 0:
                    continue
                if line.startswith("#"):
                    continue
                splits = line.strip().split(",")
                rule_type = splits[0]
                rule_content = splits[1]
                if rule_type == "DOMAIN":
                    domain.append(rule_content)
                elif rule_type == "DOMAIN-SUFFIX":
                    domain_suffix.append("." + rule_content)
                elif rule_type == "DOMAIN-KEYWORD":
                    domain_keyword.append(rule_content)
                elif rule_type == "DOMAIN-REGEX":
                    domain_regex.append(rule_content)
                elif rule_type == "IP-CIDR":
                    ip_cidr.append(rule_content)
                elif rule_type == "IP-ASN":
                    try:
                        ip_cidr.extend(asn_json_obj[rule_content])
                    except KeyError:
                        raise KeyError("No such ASN number " + rule_content + " in GeoLite2-ASN-CSV, Please consider to remove in the customization list.")
                elif rule_type == "PROCESS-NAME":
                    process_name.append(rule_content)
                elif rule_type == "USER-AGENT":
                    pass
                else:
                    logging.warning("Unknown rule type %s", rule_type)

        return cls(domain, domain_keyword, domain_suffix, domain_regex, ip_cidr, process_name)

    @classmethod
    def create_from_source(cls, source_path, asn_json_path=None):
        """
        create_from_source
        """
        with open(asn_json_path, "r", encoding="utf-8") as f:
            asn_json_obj = json.load(f)
        _, ext = os.path.splitext(source_path)
        source_type = ext[1:]  # Get file extension without dot
        if source_type in ("yaml", "yml"):
            return cls.from_yaml(source_path, asn_json_obj)
        if source_type == "txt":
            return cls.from_txt(source_path, asn_json_obj)
        raise ValueError("Unsupported file format")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process ASN data and generate ruleset.")
    parser.add_argument("--input", type=str, required=True, help="Input file path")
    parser.add_argument("--asn_json", type=str, required=True, help="asn json file path")
    parser.add_argument("--output", type=str, required=True, help="Output file path.")
    args = parser.parse_args()

    sbr = SBRuleset.create_from_source(source_path=args.input, asn_json_path=args.asn_json)

    with open(args.output, "w", encoding="utf-8") as file_json:
        json.dump(sbr, file_json, indent=2, sort_keys=True, ensure_ascii=False)
        file_json.write("\n")
