#!/usr/bin/env python3
"""FinOps Maturity Screen — Phase 2 patch (scoring / content correctness).

Implements the 5 Phase 2 items from docs/FMS-REVIEW.md §5:

  P2.1  C4 remediation softened (RBAC scope).
  P2.2  Culture domain label rename → "Culture & engineering behaviour"
        to disambiguate from Governance's "& accountability".
  P2.3  O10 drag_order marked unscored:true — informational-only,
        drives roadmap emphasis, no maturity impact.
  P2.4  C8 gains a {label:"None of these", score:0, exclusive:true}
        option; ansMulti handler learns exclusive semantics.
  P2.5  boolean_dk via allow_dk:true flag on 6 questions
        (C3, C4, I6, O7, A7, T4). qScore excludes DK; new "Unsure"
        button; new blindSpots computation; new report section
        listing DK'd questions with their dk_blind narrative.

Idempotent. Stacks cleanly on top of Phase 1 (SHA bc5c472).
Guards: json_safety + node --check + semantic markers.

Apostrophes note: the __bundler/template JSON payload rejects
backslash-apostrophe. Any user-facing "don't" must therefore route
through a JSON-safe form. This patch uses "Unsure" for the DK button
label — avoids the escape problem entirely.
"""
import argparse, json, pathlib, re, sys

FILE = pathlib.Path(
    "/home/user/ltm-core/FinopsMaturityAssessment/FinOps Maturity Screen (LTM).html"
)

# ---------------------------------------------------------------------------
# P2.1 — C4 remediation softened
# ---------------------------------------------------------------------------
EDIT_C4_REM = (
    r'{id:\"C4\", stage:\"chaos\", domain:\"culture\", critical:true, weight:1.5, answer_type:\"boolean\",\n     text:\"Does the finance team have read-only access to cloud billing consoles and cost dashboards?\",\n     remediation:\"Grant finance read-only billing access so cost conversations start from shared data.\"}',
    r'{id:\"C4\", stage:\"chaos\", domain:\"culture\", critical:true, weight:1.5, answer_type:\"boolean\", allow_dk:true,\n     text:\"Does the finance team have read-only access to cloud billing consoles and cost dashboards?\",\n     dk_blind:\"Finance access to billing consoles is unknown — usually a sign the platform team has not been asked to grant it.\",\n     remediation:\"Work with your cloud platform team to grant finance read-only billing / cost console access so cost conversations start from shared data.\"}',
)

# ---------------------------------------------------------------------------
# P2.2 — Culture domain label rename
# ---------------------------------------------------------------------------
EDIT_CULTURE_LABEL = (
    r'{id:\"culture\",     label:\"Culture & accountability\",    color:\"#226882\"}',
    r'{id:\"culture\",     label:\"Culture & engineering behaviour\", color:\"#226882\"}',
)

# ---------------------------------------------------------------------------
# P2.3 — O10 unscored:true (informational drag_order)
# ---------------------------------------------------------------------------
EDIT_O10 = (
    r'{id:\"O10\", stage:\"optimized\", domain:\"optimization\", critical:false, weight:1, answer_type:\"drag_order\",',
    r'{id:\"O10\", stage:\"optimized\", domain:\"optimization\", critical:false, weight:1, answer_type:\"drag_order\", unscored:true,',
)

# ---------------------------------------------------------------------------
# P2.4 — C8 exclusive "None of these"
# Anchor: C8's options list ends with the contract-owner option.
# ---------------------------------------------------------------------------
EDIT_C8_OPTS = (
    r'{label:\"Named commercial / contract owner per provider\",score:25}]',
    r'{label:\"Named commercial / contract owner per provider\",score:25},{label:\"None of these\",score:0,exclusive:true}]',
)

