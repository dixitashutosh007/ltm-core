#!/usr/bin/env python3
"""FinOps Maturity Screen — Phase 1 patch (legal defensibility).

Implements the 3 Phase 1 items from docs/FMS-REVIEW.md §5:

  P1.1  FinOps Foundation trademark disclaimer appended to
        meta.disclaimer (non-affiliation notice).
  P1.2  C1 reframed from an MFA / security-posture question into an
        account-ownership + access-model FinOps question. Retains
        critical:true, weight:2, stage:chaos, domain:governance.
  P1.3  Framework version + reviewed date stamp on the report cover
        (mono strip under the covermeta grid).

Idempotent: each edit checks whether it has already been applied.

Deploys to finops-screen-staging.html only. Prod (finops-screen.html)
is untouched by this script; promotion happens via
`deploy-s3.py --target prod` after legal sign-off.

Same bundler pattern as FVC (plain JSON __bundler/template — not
gzipped like DR&J). Guards: json_safety_check + node --check on inline
scripts + semantic marker sweep.
"""
import argparse
import json
import pathlib
import re
import sys

FILE = pathlib.Path(
    "/home/user/ltm-core/FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html"
)

# ---------------------------------------------------------------------------
# P1.1 — TM / non-affiliation notice appended to disclaimer
# ---------------------------------------------------------------------------
EDIT_DISCLAIMER = (
    r'disclaimer:\"Indicative maturity screen based on self-reported inputs. Scores reflect the responses given and are intended to prioritise action, not to certify compliance or guarantee savings.\"',
    r"disclaimer:\"Indicative maturity screen based on self-reported inputs. Scores reflect the responses given and are intended to prioritise action, not to certify compliance or guarantee savings. Aligned to FinOps Framework references. Not an official FinOps Foundation assessment or certification. 'FinOps' is a trademark of the FinOps Foundation.\"",
)

# ---------------------------------------------------------------------------
# P1.2 — C1 reframed. Text + options + remediation all replaced; keeps
# id, stage, domain, critical:true, weight:2, answer_type intact.
# ---------------------------------------------------------------------------
EDIT_C1 = (
    r'{id:\"C1\", stage:\"chaos\", domain:\"governance\", critical:true, weight:2, answer_type:\"single_select\",\n     text:\"Is MFA enforced on root / master accounts, with access control policies applied across all accounts?\",\n     options:[{label:\"Enforced everywhere, with policy and periodic review\",score:100},{label:\"Enforced on root, partial elsewhere\",score:65},{label:\"Enforced on some accounts only\",score:30},{label:\"Not enforced / unknown\",score:0}],\n     remediation:\"Enforce MFA on all root and privileged accounts and apply baseline access-control policy org-wide.\"}',
    r'{id:\"C1\", stage:\"chaos\", domain:\"governance\", critical:true, weight:2, answer_type:\"single_select\",\n     text:\"Is there an account-ownership and access model that supports cost governance (named owners per account, least-privilege access to billing and cost consoles)?\",\n     options:[{label:\"Yes — named owners on every account, scoped billing access documented\",score:100},{label:\"Ownership mostly assigned, access permissions ad hoc\",score:65},{label:\"Owners named for some accounts only\",score:30},{label:\"Neither owners nor access model defined\",score:0}],\n     remediation:\"Establish named owners for every account/subscription and a documented access model for billing and cost consoles — the foundation FinOps decisions attach to. (Security controls such as MFA are important but are covered by your CISO, not by this FinOps assessment.)\"}',
)

# ---------------------------------------------------------------------------
# P1.3 — Cover framework stamp
# Insert a mono strip after the covermeta grid, before the optional
# Scope block. The variable `kb` is in scope inside viewReport (const kb=S.kb).
# ---------------------------------------------------------------------------
COVER_ANCHOR = r"""+esc([r.role,r.email].filter(Boolean).join(\" · \"))+'<\u002Fdiv><\u002Fdiv><\u002Fdiv>'\n    +(o.details?"""
COVER_INSERT = r"""+esc([r.role,r.email].filter(Boolean).join(\" · \"))+'<\u002Fdiv><\u002Fdiv><\u002Fdiv>'\n    +'<div class=\"mono\" style=\"margin-top:14px;padding-top:12px;border-top:1px solid #ECECEC;font-size:11px;color:#8E8E8E;letter-spacing:.12em;text-transform:uppercase\">Framework v'+esc(kb.meta.schema_version)+' · reviewed '+esc(kb.meta.last_reviewed)+'<\u002Fdiv>'\n    +(o.details?"""

EDITS = [
    ("P1.1 Disclaimer append (FinOps Foundation TM notice)", EDIT_DISCLAIMER),
    ("P1.2 C1 reframed (account ownership, not MFA/security)", EDIT_C1),
    ("P1.3 Cover framework version + reviewed date stamp", (COVER_ANCHOR, COVER_INSERT)),
]

