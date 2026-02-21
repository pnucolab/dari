#!/usr/bin/env python3
import subprocess
import time
import os

def run_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def clean_rules(ip_addresses):
    current_ips = run_command("iptables -t nat -L POSTROUTING -n | grep 10.8.0.0 | grep -v dpt | tr -s ' ' | cut -d ' ' -f 5")
    if current_ips is None:
        print(f"Failed to get current rules.")
    for ip_address in current_ips.split('\n'):
        if not ip_address in ip_addresses:
            if run_command(f"iptables -t nat -D POSTROUTING -s 10.8.0.0/24 -d {ip_address}/32 -o eth0 -j MASQUERADE"):
                print(f"Deleted rule for IP: {ip_address}")
            else:
                print(f"Failed to delete rule for IP: {ip_address}")

def check_and_add_rule(ip_address):
    # Check if the rule already exists
    check_cmd = f"iptables -t nat -C POSTROUTING -s 10.8.0.0/24 -d {ip_address}/32 -o eth0 -j MASQUERADE"
    if run_command(check_cmd) is None:
        # Rule doesn't exist, so add it
        add_cmd = f"iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -d {ip_address}/32 -o eth0 -j MASQUERADE"
        if run_command(add_cmd) is None:
            print(f"Added rule for IP: {ip_address}")
        else:
            print(f"Failed to add rule for IP: {ip_address}")
    else:
        print(f"Rule already exists for IP: {ip_address}")

def read_ip_addresses(file_path):
    import yaml
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file) or {}
            return config.get('ip_addresses', [])
    except FileNotFoundError:
        print(f"Config file not found: {file_path}")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return []

def main(ip_file):
    print(f"Starting iptables rule check for IPs in file: {ip_file}")
    while True:
        ip_addresses = read_ip_addresses(ip_file)
        clean_rules(ip_addresses)
        for ip in ip_addresses:
            check_and_add_rule(ip)
        time.sleep(10)  # Wait for 10 seconds before the next check

if __name__ == "__main__":
    ip_file = os.environ.get('IP_FILE', '/etc/ip_addresses/conf.yml')
    main(ip_file)