# ---------------------------------------------------------------------------
# P2.4b — ansMulti handler: exclusive semantics
# ---------------------------------------------------------------------------
EDIT_ANSMULTI = (
    r'else if(a===\"ansMulti\"){ const q=el.dataset.q,i=Number(el.dataset.i); const arr=Array.isArray(S.answers[q])?S.answers[q].slice():[];\n    const p=arr.indexOf(i); if(p>=0)arr.splice(p,1); else arr.push(i); if(arr.length) S.answers[q]=arr; else delete S.answers[q]; render(); }',
    r'else if(a===\"ansMulti\"){ const q=el.dataset.q,i=Number(el.dataset.i); const qq=S.kb.questions.find(x=>x.id===q); const opt=qq.options[i];\n    let arr=Array.isArray(S.answers[q])?S.answers[q].slice():[];\n    if(opt.exclusive){ arr=arr.includes(i)?[]:[i]; }\n    else { const p=arr.indexOf(i); if(p>=0)arr.splice(p,1); else arr.push(i); arr=arr.filter(j=>!qq.options[j].exclusive); }\n    if(arr.length) S.answers[q]=arr; else delete S.answers[q]; render(); }',
)

# ---------------------------------------------------------------------------
# P2.5 — boolean_dk via allow_dk flag
# ---------------------------------------------------------------------------
# 2.5a: qScore gains a DK short-circuit + unscored short-circuit.
EDIT_QSCORE_HEAD = (
    r'function qScore(q,a){\n  if(a===undefined||a===null||a===\"__NA__\") return null;\n  switch(q.answer_type){',
    r'function qScore(q,a){\n  if(a===undefined||a===null||a===\"__NA__\"||a===\"__DK__\") return null;\n  if(q.unscored) return null;\n  switch(q.answer_type){',
)

# 2.5b: renderQ boolean branch adds the Unsure button when allow_dk.
EDIT_RENDERQ_BOOL = (
    r"""} else if(q.answer_type===\"boolean\"){\n    body='<div class=\"bool\"><button class=\"boolbtn'+(a===true?' on':'')+'\" data-action=\"ansBool\" data-q=\"'+q.id+'\" data-v=\"true\">Yes<\u002Fbutton>'\n      +'<button class=\"boolbtn'+(a===false?' on':'')+'\" data-action=\"ansBool\" data-q=\"'+q.id+'\" data-v=\"false\">No<\u002Fbutton><\u002Fdiv>';\n  }""",
    r"""} else if(q.answer_type===\"boolean\"){\n    body='<div class=\"bool\"><button class=\"boolbtn'+(a===true?' on':'')+'\" data-action=\"ansBool\" data-q=\"'+q.id+'\" data-v=\"true\">Yes<\u002Fbutton>'\n      +'<button class=\"boolbtn'+(a===false?' on':'')+'\" data-action=\"ansBool\" data-q=\"'+q.id+'\" data-v=\"false\">No<\u002Fbutton>'\n      +(q.allow_dk?'<button class=\"boolbtn dk'+(a===\"__DK__\"?' on':'')+'\" data-action=\"ansDK\" data-q=\"'+q.id+'\">Unsure<\u002Fbutton>':'')+'<\u002Fdiv>';\n  }""",
)

# 2.5c: ansDK action handler. Anchor: the ansNA handler.
EDIT_ANSNA_ADD_ANSDK = (
    r'else if(a===\"ansNA\"){ const q=el.dataset.q; if(S.answers[q]===\"__NA__\") delete S.answers[q]; else S.answers[q]=\"__NA__\"; render(); }',
    r'else if(a===\"ansNA\"){ const q=el.dataset.q; if(S.answers[q]===\"__NA__\") delete S.answers[q]; else S.answers[q]=\"__NA__\"; render(); }\n  else if(a===\"ansDK\"){ const q=el.dataset.q; if(S.answers[q]===\"__DK__\") delete S.answers[q]; else S.answers[q]=\"__DK__\"; render(); }',
)

