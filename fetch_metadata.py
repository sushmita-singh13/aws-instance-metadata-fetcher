import requests
import argparse
import json
import sys

TIMEOUT = 2


def get_token(token_url):
    """Fetch an IMDSv2 token."""
    try:
        response = requests.put(
            token_url,
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"[ERROR] Failed to retrieve IMDSv2 token: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_metadata_key(base_url, key, token):
    """Fetch a specific metadata key."""
    url = base_url.rstrip("/") + "/" + key
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


def fetch_all_metadata(base_url, token, path=""):
    """Recursively fetch all metadata starting from the given path."""
    url = base_url.rstrip("/") + "/" + path
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
                metadata[item.rstrip("/")] = fetch_all_metadata(base_url, token, path + item)
            else:
                item_url = base_url.rstrip("/") + "/" + path + item
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
    parser.add_argument("--base-url", help="Base URL for metadata service", required=True)
    parser.add_argument("--token-url", help="URL to fetch the IMDSv2 token", required=True)

    args = parser.parse_args()

    token = get_token(args.token_url)

    if args.key:
        metadata = fetch_metadata_key(args.base_url, args.key, token)
    else:
        metadata = fetch_all_metadata(args.base_url, token)

    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
