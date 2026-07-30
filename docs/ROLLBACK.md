# Rollback runbook — LTM CIS Tech Advisory accelerators

Use when a promoted change to any accelerator is producing wrong output,
a bundler crash, or a legal concern that needs the previous known-good
version restored immediately.

## Prerequisites

- Local clone on branch `claude/cis-tech-advisory-tools-8ngdon` (or `main` once merged).
- AWS credentials for the `ltm-core` bucket in env: `AWS_ACCESS_KEY_ID`,
  `AWS_SECRET_ACCESS_KEY`, `AWS_REGION=us-east-1`.
- The commit SHA that introduced the defect (from `git log` on the file).

## The 3-command rollback

```bash
# 1. Revert the offending commit (creates a new "Revert …" commit).
git revert <bad-sha>

# 2. Re-sync the reverted files to S3.
python scripts/deploy-s3.py --target prod

# 3. Verify the live URL now matches the reverted content.
curl -sI https://ltm-core.s3.us-east-1.amazonaws.com/sovereign-screen.html \
  | grep -i last-modified
```

If the defect spans multiple commits, revert the range instead:
`git revert <oldest-bad-sha>^..<newest-bad-sha>`.

## What if the revert itself won't build?

Some patches (e.g., the readiness-questions injection) depend on prior
patches being present. If reverting one commit leaves the file in a
malformed state, restore the file from a known-good SHA:

```bash
# Find the last commit that touched the file successfully:
git log --oneline -- "path/to/accelerator.html"

# Check out that exact version of the file (keeps other files as-is):
git checkout <good-sha> -- "path/to/accelerator.html"
git commit -m "Rollback accelerator.html to <good-sha>"
python scripts/deploy-s3.py --target prod
```

## Post-rollback

1. Notify Ashutosh Dixit (`ashutosh.dixit@ltm.com`) — subject line:
   `[Rollback] <accelerator name> — reverted to <sha>`.
2. Open a follow-up in the review log
   (`docs/LEGAL-REVIEW.md`) with what went wrong and how it was caught.
3. Fix forward via a new patch to staging; do not re-attempt the same
   promotion until the root cause is fixed and re-reviewed.

## Bucket-versioning note

S3 versioning on `s3://ltm-core` should be enabled so we can restore any
previous object version without a git revert. If it is not yet enabled,
raise it with the AWS admin as the first priority — a bucket without
versioning has no defence against an accidental delete.

Check with:
```bash
aws s3api get-bucket-versioning --bucket ltm-core
# Expect: "Status": "Enabled"
```