# 2.5d: allow_dk + dk_blind on 5 remaining boolean questions
# (C4 already handled by EDIT_C4_REM above; here: C3, I6, O7, A7, T4.)
EDIT_C3 = (
    r'{id:\"C3\", stage:\"chaos\", domain:\"visibility\", critical:false, weight:1, answer_type:\"boolean\",\n     text:\"Are billing alarms configured and actively alerting when spend crosses defined thresholds?\",\n     remediation:',
    r'{id:\"C3\", stage:\"chaos\", domain:\"visibility\", critical:false, weight:1, answer_type:\"boolean\", allow_dk:true,\n     text:\"Are billing alarms configured and actively alerting when spend crosses defined thresholds?\",\n     dk_blind:\"Billing alarm state is unknown — the first sign of overspend usually arrives via the invoice.\",\n     remediation:',
)
EDIT_I6 = (
    r'{id:\"I6\", stage:\"informed\", domain:\"visibility\", critical:false, weight:1, answer_type:\"boolean\",\n     text:\"Is cost anomaly detection enabled and alerting on unexpected spend spikes?\",\n     remediation:',
    r'{id:\"I6\", stage:\"informed\", domain:\"visibility\", critical:false, weight:1, answer_type:\"boolean\", allow_dk:true,\n     text:\"Is cost anomaly detection enabled and alerting on unexpected spend spikes?\",\n     dk_blind:\"Anomaly-detection state is unknown — spikes are being discovered by whoever notices the bill first.\",\n     remediation:',
)
EDIT_O7 = (
    r'{id:\"O7\", stage:\"optimized\", domain:\"optimization\", critical:false, weight:1, answer_type:\"boolean\",\n     text:\"Has data egress and cross-region transfer architecture been reviewed and optimised for cost?\",\n     remediation:',
    r'{id:\"O7\", stage:\"optimized\", domain:\"optimization\", critical:false, weight:1, answer_type:\"boolean\", allow_dk:true,\n     text:\"Has data egress and cross-region transfer architecture been reviewed and optimised for cost?\",\n     dk_blind:\"Egress / inter-region traffic has not been reviewed — often one of the largest unexamined line items on the bill.\",\n     remediation:',
)
EDIT_A7 = (
    r'{id:\"A7\", stage:\"automated\", domain:\"automation\", critical:false, weight:1, answer_type:\"boolean\",\n     text:\"Does automated handling and graceful recovery exist for Spot / Preemptible interruptions?\",\n     remediation:',
    r'{id:\"A7\", stage:\"automated\", domain:\"automation\", critical:false, weight:1, answer_type:\"boolean\", allow_dk:true,\n     text:\"Does automated handling and graceful recovery exist for Spot / Preemptible interruptions?\",\n     dk_blind:\"Spot interruption handling is unknown — usually why spot adoption is blocked on reliability concerns.\",\n     remediation:',
)
EDIT_T4 = (
    r'{id:\"T4\", stage:\"transparent\", domain:\"visibility\", critical:false, weight:1, answer_type:\"boolean\",\n     text:\"Is cost per tenant or per customer tracked and used to inform pricing and margin decisions?\",\n     remediation:',
    r'{id:\"T4\", stage:\"transparent\", domain:\"visibility\", critical:false, weight:1, answer_type:\"boolean\", allow_dk:true,\n     text:\"Is cost per tenant or per customer tracked and used to inform pricing and margin decisions?\",\n     dk_blind:\"Per-tenant cost is unknown — the anchor of margin conversations is missing.\",\n     remediation:',
)

# 2.5e: blindSpots() function + injection into viewReport.
# Insert blindSpots() right after overallScore()'s closing brace.
EDIT_BLINDSPOTS_FN = (
    r'function overallScore(kb,answers){\n  let t=0,w=0;\n  kb.questions.forEach(q=>{ const s=qScore(q,answers[q.id]); if(s===null) return;\n    const ww=q.weight||1; t+=s*ww; w+=ww; });\n  return w?Math.round(t/w):null;\n}',
    r'function overallScore(kb,answers){\n  let t=0,w=0;\n  kb.questions.forEach(q=>{ const s=qScore(q,answers[q.id]); if(s===null) return;\n    const ww=q.weight||1; t+=s*ww; w+=ww; });\n  return w?Math.round(t/w):null;\n}\nfunction blindSpots(kb,answers){\n  const list=[];\n  kb.questions.forEach(q=>{ if(answers[q.id]===\"__DK__\") list.push({q,text:q.dk_blind||q.text}); });\n  return list;\n}',
)

