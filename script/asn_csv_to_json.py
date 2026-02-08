"""
This module processes ASN data
"""
import json
import csv
import argparse
from collections import defaultdict

def add_asn_csv_to_asn_dict(asn_dict, asn_csv):
    """
        process_asn_csv
    """
    with open(asn_csv, mode="r", encoding="utf-8") as file_asn:
        csv_reader = csv.reader(file_asn, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            if not row or len(row) < 2:
                continue
            asn_dict[int(row[1])].append(row[0])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process ASN csv data and generate json.")
    parser.add_argument("--input_asn_files", type=str, required=True, help="input asn csv file path")
    parser.add_argument("--output_asn_json", type=str, required=True, help="output asn json file path")
    args = parser.parse_args()

    asn_json = defaultdict(list)
    for asn_file in args.input_asn_files.split(","):
        add_asn_csv_to_asn_dict(asn_dict=asn_json, asn_csv=asn_file)

    with open(args.output_asn_json, "w", encoding="utf-8") as file_json:
        json.dump(asn_json, file_json, indent=2, sort_keys=True, ensure_ascii=False)
        file_json.write("\n")
