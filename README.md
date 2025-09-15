# AWS Instance Metadata Fetcher (Single Key)

A Python script to fetch a **single metadata key** from an **AWS EC2 instance** using the **IMDSv2** protocol. The output is JSON formatted.

This script is ideal for use inside EC2 instances or as part of CI/CD pipelines running within AWS infrastructure.

---

## Features

- Fetches a single EC2 metadata key (e.g., `instance-id`)
- Uses AWS IMDSv2 (Instance Metadata Service v2) with token-based authentication
- Lightweight (no recursion, minimal code)
- Works with GitLab CI/CD or local execution on EC2

---

## Parameters
| Parameter     | Required | Description                                                                   |
| ------------- | -------- | ----------------------------------------------------------------------------- |
| `--key`       | Yes      | The specific metadata key to fetch (e.g. `instance-id`)                       |
| `--base-url`  | Yes      | Base URL for EC2 metadata                                                     |
| `--token-url` | Yes      | Token URL for IMDSv2                                                          |