# 2.5f: viewReport picks up blindSpots + renders a section between the
# stagetable and the recommended plan. Anchor: the closing of section 2
# (Assessment), right before section 3 (Recommended plan).
EDIT_REPORT_BLINDSPOTS = (
    r"""+'<div style=\"margin-top:22px\"><div class=\"mlab\" style=\"font-family:\\'IBM Plex Mono\\',monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#8E8E8E;margin-bottom:10px\">Capability by domain<\u002Fdiv>'+domHtml+'<\u002Fdiv><\u002Fdiv>'\n    // 3 plan""",
    r"""+'<div style=\"margin-top:22px\"><div class=\"mlab\" style=\"font-family:\\'IBM Plex Mono\\',monospace;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:#8E8E8E;margin-bottom:10px\">Capability by domain<\u002Fdiv>'+domHtml+'<\u002Fdiv><\u002Fdiv>'\n    // 2b blind spots (Unsure answers)\n    +(function(){var bs=blindSpots(kb,S.answers); if(!bs.length) return \"\"; return '<div class=\"repsec\"><h3>Blind spots<\u002Fh3><p style=\"color:#5B5B5B;font-size:13.5px;margin-top:0\">You answered \"Unsure\" '+bs.length+' time'+(bs.length>1?\"s\":\"\")+'. Each is a decision currently being made without data.<\u002Fp>'+bs.map(function(b){return '<div style=\"background:#F9F9F9;border-left:3px solid #B26A00;padding:10px 14px;border-radius:0 6px 6px 0;margin:8px 0\"><div style=\"font-weight:600;color:#313131;font-size:13.5px\">'+esc(b.q.text)+'<\u002Fdiv><div style=\"color:#5B5B5B;font-size:13px;margin-top:4px\">'+esc(b.text)+'<\u002Fdiv><\u002Fdiv>';}).join(\"\")+'<\u002Fdiv>';})()\n    // 3 plan""",
)


EDITS = [
    ("P2.1 C4 remediation + allow_dk", EDIT_C4_REM),
    ("P2.2 Culture domain label rename", EDIT_CULTURE_LABEL),
    ("P2.3 O10 unscored:true", EDIT_O10),
    ("P2.4a C8 add None-exclusive option", EDIT_C8_OPTS),
    ("P2.4b ansMulti learns exclusive semantics", EDIT_ANSMULTI),
    ("P2.5a qScore short-circuits DK + unscored", EDIT_QSCORE_HEAD),
    ("P2.5b renderQ adds Unsure button when allow_dk", EDIT_RENDERQ_BOOL),
    ("P2.5c ansDK action handler", EDIT_ANSNA_ADD_ANSDK),
    ("P2.5d C3 allow_dk + dk_blind", EDIT_C3),
    ("P2.5d I6 allow_dk + dk_blind", EDIT_I6),
    ("P2.5d O7 allow_dk + dk_blind", EDIT_O7),
    ("P2.5d A7 allow_dk + dk_blind", EDIT_A7),
    ("P2.5d T4 allow_dk + dk_blind", EDIT_T4),
    ("P2.5e blindSpots() function", EDIT_BLINDSPOTS_FN),
    ("P2.5f Blind spots section in viewReport", EDIT_REPORT_BLINDSPOTS),
]

POST_MARKERS = {
    "P2.1 C4 remediation + allow_dk": r'Work with your cloud platform team to grant finance',
    "P2.2 Culture domain label rename": r'Culture & engineering behaviour',
    "P2.3 O10 unscored:true": r'answer_type:\"drag_order\", unscored:true',
    "P2.4a C8 add None-exclusive option": r'{label:\"None of these\",score:0,exclusive:true}',
    "P2.4b ansMulti learns exclusive semantics": r'if(opt.exclusive){ arr=arr.includes(i)',
    "P2.5a qScore short-circuits DK + unscored": r'a===\"__DK__\") return null;\n  if(q.unscored)',
    "P2.5b renderQ adds Unsure button when allow_dk": r'q.allow_dk?\'<button class=\"boolbtn dk',
    "P2.5c ansDK action handler": r'else if(a===\"ansDK\")',
    "P2.5d C3 allow_dk + dk_blind": r'Billing alarm state is unknown',
    "P2.5d I6 allow_dk + dk_blind": r'Anomaly-detection state is unknown',
    "P2.5d O7 allow_dk + dk_blind": r'Egress / inter-region traffic has not been reviewed',
    "P2.5d A7 allow_dk + dk_blind": r'Spot interruption handling is unknown',
    "P2.5d T4 allow_dk + dk_blind": r'Per-tenant cost is unknown',
    "P2.5e blindSpots() function": r'function blindSpots(kb,answers)',
    "P2.5f Blind spots section in viewReport": r'2b blind spots (Unsure answers)',
}


