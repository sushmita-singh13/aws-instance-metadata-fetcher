import requests
import argparse
import json
import sys

# AWS Metadata Service base URL (IMDSv2)
METADATA_BASE_URL = "http://169.254.169.254/latest/meta-data/"
TOKEN_URL = "http://169.254.169.254/latest/api/token"

# Request timeout in seconds
TIMEOUT = 2


def get_token():
    """Fetch an IMDSv2 token."""
    try:
        response = requests.put(
            TOKEN_URL,
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] Failed to retrieve IMDSv2 token: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_metadata_key(key, token):
    """Fetch a specific metadata key."""
    url = METADATA_BASE_URL + key
    try:
        response = requests.get(
            url,
            headers={"X-aws-ec2-metadata-token": token},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return {key: response.text}
    except requests.HTTPError as e:
        print(f"[ERROR] Failed to retrieve key '{key}': {e}", file=sys.stderr)
        sys.exit(1)


def fetch_all_metadata(token, path=""):
    """Recursively fetch all metadata starting from the given path."""
    url = METADATA_BASE_URL + path
    try:
        response = requests.get(
            url,
            headers={"X-aws-ec2-metadata-token": token},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        items = response.text.splitlines()

        metadata = {}
        for item in items:
            if item.endswith("/"):
                # Recurse into sub-path
                metadata[item.rstrip("/")] = fetch_all_metadata(token, path + item)
            else:
                item_url = METADATA_BASE_URL + path + item
                item_response = requests.get(
                    item_url,
                    headers={"X-aws-ec2-metadata-token": token},
                    timeout=TIMEOUT
                )
                item_response.raise_for_status()
                metadata[item] = item_response.text

        return metadata
    except requests.RequestException as e:
        print(f"[ERROR] Failed to fetch metadata: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Fetch AWS EC2 instance metadata as JSON.")
    parser.add_argument("--key", help="Specific metadata key to fetch", required=False)

    args = parser.parse_args()
    token = get_token()

    if args.key:
        metadata = fetch_metadata_key(args.key, token)
    else:
        metadata = fetch_all_metadata(token)

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
