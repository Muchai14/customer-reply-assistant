# Pre-publication credential scan

Gitleaks 8.30.1 reported no findings in the tracked checkout at e9bf2b2 and the
Git history reachable from all locally fetched branches and tags. The clone was
not shallow. Git counted 11 reachable commits; Gitleaks reported 10 scanned
commits (merge commits need not contribute separate diffs). The official release
archive checksum was verified before executing the scanner.

[Machine-readable evidence](reports/pre-publication-secrets.json) records the
version, scope, hash, and empty finding lists. Redaction was enabled. No tracked
.env, database, .pem, or .key filenames were found by the supplementary filename
check. No scanner exclusions or inline allow comments were used to hide findings.

## Reproduce

Use the official Gitleaks 8.30.1 binary from
https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1 and fetch current refs:

```bash
git fetch --all --tags
gitleaks git . --log-opts=--all --redact=100 --ignore-gitleaks-allow --no-banner --report-format json --report-path /tmp/history-secrets.json
```

For current tracked files, export HEAD using git archive into a fresh temporary
directory and run `gitleaks dir` on that directory with the same redaction flags.
Scan reports should first be saved outside the repository and reviewed before
publishing. The current scan used no custom configuration or baseline.

## Decision and limits

No credential finding requires remediation from this scan. This is not a
certificate that the repository contains no sensitive information: detectors
can miss secrets, and source history can include personal metadata such as Git
author names/email or local paths. The owner should decide whether those are
appropriate to publish. Untracked files, unreachable objects, issue discussions,
attachments, and hosting settings were outside this scan.

The repository remains PRIVATE. Its visibility has not been changed. Final
human review, clean-checkout verification, and course-specific audit/peer-review
requirements remain outstanding. Re-run the scan after adding future content.
