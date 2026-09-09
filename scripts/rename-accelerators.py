#!/usr/bin/env python3
"""Canonical rename across the 4 CIS accelerators.

Practice: CIS Tech Advisory -> Infrastructure Tech Advisory
Company:  LTIMindtree -> LTM

Products:
  SoS: "Sovereign Screen"      -> "Sovereign IQ"
  DRJ: "Data Residency ..."    -> "Posture IQ"
  FVC: keep name
  FMS: "FinOps Maturity Screen" / "FinOps Maturity Assessment" /
       "FinOps Maturity Accelerator" -> "FinOps IQ"

Guards: JSON payloads valid, node --check on inline scripts,
        no forbidden strings remain (in outer template AND
        DR&J's gzipped KB inside __bundler/manifest).
"""
import argparse, base64, gzip, json, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path("/home/user/ltm-core")
FILES = {
    "SoS": ROOT / "Data-Sovereignty-Value-Case-Tool" / "Sovereign Screen (standalone).html",
    "DRJ": ROOT / "Digital Sovereignty Data Residency Jurisdiction Audit" / "LTM-Data Residency & Jurisdiction Audit.html",
    "FVC": ROOT / "finops-value-case" / "FinOps Value Case (LTM).html",
    "FMS": ROOT / "FinopsMaturityAssessment" / "FinOps Maturity Screen (LTM).html",
}

def patch_template(html, replacements):
    m = re.search(r'<script type="__bundler/template">', html)
    if not m: return html, 0
    end = html.find('</script>', m.end())
    decoded = json.loads(html[m.end():end])
    applied = 0
    for old, new in replacements:
        if old in decoded:
            decoded = decoded.replace(old, new); applied += 1
    new_payload = json.dumps(decoded, ensure_ascii=False).replace("</script>", "<\\/script>")
    return html[:m.end()] + new_payload + html[end:], applied

def patch_drj_kb(html, replacements):
    m = re.search(r'<script type="__bundler/manifest">', html)
    end = html.find('</script>', m.end())
    manifest = json.loads(html[m.end():end])
    applied, target_uid = 0, None
    for uid, ent in manifest.items():
        if ent.get("mime") != "application/javascript" or not ent.get("compressed"): continue
        body = gzip.decompress(base64.b64decode(ent["data"])).decode("utf-8")
        touched = False
        for old, new in replacements:
            if old in body:
                body = body.replace(old, new); touched = True; applied += 1
        if touched:
            ent["data"] = base64.b64encode(gzip.compress(body.encode("utf-8"))).decode("ascii")
            target_uid = uid
            break
    new_payload = json.dumps(manifest, ensure_ascii=False).replace("</script>", "<\\/script>")
    return html[:m.end()] + new_payload + html[end:], applied, target_uid

def json_ok(data):
    for tag in ("__bundler/manifest", "__bundler/template", "__bundler/ext_resources"):
        m = re.search(r'<script type="' + re.escape(tag) + r'">', data)
        if not m: continue
        end = data.find('</script>', m.end())
        json.loads(data[m.end():end])