def json_safety_check(data: str) -> None:
    for tag in ("__bundler/manifest", "__bundler/template", "__bundler/ext_resources"):
        m = re.search(r'<script type="' + re.escape(tag) + r'">', data)
        if not m: continue
        end = data.find("</script>", m.end())
        payload = data[m.end():end]
        try: json.loads(payload)
        except json.JSONDecodeError as e:
            ctx = payload[max(0, e.pos - 80):e.pos + 80]
            raise SystemExit(f"\n  ✗ {tag} JSON invalid: {e}\n    context: {ctx!r}\n    REFUSING TO SAVE")


def js_syntax_check(data: str) -> None:
    import shutil, subprocess, tempfile
    m = re.search(r'<script type="__bundler/template">', data)
    if not m: return
    end = data.find("</script>", m.end())
    decoded = json.loads(data[m.end():end])
    scripts = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", decoded, flags=re.DOTALL)
    node = shutil.which("node")
    if not node:
        print("  ! node not on PATH — skipping"); return
    for i, body in enumerate(scripts):
        if len(body.strip()) < 32: continue
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
            tf.write(body); path = tf.name
        try:
            r = subprocess.run([node, "--check", path], capture_output=True, text=True, timeout=15)
            if r.returncode != 0:
                raise SystemExit(f"\n  ✗ inline <script> #{i} failed node --check:\n    {r.stderr.strip()}")
        finally:
            pathlib.Path(path).unlink(missing_ok=True)


def semantic_check(data: str) -> None:
    m = re.search(r'<script type="__bundler/template">', data)
    end = data.find("</script>", m.end())
    decoded = json.loads(data[m.end():end])
    checks = [
        # Phase 1 still present
        (r'is a trademark of the FinOps Foundation', "P1 TM notice"),
        (r'account-ownership and access model that supports cost governance', "P1 C1 reframed"),
        (r"Framework v'\+esc\(kb\.meta\.schema_version\)", "P1 cover stamp"),
        # Phase 2 markers
        (r'Culture & engineering behaviour', "P2.2 culture label"),
        (r'answer_type:"drag_order", unscored:true', "P2.3 O10 unscored"),
        (r'{label:"None of these",score:0,exclusive:true}', "P2.4a C8 None"),
        (r'if\(opt\.exclusive\)\{ arr=arr\.includes\(i\)', "P2.4b exclusive handler"),
        (r'"__DK__"\) return null', "P2.5a DK short-circuit"),
        (r'q\.allow_dk\?\'<button class="boolbtn dk', "P2.5b Unsure button"),
        (r'else if\(a==="ansDK"\)', "P2.5c ansDK handler"),
        (r'function blindSpots', "P2.5e blindSpots fn"),
        (r'2b blind spots \(Unsure answers\)', "P2.5f report section"),
        # 6 dk_blind narratives
        (r'Billing alarm state is unknown', "C3 dk_blind"),
        (r'Finance access to billing consoles is unknown', "C4 dk_blind"),
        (r'Anomaly-detection state is unknown', "I6 dk_blind"),
        (r'Egress / inter-region traffic has not been reviewed', "O7 dk_blind"),
        (r'Spot interruption handling is unknown', "A7 dk_blind"),
        (r'Per-tenant cost is unknown', "T4 dk_blind"),
    ]
    missing = [lbl for pat, lbl in checks if not re.search(pat, decoded)]
    if missing:
        raise SystemExit("\n  ✗ semantic check failed: " + ", ".join(missing))


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    data = FILE.read_text(); before = len(data); applied = 0
    print("--- EDITS ---")
    for label, (old, new) in EDITS:
        marker = POST_MARKERS.get(label)
        if marker and marker in data:
            print(f"  = {label}: already applied"); continue
        if old not in data:
            print(f"  ! {label}: OLD NOT FOUND"); continue
        data = data.replace(old, new, 1); applied += 1
        print(f"  ✓ {label}")
    print()
    json_safety_check(data); print("  ✓ JSON payloads valid")
    js_syntax_check(data); print("  ✓ inline <script> passes node --check")
    semantic_check(data); print("  ✓ semantic markers present")
    if args.dry_run:
        print("\n  (dry run — file not written)"); return 0
    FILE.write_text(data)
    print(f"\n  size delta: {len(data)-before:+d} bytes  ({applied} edits)")
    return 0 if applied else 1


if __name__ == "__main__":
    sys.exit(main())
