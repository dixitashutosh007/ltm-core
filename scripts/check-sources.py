#!/usr/bin/env python3
"""Health-check every source URL cited in the Sovereign Screen KB.

Extracts each regime's sources[{name,url}] array from the bundled HTML,
HEADs every URL, reports any 4xx / 5xx as a failure.

Exit code 0 if all URLs are healthy, 1 if any failed. Designed to be
invoked by .github/workflows/source-url-health.yml on a monthly cron and
on any change to the Sovereign Screen HTML.
"""
import argparse
import codecs
import concurrent.futures
import re
import sys
import urllib.request
from pathlib import Path

DEFAULT_FILE = Path("/home/user/ltm-core/Data-Sovereignty-Value-Case-Tool/Sovereign Screen (standalone).html")


def extract_sources(html_path: Path) -> list[tuple[str, str, str]]:
    """Return list of (regime_id, source_name, url)."""
    raw = html_path.read_text(encoding="utf-8")
    d = codecs.decode(raw, "unicode_escape", errors="ignore")

    # For each regime block, capture id and its sources array
    out = []
    for regime_m in re.finditer(r'\{id:"([a-z_0-9]+)", name:"[^"]+",[^}]*?sources:\[(.*?)\]', d, re.DOTALL):
        regime_id = regime_m.group(1)
        sources_block = regime_m.group(2)
        for src_m in re.finditer(r'\{name:"([^"]+)",url:"([^"]+)"\}', sources_block):
            out.append((regime_id, src_m.group(1), src_m.group(2)))
    return out


def check_url(url: str, timeout: float = 10.0) -> tuple[int, str]:
    """HEAD the URL; return (http_status, error_str). status 0 = network error."""
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "LTM-source-check/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        # Some servers reject HEAD but accept GET; try GET as a fallback for 405
        if e.code in (405, 501):
            try:
                req = urllib.request.Request(url, method="GET",
                                             headers={"User-Agent": "LTM-source-check/1.0"})
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    return r.status, ""
            except Exception as e2:
                return getattr(e2, "code", 0), str(e2)
        return e.code, str(e)
    except Exception as e:
        return 0, str(e)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default=str(DEFAULT_FILE),
                        help="Path to Sovereign Screen HTML (default: bundled prod file)")
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    sources = extract_sources(Path(args.file))
    if not sources:
        print("ERROR: no sources extracted — regex may be wrong for this file version", file=sys.stderr)
        return 2

    print(f"Checking {len(sources)} source URLs across {len({r for r,_,_ in sources})} regimes...\n")

    failures: list[tuple[str, str, str, int, str]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        futures = {ex.submit(check_url, url, args.timeout): (rid, name, url)
                   for rid, name, url in sources}
        for f in concurrent.futures.as_completed(futures):
            rid, name, url = futures[f]
            status, err = f.result()
            ok = 200 <= status < 400
            mark = "✓" if ok else "✗"
            print(f"  {mark}  [{status or 'ERR':>3}]  {rid:22}  {url}")
            if not ok:
                failures.append((rid, name, url, status, err))

    print()
    if failures:
        print(f"FAILED — {len(failures)} broken URL(s):")
        for rid, name, url, status, err in failures:
            print(f"  {rid}  ·  {name}")
            print(f"     {url}")
            print(f"     status={status}  {err}")
        return 1

    print(f"OK — all {len(sources)} source URLs healthy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