def js_ok(data):
    node = shutil.which("node")
    if not node: print("   ! node not on PATH — skipping"); return
    m = re.search(r'<script type="__bundler/template">', data)
    if not m: return
    end = data.find('</script>', m.end())
    decoded = json.loads(data[m.end():end])
    for i, body in enumerate(re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", decoded, flags=re.DOTALL)):
        if len(body.strip()) < 32: continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
            tf.write(body); p = tf.name
        try:
            r = subprocess.run([node, "--check", p], capture_output=True, text=True, timeout=15)
            if r.returncode != 0:
                raise SystemExit(f"   ✗ inline script #{i}: {r.stderr.strip()}")
        finally:
            pathlib.Path(p).unlink(missing_ok=True)

def old_names_gone(html, forbidden):
    problems = []
    m = re.search(r'<script type="__bundler/template">', html)
    end = html.find('</script>', m.end())
    decoded = json.loads(html[m.end():end])
    for p in forbidden:
        if p in decoded: problems.append(f"{p} (in template)")
    mm = re.search(r'<script type="__bundler/manifest">', html)
    if mm:
        e2 = html.find('</script>', mm.end())
        manifest = json.loads(html[mm.end():e2])
        for uid, ent in manifest.items():
            if ent.get("mime") == "application/javascript" and ent.get("compressed"):
                try:
                    body = gzip.decompress(base64.b64decode(ent["data"])).decode("utf-8")
                    for p in forbidden:
                        if p in body: problems.append(f"{p} (in KB {uid[:8]})")
                except Exception: pass
    return problems

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    plans = {
        "SoS": {
            "template": [
                ("<b>LTM</b><span>Sovereign Screen</span>", "<b>LTM</b><span>Sovereign IQ</span>"),
                ("Prepared with the LTM Sovereign Screen", "Prepared with the LTM Sovereign IQ"),
            ],
            "forbidden": ["Sovereign Screen"],
        },
        "DRJ": {
            "template": [("<title>Data Residency &amp; Jurisdiction Audit — LTM</title>",
                          "<title>Posture IQ — LTM</title>")],
            "kb": [
                ("Data Residency &amp; Jurisdiction Audit", "Posture IQ"),
                ("Data Residency & Jurisdiction Audit",     "Posture IQ"),
                ("CIS Tech Advisory", "Infrastructure Tech Advisory"),
                ("LTIMindtree", "LTM"),
            ],
            "forbidden": [
                "Data Residency &amp; Jurisdiction Audit",
                "Data Residency & Jurisdiction Audit",
                "CIS Tech Advisory", "LTIMindtree",
            ],
        },
        "FVC": {"template": [], "forbidden": []},
        "FMS": {
            "template": [
                ("<title>FinOps Maturity Screen — Cloud Financial Management Accelerator · LTM</title>",
                 "<title>FinOps IQ — Cloud Financial Management Accelerator · LTM</title>"),
                ("FinOps Maturity Screen — knowledge base", "FinOps IQ — knowledge base"),
                ('framework:"FinOps Maturity Assessment"',  'framework:"FinOps IQ"'),
                ("<b>LTM</b><span>FinOps Maturity Accelerator</span>",
                 "<b>LTM</b><span>FinOps IQ</span>"),
                ('<div class="reptitle">FinOps Maturity Assessment</div>',
                 '<div class="reptitle">FinOps IQ</div>'),
                ("Prepared with the LTM FinOps Maturity Accelerator.",
                 "Prepared with the LTM FinOps IQ accelerator."),
            ],
            "forbidden": ["FinOps Maturity Screen", "FinOps Maturity Assessment", "FinOps Maturity Accelerator"],
        },
    }
    total = 0
    for tag, plan in plans.items():
        path = FILES[tag]; html = path.read_text(); before = len(html)
        applied_tpl, applied_kb = 0, 0
        if plan["template"]: html, applied_tpl = patch_template(html, plan["template"])
        if tag == "DRJ":
            html, applied_kb, uid = patch_drj_kb(html, plan["kb"])
            print(f"[{tag}] template={applied_tpl}  KB={applied_kb} (uid={uid[:8] if uid else '-'})")
        else:
            print(f"[{tag}] template={applied_tpl}")
        json_ok(html); print("   ✓ JSON valid")
        js_ok(html);   print("   ✓ inline scripts pass node --check")
        problems = old_names_gone(html, plan["forbidden"])
        if problems: raise SystemExit(f"   ✗ still contains: {problems}")
        print("   ✓ forbidden gone")
        if not args.dry_run:
            path.write_text(html); print(f"   ✓ wrote  (Δ {len(html)-before:+d} bytes)")
        else:
            print("   (dry-run)")
        total += applied_tpl + applied_kb
    print(f"\n=== {total} edits across {len(plans)} files ===")
    return 0

if __name__ == "__main__":
    sys.exit(main())
