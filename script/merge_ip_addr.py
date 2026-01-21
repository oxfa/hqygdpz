#!/usr/bin/env python3
import sys
import re
import ipaddress


def load_networks(lines):
    """Parse an iterable of input lines into a list of ipaddress network objects.

    This function is forgiving: it strips surrounding quotes, removes inline
    comments (text after '#'), and accepts multiple tokens per line separated
    by whitespace or commas.
    """
    nets = []
    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        # remove surrounding quotes
        line = line.strip('"\'')
        # drop inline comments
        line = line.split('#', 1)[0].strip()
        if not line:
            continue
        # split possible multiple entries on whitespace or commas
        tokens = re.split(r'[\s,]+', line)
        for token in tokens:
            if not token:
                continue
            try:
                if '/' in token:
                    net = ipaddress.ip_network(token, strict=False)
                else:
                    addr = ipaddress.ip_address(token)
                    net = ipaddress.ip_network(f"{addr}/{addr.max_prefixlen}", strict=False)
                nets.append(net)
            except ValueError as e:
                print(f"Skipping invalid entry {token!r}: {e}", file=sys.stderr)
    return nets

def merge_and_print(nets):
    v4 = [n for n in nets if isinstance(n, ipaddress.IPv4Network)]
    v6 = [n for n in nets if isinstance(n, ipaddress.IPv6Network)]
    for net in ipaddress.collapse_addresses(v4):
        print(net)
    for net in ipaddress.collapse_addresses(v6):
        print(net)

def main():
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                lines = f.readlines()
        except IOError as e:
            sys.exit(f"Error opening {sys.argv[1]}: {e}")
    else:
        lines = sys.stdin  # this is fine for line iteration in Python

    networks = load_networks(lines)
    if not networks:
        sys.exit("No valid IPs or CIDRs found.")
    merge_and_print(networks)

if __name__ == "__main__":
    main()