# Idempotency markers — substrings unique to the post-patch state.
POST_MARKERS = {
    "P1.1 Disclaimer append (FinOps Foundation TM notice)": r"is a trademark of the FinOps Foundation.",
    "P1.2 C1 reframed (account ownership, not MFA/security)": r"account-ownership and access model that supports cost governance",
    "P1.3 Cover framework version + reviewed date stamp": r"Framework v'+esc(kb.meta.schema_version)",
}


def json_safety_check(data: str) -> None:
    for tag in ("__bundler/manifest", "__bundler/template", "__bundler/ext_resources"):
        m = re.search(r'<script type="' + re.escape(tag) + r'">', data)
        if not m:
            continue
        end = data.find("</script>", m.end())
        payload = data[m.end():end]
        try:
            json.loads(payload)
        except json.JSONDecodeError as e:
            ctx = payload[max(0, e.pos - 80):e.pos + 80]
            raise SystemExit(
                f"\n  ✗ {tag} JSON invalid after Phase 1 patch: {e}\n"
                f"    context: {ctx!r}\n"
                f"    REFUSING TO SAVE — adjust the replacements."
            )


def js_syntax_check(data: str) -> None:
    import shutil, subprocess, tempfile
    m = re.search(r'<script type="__bundler/template">', data)
    if not m:
        return
    end = data.find("</script>", m.end())
    decoded = json.loads(data[m.end():end])
    script_bodies = re.findall(
        r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", decoded, flags=re.DOTALL
    )
    node = shutil.which("node")
    if not node:
        print("  ! js_syntax_check: node not on PATH — skipping")
        return
    for i, body in enumerate(script_bodies):
        if len(body.strip()) < 32:
            continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
            tf.write(body); path = tf.name
        try:
            result = subprocess.run(
                [node, "--check", path], capture_output=True, text=True, timeout=15
            )
            if result.returncode != 0:
                raise SystemExit(
                    f"\n  ✗ inline <script> #{i} failed node --check:\n"
                    f"    {result.stderr.strip()}\n"
                    f"    REFUSING TO SAVE — a patch produced invalid JS."
                )
        finally:
            pathlib.Path(path).unlink(missing_ok=True)


def semantic_check(data: str) -> None:
    m = re.search(r'<script type="__bundler/template">', data)
    if not m:
        return
    end = data.find("</script>", m.end())
    decoded = json.loads(data[m.end():end])

    checks = [
        # KB still has 5 stages + all 44 questions
        (r'\bid:"chaos"', "chaos stage"), (r'\bid:"transparent"', "transparent stage"),
        (r'\bid:"C1"', "Q_C1"), (r'\bid:"C8"', "Q_C8"),
        (r'\bid:"I1"', "Q_I1"), (r'\bid:"I9"', "Q_I9"),
        (r'\bid:"O1"', "Q_O1"), (r'\bid:"O10"', "Q_O10"),
        (r'\bid:"A1"', "Q_A1"), (r'\bid:"A9"', "Q_A9"),
        (r'\bid:"T1"', "Q_T1"), (r'\bid:"T8"', "Q_T8"),
        # Phase 1 post-conditions
        (r"is a trademark of the FinOps Foundation", "TM disclaimer"),
        (r"account-ownership and access model", "C1 reframed"),
        (r"Framework v'\+esc\(kb\.meta\.schema_version\)", "cover framework stamp"),
        # And the C1 MFA framing is GONE
    ]
    missing = [label for pat, label in checks if not re.search(pat, decoded)]
    if missing:
        raise SystemExit(
            "\n  ✗ semantic check failed — missing markers:\n    " + "\n    ".join(missing)
        )
    # Explicit negative check: old C1 MFA text should be gone
    if re.search(r"Is MFA enforced on root / master accounts", decoded):
        raise SystemExit(
            "\n  ✗ semantic check failed — old C1 MFA text still present; patch did not replace."
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = FILE.read_text(encoding="utf-8")
    before_len = len(data)
    applied = 0

    print("--- EDITS ---")
    for label, (old, new) in EDITS:
        marker = POST_MARKERS.get(label)
        if marker and marker in data:
            print(f"  = {label}: already applied")
            continue
        if old not in data:
            print(f"  ! {label}: OLD NOT FOUND — adjust anchor")
            continue
        data = data.replace(old, new, 1)
        applied += 1
        print(f"  ✓ {label}")

    print()
    json_safety_check(data)
    print("  ✓ all bundler payloads still parse as valid JSON")
    js_syntax_check(data)
    print("  ✓ inline <script> passes node --check")
    semantic_check(data)
    print("  ✓ semantic markers all present, old text removed")

    if args.dry_run:
        print("\n  (dry run — file not written)")
        return 0

    FILE.write_text(data, encoding="utf-8")
    print(f"\n  file: {FILE}")
    print(f"  size delta: {len(data) - before_len:+d} bytes  ({applied} edits)")
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
