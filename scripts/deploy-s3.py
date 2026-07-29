#!/usr/bin/env python3
"""Sync LTM assets to S3.

Reads bucket + file list from deploy.config.json.
Credentials come from environment: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
(never from the repo). Region can be overridden with AWS_REGION.
"""
import json
import os
import sys
import pathlib
import boto3
from botocore.exceptions import ClientError

ROOT = pathlib.Path(__file__).resolve().parent.parent
CFG = json.loads((ROOT / "deploy.config.json").read_text())

bucket = CFG["bucket"]
region = os.environ.get("AWS_REGION") or CFG.get("region", "us-east-1")
default_acl = CFG.get("defaultAcl", "private")

s3 = boto3.client("s3", region_name=region)

def upload(src_rel: str, key: str, content_type: str, acl: str) -> None:
    src = ROOT / src_rel
    if not src.exists():
        print(f"  ! missing: {src_rel}")
        return
    extra = {"ContentType": content_type, "CacheControl": "public, max-age=300"}
    if acl:
        extra["ACL"] = acl
    with src.open("rb") as fh:
        s3.put_object(Bucket=bucket, Key=key, Body=fh, **extra)
    print(f"  ✓ {src_rel}  →  s3://{bucket}/{key}")

def main() -> int:
    print(f"Deploying to s3://{bucket}  (region={region})")
    for item in CFG["files"]:
        upload(
            item["src"],
            item["key"],
            item.get("contentType", "application/octet-stream"),
            item.get("acl", default_acl),
        )
    print("Done.")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except ClientError as e:
        print(f"AWS error: {e}", file=sys.stderr)
        sys.exit(1)
