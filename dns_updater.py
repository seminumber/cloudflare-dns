import argparse
import os
import sys

import requests


def get_current_ip():
    # Function to get the current public IP address
    try:
        response = requests.get("https://api.ipify.org")
        if response.status_code == 200:
            return response.text
        else:
            print("Failed to retrieve IP address.")
            return None
    except Exception as e:
        print("Error:", e)
        return None


def update_dns_record(api_key, zone_id, record_name):
    # Function to update DNS record with the current IP address using Cloudflare API
    current_ip = get_current_ip()
    if current_ip:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
        params = {"name": record_name, "type": "A"}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            dns_records = response.json()["result"]
            if dns_records:
                record_id = dns_records[0]["id"]
                update_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
                update_data = {"type": "A", "name": record_name, "content": current_ip}
                update_response = requests.put(
                    update_url, headers=headers, json=update_data
                )
                if update_response.status_code == 200:
                    print("DNS record updated successfully.")
                else:
                    print("Failed to update DNS record:", update_response.json())
            else:
                print("No DNS records found for the specified name.")
        else:
            print("Failed to fetch DNS records:", response.json())
    else:
        print("Failed to retrieve current IP address.")


# Set your Cloudflare API key, Zone ID, and DNS record name
API_KEY = os.environ.get("CLOUDFLARE_API_KEY")
ZONE_ID = "23235e355f09269206d50adec1f88f96"
DEFAULT_RECORD_NAME = "server.junsoo.kr"  # Change this to your DNS record name


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("--record-name", default=DEFAULT_RECORD_NAME)
    parser.add_argument("--api-key", default=API_KEY)
    args = parser.parse_args(argv)

    if args.api_key is None:
        raise ValueError("Environment variable CLOUDFLARE_API_KEY not set.")

    # Call the function to update DNS record
    update_dns_record(args.api_key, ZONE_ID, args.record_name)


if __name__ == "__main__":
    main()
