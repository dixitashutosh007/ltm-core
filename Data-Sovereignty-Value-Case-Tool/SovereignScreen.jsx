import React, { useState, useMemo, useEffect, useRef } from "react";

/* =========================================================================
   Digital Sovereignty Accelerator — Finance vertical (Phase 1: UK & EU)
   Interactive triage + readiness screen.
   Rule engine + knowledge base are the verified core (parity-checked in node).
   ========================================================================= */

const GRADE_PRECEDENCE = ["applies","likely_confirm","partial","needs_legal_review","advisory","not_applicable"];

const GRADE_META = {
  applies:            { label: "Applies",              c: "#58A6E0" },
  likely_confirm:     { label: "Likely — confirm",     c: "#FBAE40" },
  partial:            { label: "Partial",              c: "#9B82D0" },
  needs_legal_review: { label: "Needs legal review",   c: "#F15F53" },
  advisory:           { label: "Advisory",             c: "#57B6C2" },
  not_applicable:     { label: "Not applicable",       c: "#7C93A8" },
};

const STAGES = [
  { stage:1, label:"Reactive",            band:[0,20],  desc:"Compliance handled ad hoc and after the fact; exposure largely unmapped." },
  { stage:2, label:"Aware",               band:[21,40], desc:"Obligations identified; controls patchy and undocumented." },
  { stage:3, label:"Structured",          band:[41,60], desc:"Defined controls and ownership; residency addressed but jurisdictional exposure not fully controlled." },
  { stage:4, label:"Managed",             band:[61,80], desc:"Controls tested and evidenced; third-party and concentration risk actively managed." },
  { stage:5, label:"Sovereign-by-Design", band:[81,100],desc:"Sovereignty embedded in architecture and procurement; foreign-access risk provably mitigated." },
];

const REGIMES = [
  { id:"dora", name:"Digital Operational Resilience Act", short:"EU · financial ICT resilience", jur:"EU", weight:0.30,
    rules:[
      { when:{all:[{fact:"entity_role",op:"eq",value:"financial_entity"},{fact:"fin_entity_type",op:"in",value:["credit_institution","investment_firm","payment_institution","emi","insurer","reinsurer","insurance_intermediary","iorp_pension","casp_crypto","ccp","csd","trading_venue","credit_rating_agency","aifm","ucits_mgmt","crowdfunding"]},{any:[{fact:"establishment_eu",op:"is_true"},{fact:"offers_services_eu",op:"is_true"}]}]}, grade:"applies", why:"A regulated financial entity operating in or into the EU falls within DORA's ~20 in-scope categories (Art. 2)." },
      { when:{all:[{fact:"entity_role",op:"eq",value:"ict_provider_to_finance"},{fact:"is_or_uses_designated_ctp",op:"eq",value:"yes"}]}, grade:"likely_confirm", why:"ICT providers to finance can be designated Critical ICT Third-Party Providers under direct ESA oversight (19 designated as of Nov 2025, incl. AWS, Azure, Google Cloud, IBM, Bloomberg)." },
    ],
    obligations:["ICT risk-management framework with board accountability","Major-incident reporting within tight timelines (~4h after classification)","Resilience testing incl. threat-led penetration testing (≥ every 3 years for significant entities)","Register of Information for all ICT arrangements; concentration-risk management","Documented exit strategies for critical ICT services"],
    dims:[{id:"governance",name:"ICT risk governance",weight:0.2},{id:"incident_reporting",name:"Incident detection & reporting",weight:0.2},{id:"resilience_testing",name:"Resilience & threat-led testing",weight:0.2},{id:"third_party_risk",name:"Third-party & concentration risk",weight:0.2},{id:"exit_strategy",name:"Exit / substitutability",weight:0.2}] },

  { id:"nis2_residual", name:"NIS2 — residual obligations", short:"EU · residual after DORA", jur:"EU", weight:0.05,
    rules:[{ when:{all:[{fact:"entity_role",op:"eq",value:"financial_entity"},{fact:"establishment_eu",op:"is_true"}]}, grade:"partial", why:"DORA is lex specialis (DORA Art. 1(2) / NIS2 Art. 4): it replaces NIS2's ICT-risk and incident-reporting duties for financial entities. Residual NIS2 obligations (corporate cyber hygiene, cross-sector cooperation, member-state registration) may still apply — confirm per member state." }],
    obligations:["Residual corporate-level cybersecurity obligations outside DORA's remit","Member-state-specific registration/cooperation duties where applicable"],
    dims:[{id:"corporate_cyber_hygiene",name:"Corporate cyber hygiene",weight:1.0}] },

  { id:"uk_opres", name:"UK Operational Resilience & Outsourcing", short:"UK · FCA/PRA resilience", jur:"UK", weight:0.20,
    rules:[{ when:{all:[{fact:"entity_role",op:"eq",value:"financial_entity"},{fact:"establishment_uk",op:"is_true"}]}, grade:"applies", why:"FCA/PRA-regulated firms and FMIs must meet UK operational-resilience and outsourcing/third-party-risk rules (PS21/3, SS2/21)." }],
    obligations:["Identify important business services and set impact tolerances","Map and test ability to stay within tolerances under severe-but-plausible scenarios","Maintain a self-assessment document","Manage outsourcing & third-party risk (due diligence, exit, contingency)"],
    dims:[{id:"important_business_services",name:"Important business services & tolerances",weight:0.35},{id:"third_party_oversight",name:"Third-party oversight",weight:0.35},{id:"testing",name:"Scenario testing & self-assessment",weight:0.30}] },

  { id:"uk_ctp", name:"UK Critical Third Parties regime", short:"UK · CTP oversight", jur:"UK", weight:0.05,
    rules:[
      { when:{fact:"entity_role",op:"eq",value:"ict_provider_to_finance"}, grade:"advisory", why:"ICT providers to the UK financial sector may be designated Critical Third Parties by HM Treasury, bringing them under joint FCA/PRA/Bank of England oversight and six Fundamental Rules." },
      { when:{all:[{fact:"entity_role",op:"eq",value:"financial_entity"},{fact:"establishment_uk",op:"is_true"},{fact:"is_or_uses_designated_ctp",op:"eq",value:"yes"}]}, grade:"advisory", why:"Reliance on a designated CTP is a material concentration/dependency consideration. The rules bind the provider, not the firm — but the firm's own resilience accountability is undiminished." },
    ],
    obligations:["(If designated) Comply with CTP rules across governance, supply-chain risk, cyber resilience, change and incident management, plus six Fundamental Rules"],
    dims:[{id:"ctp_dependency",name:"CTP dependency / readiness",weight:1.0}] },

  { id:"eu_gdpr", name:"EU GDPR", short:"EU · data protection", jur:"EU", weight:0.15,
    rules:[{ when:{all:[{fact:"processes_personal_data",op:"is_true"},{any:[{fact:"establishment_eu",op:"is_true"},{fact:"offers_services_eu",op:"is_true"},{fact:"data_subjects_geo",op:"includes_any",value:["EU"]}]}]}, grade:"applies", why:"Processing personal data with an EU establishment, or targeting/monitoring individuals in the EU, engages GDPR (Art. 3) — including Chapter V transfer restrictions and Art. 9 conditions." }],
    obligations:["Lawful basis, transparency, data-subject rights, security, records, DPO where applicable","Chapter V restrictions on transfers outside the EEA","Article 9 conditions for special-category data"],
    dims:[{id:"data_protection_governance",name:"Data-protection governance",weight:0.5},{id:"transfer_compliance",name:"Transfer compliance",weight:0.5}] },

  { id:"uk_gdpr", name:"UK GDPR / DPA 2018 / PECR", short:"UK · data protection (DUAA 2025)", jur:"UK", weight:0.10,
    rules:[{ when:{all:[{fact:"processes_personal_data",op:"is_true"},{any:[{fact:"establishment_uk",op:"is_true"},{fact:"offers_services_uk",op:"is_true"},{fact:"data_subjects_geo",op:"includes_any",value:["UK"]}]}]}, grade:"applies", why:"Processing personal data with a UK establishment, or targeting/monitoring individuals in the UK, engages the UK GDPR / DPA 2018 (and PECR). Track phased DUAA 2025 changes." }],
    obligations:["UK GDPR / DPA 2018 core obligations","PECR obligations for electronic marketing/communications","Monitor phased DUAA 2025 amendments"],
    dims:[{id:"data_protection_governance",name:"Data-protection governance",weight:1.0}] },

  { id:"data_transfer_jurisdiction", name:"Transfer & jurisdictional exposure", short:"UK/EU · residency ≠ sovereignty", jur:"UK/EU", weight:0.15,
    rules:[
      { when:{all:[{fact:"processes_personal_data",op:"is_true"},{fact:"data_subjects_geo",op:"includes_any",value:["EU","UK"]},{any:[{fact:"uses_us_hyperscaler",op:"is_true"},{fact:"cloud_provider_hq",op:"includes_any",value:["US"]}]}]}, grade:"advisory", why:"Residency is not sovereignty. A US-headquartered provider can be reachable under the US CLOUD Act regardless of where data physically sits — including EU/UK regions. Assess jurisdictional exposure, not just data location." },
      { when:{all:[{fact:"data_subjects_geo",op:"includes_any",value:["EU"]},{fact:"data_hosting_location",op:"includes_any",value:["US","Other"]}]}, grade:"needs_legal_review", why:"EU personal data hosted outside the EEA in a non-adequate jurisdiction needs a valid Chapter V transfer mechanism (adequacy / SCCs + TIA). Note: UK hosting is covered by EU→UK adequacy and is not itself a transfer violation." },
    ],
    obligations:["Valid transfer mechanism for personal data leaving the EEA/UK","Transfer Impact Assessments where required","Demonstrable control against foreign-government access, not just localisation"],
    dims:[{id:"jurisdiction_control",name:"Foreign-access / jurisdictional control",weight:0.6},{id:"transfer_mechanisms",name:"Transfer mechanisms & TIAs",weight:0.4}] },

  { id:"eu_ai_act", name:"EU AI Act", short:"EU · high-risk AI", jur:"EU", weight:0.10,
    rules:[
      { when:{all:[{fact:"uses_high_risk_ai",op:"is_true"},{any:[{fact:"establishment_eu",op:"is_true"},{fact:"offers_services_eu",op:"is_true"}]}]}, grade:"applies", why:"AI for creditworthiness/credit scoring or insurance risk/pricing is high-risk under Annex III — triggering risk management, data governance, transparency, human oversight and conformity obligations. Penalties reach 7% of global turnover." },
      { when:{all:[{fact:"uses_other_ai",op:"is_true"},{any:[{fact:"establishment_eu",op:"is_true"},{fact:"offers_services_eu",op:"is_true"}]}]}, grade:"advisory", why:"Non-high-risk AI may still carry transparency and/or GPAI obligations depending on the system. Confirm classification." },
    ],
    obligations:["(High-risk) Risk-management system, data governance, technical documentation, logging, transparency, human oversight, conformity assessment"],
    dims:[{id:"ai_data_governance",name:"AI data governance",weight:0.5},{id:"ai_risk_controls",name:"High-risk AI controls & oversight",weight:0.5}] },

  { id:"eu_data_act", name:"EU Data Act", short:"EU · cloud switching & access", jur:"EU", weight:0.05,
    rules:[{ when:{all:[{any:[{fact:"establishment_eu",op:"is_true"},{fact:"offers_services_eu",op:"is_true"}]},{any:[{fact:"uses_us_hyperscaler",op:"is_true"},{fact:"cloud_provider_hq",op:"includes_any",value:["US","EU","UK","Other"]}]}]}, grade:"likely_confirm", why:"Users and providers of cloud/data-processing services with an EU nexus fall within the Data Act's switching/portability duties and its bar on unlawful third-country access to non-personal data held in the EU. Confirm customer vs provider obligations." }],
    obligations:["Cloud switching and portability facilitation","Safeguards against unlawful third-country access to non-personal data","Contractual fairness for data access/sharing"],
    dims:[{id:"portability_switching",name:"Portability & switching readiness",weight:1.0}] },
];

const SECTIONS = [
  { cat:"entity_identity",        n:"01", label:"Your organisation", blurb:"Who you are decides which rulebooks even open." },
  { cat:"jurisdictional_footprint",n:"02", label:"Footprint",         blurb:"Where you operate and whom you serve." },
  { cat:"data_profile",           n:"03", label:"Data",               blurb:"What personal data you hold, and whose." },
  { cat:"hosting_and_cloud",      n:"04", label:"Hosting & cloud",    blurb:"Where data sits — and who can legally reach it." },
  { cat:"scale",                  n:"05", label:"Scale",              blurb:"Size sets proportionality thresholds." },
  { cat:"technology_use",         n:"06", label:"Technology",         blurb:"AI in decisions that regulators watch closely." },
  { cat:"third_party_dependency", n:"07", label:"Third parties",      blurb:"Concentration and critical-provider exposure." },
  { cat:"resilience_posture",     n:"08", label:"Readiness",          blurb:"How ready your controls are today." },
  { cat:"governance_posture",     n:"09", label:"Governance",         blurb:"Context that shapes the roadmap." },
];

const QUESTIONS = [
  { id:"Q_ROLE", cat:"entity_identity", tier:1, type:"single_select", text:"Which best describes your organisation's role?",
    options:[{label:"A regulated financial entity (bank, insurer, payment firm, fund…)",fv:{entity_role:"financial_entity"}},{label:"An ICT / technology provider serving financial firms",fv:{entity_role:"ict_provider_to_finance"}},{label:"Neither / other",fv:{entity_role:"other"}}] },
  { id:"Q_FINTYPE", cat:"entity_identity", tier:1, type:"single_select", shown_if:{fact:"entity_role",op:"eq",value:"financial_entity"}, text:"Which type of financial entity are you?",
    options:[{label:"Bank / credit institution",fv:{fin_entity_type:"credit_institution"}},{label:"Investment firm",fv:{fin_entity_type:"investment_firm"}},{label:"Payment institution",fv:{fin_entity_type:"payment_institution"}},{label:"E-money institution",fv:{fin_entity_type:"emi"}},{label:"Insurer / reinsurer / intermediary",fv:{fin_entity_type:"insurer"}},{label:"Pension fund (IORP)",fv:{fin_entity_type:"iorp_pension"}},{label:"Crypto-asset service provider",fv:{fin_entity_type:"casp_crypto"}},{label:"Fund manager (AIFM / UCITS)",fv:{fin_entity_type:"aifm"}},{label:"Market infrastructure (CCP / CSD / trading venue)",fv:{fin_entity_type:"ccp"}},{label:"Other financial entity",fv:{fin_entity_type:"other_financial"}}] },

  { id:"Q_EST", cat:"jurisdictional_footprint", tier:1, type:"multi_select", text:"Where is your organisation established or operating?",
    options:[{label:"One or more EU member states",fv:{establishment_eu:true}},{label:"United Kingdom",fv:{establishment_uk:true}},{label:"United States",fv:{}},{label:"Other",fv:{}}] },
  { id:"Q_SERVE", cat:"jurisdictional_footprint", tier:1, type:"multi_select", text:"Do you offer products or services to — or monitor — individuals located in the EU or UK?",
    options:[{label:"Individuals in the EU",fv:{offers_services_eu:true}},{label:"Individuals in the UK",fv:{offers_services_uk:true}},{label:"Neither",fv:{}}] },
  { id:"Q_MSTATES", cat:"jurisdictional_footprint", tier:1, type:"range", shown_if:{fact:"establishment_eu",op:"is_true"}, text:"In how many EU member states do you operate?", writes:"eu_member_state_count", range:{min:0,max:27,step:1,suffix:" member states"} },

  { id:"Q_PD", cat:"data_profile", tier:1, type:"boolean", text:"Does your organisation process personal data?", writes:"processes_personal_data" },
  { id:"Q_DSGEO", cat:"data_profile", tier:1, type:"multi_select", na:true, shown_if:{fact:"processes_personal_data",op:"is_true"}, text:"Where are the individuals whose data you process located?",
    options:[{label:"EU",fv:{data_subjects_geo:["EU"]}},{label:"UK",fv:{data_subjects_geo:["UK"]}},{label:"US",fv:{data_subjects_geo:["US"]}},{label:"Other",fv:{data_subjects_geo:["Other"]}}] },
  { id:"Q_SCD", cat:"data_profile", tier:1, type:"boolean", shown_if:{fact:"processes_personal_data",op:"is_true"}, text:"Do you process special-category or highly sensitive data (biometric, health, detailed financial)?", writes:"special_category_data" },
  { id:"Q_VOL", cat:"data_profile", tier:1, type:"single_select", na:true, shown_if:{fact:"processes_personal_data",op:"is_true"}, text:"Roughly how many personal-data records do you hold?",
    options:[{label:"Under 10,000",fv:{data_volume_band:"under_10k"}},{label:"10k – 1m",fv:{data_volume_band:"10k_1m"}},{label:"1m – 10m",fv:{data_volume_band:"1m_10m"}},{label:"Over 10m",fv:{data_volume_band:"over_10m"}}] },

  { id:"Q_HOSTLOC", cat:"hosting_and_cloud", tier:1, type:"multi_select", text:"Where is your data physically stored and processed?",
    options:[{label:"EU",fv:{data_hosting_location:["EU"]}},{label:"UK",fv:{data_hosting_location:["UK"]}},{label:"US",fv:{data_hosting_location:["US"]}},{label:"Other",fv:{data_hosting_location:["Other"]}}] },
  { id:"Q_CLOUDHQ", cat:"hosting_and_cloud", tier:1, type:"multi_select", text:"What is the headquarters jurisdiction of your primary cloud / hosting providers?", hint:"Provider HQ — not data location — is what drives foreign-access risk.",
    options:[{label:"US-headquartered",fv:{cloud_provider_hq:["US"]}},{label:"EU-headquartered",fv:{cloud_provider_hq:["EU"]}},{label:"UK-headquartered",fv:{cloud_provider_hq:["UK"]}},{label:"Other",fv:{cloud_provider_hq:["Other"]}}] },
  { id:"Q_HYPER", cat:"hosting_and_cloud", tier:1, type:"boolean", text:"Do you rely on a US-headquartered hyperscaler (AWS, Microsoft Azure, Google Cloud) for material workloads?", writes:"uses_us_hyperscaler" },
  { id:"Q_SOVOFFER", cat:"hosting_and_cloud", tier:1, type:"single_select", na:true, shown_if:{fact:"uses_us_hyperscaler",op:"is_true"}, text:"Are those workloads on a sovereign / EU-boundary offering with contractual and operational controls against foreign access?",
    readiness:{regime:"data_transfer_jurisdiction",dim:"jurisdiction_control"},
    options:[{label:"Yes — sovereign offering with controls",fv:{sovereign_offering_status:"yes"},score:100},{label:"Partially",fv:{sovereign_offering_status:"partial"},score:50},{label:"No — standard commercial region",fv:{sovereign_offering_status:"no"},score:0},{label:"Don't know",fv:{sovereign_offering_status:"unknown"},score:0}] },

  { id:"Q_SIZE", cat:"scale", tier:1, type:"single_select", text:"What is your organisation's size?",
    options:[{label:"Micro (<10 staff, ≤ €2m)",fv:{company_size:"micro"}},{label:"Small (<50 staff, ≤ €10m)",fv:{company_size:"small"}},{label:"Medium (<250 staff, ≤ €50m)",fv:{company_size:"medium"}},{label:"Large (≥250 staff or > €50m)",fv:{company_size:"large"}}] },

  { id:"Q_AI", cat:"technology_use", tier:1, type:"multi_select", text:"Do you use AI or automated decision systems for any of the following?",
    options:[{label:"Creditworthiness / credit scoring",fv:{uses_high_risk_ai:true}},{label:"Insurance risk assessment or pricing",fv:{uses_high_risk_ai:true}},{label:"Fraud detection or operational automation",fv:{uses_other_ai:true}},{label:"None of these",fv:{}}] },

  { id:"Q_CTP", cat:"third_party_dependency", tier:1, type:"single_select", text:"Are you — or do you depend on — a provider designated (or likely to be) a Critical Third Party under UK rules or a Critical ICT Third-Party Provider under DORA (e.g. a major cloud provider)?",
    options:[{label:"Yes",fv:{is_or_uses_designated_ctp:"yes"}},{label:"No",fv:{is_or_uses_designated_ctp:"no"}},{label:"Don't know",fv:{is_or_uses_designated_ctp:"unknown"}}] },
  { id:"Q_CONC", cat:"third_party_dependency", tier:1, type:"boolean", text:"Is a single ICT provider responsible for a critical or important function with no ready substitute?", writes:"ict_concentration_risk", readiness:{regime:"dora",dim:"third_party_risk"} },

  { id:"QR_GOV", cat:"resilience_posture", tier:1, type:"rating_1_5", text:"How mature is board-level ownership of ICT / operational-resilience risk?", readiness:{regime:"dora",dim:"governance"} },
  { id:"QR_INC", cat:"resilience_posture", tier:1, type:"rating_1_5", text:"How ready is your ICT-incident detection and regulatory-reporting capability (reporting a major incident within hours)?", readiness:{regime:"dora",dim:"incident_reporting"} },
  { id:"QR_TEST", cat:"resilience_posture", tier:1, type:"rating_1_5", text:"How regularly do you run resilience / scenario testing, including threat-led penetration testing?", readiness:{regime:"dora",dim:"resilience_testing"} },
  { id:"QR_TPR", cat:"resilience_posture", tier:1, type:"rating_1_5", text:"How complete is your register of ICT third-party arrangements and your exit / substitutability planning?", readiness:{regime:"dora",dim:"third_party_risk"} },
  { id:"QR_IBS", cat:"resilience_posture", tier:1, type:"single_select", na:true, shown_if:{fact:"establishment_uk",op:"is_true"}, text:"Have you identified important business services and set impact tolerances (UK operational resilience)?",
    readiness:{regime:"uk_opres",dim:"important_business_services"},
    options:[{label:"Fully",fv:{},score:100},{label:"Partially",fv:{},score:50},{label:"Not yet",fv:{},score:0}] },
  { id:"QR_SOV", cat:"resilience_posture", tier:1, type:"rating_1_5", text:"How well can you evidence protection of data from foreign-government access — beyond physical residency?", readiness:{regime:"data_transfer_jurisdiction",dim:"jurisdiction_control"} },
  { id:"QR_TRANSFER", cat:"resilience_posture", tier:1, type:"single_select", na:true, text:"Do you have transfer mechanisms and Transfer Impact Assessments (TIAs) in place for cross-border data flows?",
    readiness:{regime:"data_transfer_jurisdiction",dim:"transfer_mechanisms"},
    options:[{label:"Yes, documented",fv:{},score:100},{label:"Partial",fv:{},score:50},{label:"No",fv:{},score:0}] },

  { id:"Q2_PRIORITY", cat:"governance_posture", tier:2, type:"drag_order", text:"Rank these sovereignty risk domains by concern for your organisation — most concerning first.",
    options:["Data residency","Foreign-government access","ICT concentration / resilience","Regulatory reporting","Supply-chain oversight"] },
  { id:"Q2_CONTEXT", cat:"governance_posture", tier:2, type:"open_text", text:"Note any known regulatory findings, audit gaps, or board-level concerns relating to digital sovereignty.", placeholder:"Optional — captured for the facilitated review." },
  { id:"Q2_EXIT", cat:"governance_posture", tier:2, type:"open_text", shown_if:{fact:"ict_concentration_risk",op:"is_true"}, text:"Describe the exit strategy for your most critical ICT provider.", placeholder:"Optional — captured for the facilitated review.", readiness:{regime:"dora",dim:"exit_strategy"} },
];

/* ---------- rule engine (verified parity with node/python) ---------- */
function leaf(c,f){
  const v=f[c.fact], op=c.op, val=c.value;
  switch(op){
    case "is_true": return v===true;
    case "is_false": return v===false;
    case "eq": return v===val;
    case "neq": return v!==val;
    case "in": return Array.isArray(val)&&val.includes(v);
    case "not_in": return Array.isArray(val)&&!val.includes(v);
    case "includes_any": return Array.isArray(v)&&val.some(x=>v.includes(x));
    case "includes_all": return Array.isArray(v)&&val.every(x=>v.includes(x));
    case "gte": return v!=null&&v>=val;
    case "lte": return v!=null&&v<=val;
    default: return false;
  }
}
function evalCond(c,f){
  if(!c) return true;
  if(c.all) return c.all.every(x=>evalCond(x,f));
  if(c.any) return c.any.some(x=>evalCond(x,f));
  if(c.not) return !evalCond(c.not,f);
  return leaf(c,f);
}
function mergeFacts(f,fv){
  for(const k of Object.keys(fv)){
    const val=fv[k];
    if(Array.isArray(val)){ f[k]=Array.from(new Set([...(f[k]||[]),...val])); }
    else if(typeof val==="boolean"){ f[k]=f[k]===true||val===true; }
    else { f[k]=val; }
  }
}
function computeFacts(answers){
  const f={};
  for(let pass=0; pass<2; pass++){
    for(const q of QUESTIONS){
      const a=answers[q.id];
      if(a===undefined||a==="__NA__") continue;
      if(q.shown_if && !evalCond(q.shown_if,f)) continue;
      if(q.type==="boolean"){ if(q.writes) f[q.writes]=a; }
      else if(q.type==="range"){ if(q.writes) f[q.writes]=a; }
      else if(q.type==="single_select"){ const opt=q.options[a]; if(opt&&opt.fv) mergeFacts(f,opt.fv); }
      else if(q.type==="multi_select"){ for(const i of a){ const opt=q.options[i]; if(opt&&opt.fv) mergeFacts(f,opt.fv);} }
    }
  }
  return f;
}
function assess(facts){
  const out=[];
  for(const r of REGIMES){
    const fired=r.rules.filter(rl=>evalCond(rl.when,facts)).map(rl=>({grade:rl.grade,why:rl.why}));
    if(fired.length){
      fired.sort((a,b)=>GRADE_PRECEDENCE.indexOf(a.grade)-GRADE_PRECEDENCE.indexOf(b.grade));
      out.push({regime:r,grade:fired[0].grade,why:fired[0].why});
    }
  }
  out.sort((a,b)=>GRADE_PRECEDENCE.indexOf(a.grade)-GRADE_PRECEDENCE.indexOf(b.grade));
  return out;
}
function stageFor(score){ for(const s of STAGES){ if(score>=s.band[0]&&score<=s.band[1]) return s; } return STAGES[STAGES.length-1]; }

function computeReadiness(answers, facts, resultsByRegime){
  const bucket={}; // regimeId -> dimId -> [scores]
  for(const q of QUESTIONS){
    if(!q.readiness) continue;
    const a=answers[q.id];
    if(a===undefined||a==="__NA__") continue;
    if(q.shown_if && !evalCond(q.shown_if,facts)) continue;
    let score=null;
    if(q.type==="rating_1_5"){ score=((a-1)/4)*100; }
    else if(q.type==="single_select"){ const opt=q.options[a]; if(opt&&typeof opt.score==="number") score=opt.score; }
    else if(q.type==="open_text"){ score=null; } // captured, not scored
    if(score===null) continue;
    const {regime,dim}=q.readiness;
    bucket[regime]=bucket[regime]||{};
    (bucket[regime][dim]=bucket[regime][dim]||[]).push(score);
  }
  const regimeScores={};
  for(const r of REGIMES){
    const res=resultsByRegime[r.id];
    if(!res||!["applies","likely_confirm","partial"].includes(res.grade)) continue;
    const b=bucket[r.id]; if(!b) continue;
    let wsum=0, acc=0;
    for(const d of r.dims){
      const arr=b[d.id];
      if(arr&&arr.length){ acc+=(arr.reduce((x,y)=>x+y,0)/arr.length)*d.weight; wsum+=d.weight; }
    }
    if(wsum>0) regimeScores[r.id]=Math.round(acc/wsum);
  }
  let owsum=0, oacc=0;
  for(const r of REGIMES){
    if(regimeScores[r.id]!=null){ oacc+=regimeScores[r.id]*r.weight; owsum+=r.weight; }
  }
  const overall = owsum>0 ? Math.round(oacc/owsum) : null;
  return { regimeScores, overall };
}

/* ============================== UI ============================== */
export default function SovereignScreen(){
  const [screen,setScreen]=useState("intro"); // intro | assess | results
  const [tier,setTier]=useState(1);
  const [answers,setAnswers]=useState({});
  const [step,setStep]=useState(0);

  const facts=useMemo(()=>computeFacts(answers),[answers]);

  const visibleSections=useMemo(()=>{
    return SECTIONS.map(s=>{
      const qs=QUESTIONS.filter(q=>q.cat===s.cat && q.tier<=tier && (!q.shown_if || evalCond(q.shown_if,facts)));
      return {...s, qs};
    }).filter(s=>s.qs.length>0);
  },[facts,tier]);

  const clampedStep=Math.min(step,Math.max(0,visibleSections.length-1));
  const section=visibleSections[clampedStep];

  const totalQ=visibleSections.reduce((n,s)=>n+s.qs.length,0);
  const answeredQ=visibleSections.reduce((n,s)=>n+s.qs.filter(q=>answers[q.id]!==undefined).length,0);
  const pct=totalQ?Math.round((answeredQ/totalQ)*100):0;

  const setAns=(id,val)=>setAnswers(a=>({...a,[id]:val}));

  const results=useMemo(()=>assess(facts),[facts]);
  const byRegime=useMemo(()=>{const m={};for(const r of results)m[r.regime.id]=r;return m;},[results]);
  const readiness=useMemo(()=>computeReadiness(answers,facts,byRegime),[answers,facts,byRegime]);

  return (
    <div className="ss-root">
      <StyleBlock/>
      <div className="ss-gridbg" aria-hidden="true"/>
      <header className="ss-bar">
        <div className="ss-brand">
          <span className="ss-mark" aria-hidden="true"/>
          <div>
            <div className="ss-eyebrow">LTIMindtree · Digital Sovereignty Accelerator</div>
            <div className="ss-brandtitle">Sovereign Screen <span className="ss-brandtag">Financial Services · UK &amp; EU</span></div>
          </div>
        </div>
        <div className="ss-tier" role="group" aria-label="Assessment depth">
          <button className={"ss-tierbtn"+(tier===1?" on":"")} onClick={()=>setTier(1)} disabled={screen==="results"}>Indicative</button>
          <button className={"ss-tierbtn"+(tier===2?" on":"")} onClick={()=>setTier(2)} disabled={screen==="results"}>Extended</button>
        </div>
      </header>

      {screen==="intro" && <Intro tier={tier} onStart={()=>{setStep(0);setScreen("assess");}}/>}

      {screen==="assess" && section && (
        <main className="ss-shell">
          <nav className="ss-rail" aria-label="Sections">
            {visibleSections.map((s,i)=>{
              const done=s.qs.every(q=>answers[q.id]!==undefined);
              const active=i===clampedStep;
              return (
                <button key={s.cat} className={"ss-railitem"+(active?" active":"")+(done?" done":"")} onClick={()=>setStep(i)}>
                  <span className="ss-railn">{s.n}</span>
                  <span className="ss-raill">{s.label}</span>
                  {done && <span className="ss-railcheck" aria-hidden="true">✓</span>}
                </button>
              );
            })}
          </nav>

          <section className="ss-main">
            <div className="ss-progress"><div className="ss-progressfill" style={{width:pct+"%"}}/></div>
            <div className="ss-sechead">
              <span className="ss-secn">{section.n}</span>
              <div>
                <h2 className="ss-h2">{section.label}</h2>
                <p className="ss-blurb">{section.blurb}</p>
              </div>
            </div>

            <div className="ss-qs">
              {section.qs.map(q=><Question key={q.id} q={q} value={answers[q.id]} onChange={v=>setAns(q.id,v)}/>)}
            </div>

            <div className="ss-nav">
              <button className="ss-btn ghost" onClick={()=>clampedStep===0?setScreen("intro"):setStep(clampedStep-1)}>
                {clampedStep===0?"← Intro":"← Back"}
              </button>
              <div className="ss-navmeta ss-mono">{answeredQ}/{totalQ} answered</div>
              {clampedStep<visibleSections.length-1
                ? <button className="ss-btn primary" onClick={()=>setStep(clampedStep+1)}>Next →</button>
                : <button className="ss-btn primary" onClick={()=>setScreen("results")}>See results →</button>}
            </div>
          </section>
        </main>
      )}

      {screen==="results" && (
        <Results results={results} readiness={readiness} facts={facts}
          onEdit={()=>setScreen("assess")}
          onReset={()=>{setAnswers({});setStep(0);setScreen("intro");}}/>
      )}
    </div>
  );
}

function Intro({onStart,tier}){
  return (
    <main className="ss-intro">
      <div className="ss-introinner">
        <div className="ss-eyebrow">Digital sovereignty triage</div>
        <h1 className="ss-h1">Where your data lives<br/>is not who can reach it.</h1>
        <p className="ss-lead">
          A short screen of which UK &amp; EU digital-sovereignty laws apply to your business — and how ready you are against them.
          Physical residency is the easy half; jurisdictional reach is the half that gets missed.
        </p>
        <div className="ss-signature" aria-hidden="true">
          <div className="ss-signode"><div className="ss-sigk">Data location</div><div className="ss-sigv">EU region</div></div>
          <div className="ss-sigbridge"><span>US&nbsp;CLOUD&nbsp;Act reach</span></div>
          <div className="ss-signode alt"><div className="ss-sigk">Legal reach</div><div className="ss-sigv">US provider HQ</div></div>
        </div>
        <div className="ss-introfoot">
          <button className="ss-btn primary lg" onClick={onStart}>Start the screen →</button>
          <p className="ss-fine">
            {tier===1 ? "Indicative mode: self-serve, closed questions." : "Extended mode: adds facilitated, open-ended prompts."}
            {" "}Triage only — not legal advice.
          </p>
        </div>
      </div>
    </main>
  );
}

function Question({q,value,onChange}){
  return (
    <div className="ss-q">
      <div className="ss-qtext">{q.text}</div>
      {q.hint && <div className="ss-qhint">{q.hint}</div>}
      {q.type==="single_select" && <SingleSelect q={q} value={value} onChange={onChange}/>}
      {q.type==="multi_select" && <MultiSelect q={q} value={value} onChange={onChange}/>}
      {q.type==="boolean" && <BoolToggle value={value} onChange={onChange}/>}
      {q.type==="rating_1_5" && <Rating value={value} onChange={onChange}/>}
      {q.type==="range" && <RangeInput q={q} value={value} onChange={onChange}/>}
      {q.type==="drag_order" && <DragOrder q={q} value={value} onChange={onChange}/>}
      {q.type==="open_text" && <textarea className="ss-textarea" placeholder={q.placeholder||""} value={value==="__NA__"?"":(value||"")} onChange={e=>onChange(e.target.value)}/>}
    </div>
  );
}

function SingleSelect({q,value,onChange}){
  return (
    <div className="ss-opts">
      {q.options.map((o,i)=>(
        <button key={i} className={"ss-opt"+(value===i?" sel":"")} onClick={()=>onChange(value===i?undefined:i)}>
          <span className="ss-optdot" aria-hidden="true"/>{o.label}
        </button>
      ))}
      {q.na && <button className={"ss-opt na"+(value==="__NA__"?" sel":"")} onClick={()=>onChange(value==="__NA__"?undefined:"__NA__")}>Not applicable</button>}
    </div>
  );
}

function MultiSelect({q,value,onChange}){
  const arr=Array.isArray(value)?value:[];
  const toggle=i=>{ const next=arr.includes(i)?arr.filter(x=>x!==i):[...arr,i]; onChange(next.length?next:undefined); };
  return (
    <div className="ss-opts">
      {q.options.map((o,i)=>(
        <button key={i} className={"ss-opt multi"+(arr.includes(i)?" sel":"")} onClick={()=>toggle(i)}>
          <span className="ss-optbox" aria-hidden="true">{arr.includes(i)?"✓":""}</span>{o.label}
        </button>
      ))}
      {q.na && <button className={"ss-opt na"+(value==="__NA__"?" sel":"")} onClick={()=>onChange(value==="__NA__"?undefined:"__NA__")}>Not applicable</button>}
    </div>
  );
}

function BoolToggle({value,onChange}){
  return (
    <div className="ss-bool">
      <button className={"ss-boolbtn"+(value===true?" on":"")} onClick={()=>onChange(value===true?undefined:true)}>Yes</button>
      <button className={"ss-boolbtn"+(value===false?" on":"")} onClick={()=>onChange(value===false?undefined:false)}>No</button>
    </div>
  );
}

function Rating({value,onChange}){
  const labels=["Nascent","Emerging","Developing","Strong","Leading"];
  return (
    <div className="ss-rating">
      {[1,2,3,4,5].map(n=>(
        <button key={n} className={"ss-ratebtn"+(value===n?" on":"")} onClick={()=>onChange(value===n?undefined:n)}>
          <span className="ss-raten">{n}</span><span className="ss-ratel">{labels[n-1]}</span>
        </button>
      ))}
    </div>
  );
}

function RangeInput({q,value,onChange}){
  const {min,max,step,suffix}=q.range;
  const v=value===undefined?min:value;
  return (
    <div className="ss-rangewrap">
      <input className="ss-range" type="range" min={min} max={max} step={step||1} value={v} onChange={e=>onChange(Number(e.target.value))}/>
      <div className="ss-rangeval ss-mono">{v}{suffix||""}</div>
    </div>
  );
}

function DragOrder({q,value,onChange}){
  const order=Array.isArray(value)?value:q.options.slice();
  useEffect(()=>{ if(!Array.isArray(value)) onChange(q.options.slice()); /* eslint-disable-next-line */ },[]);
  const move=(i,d)=>{ const j=i+d; if(j<0||j>=order.length) return; const next=order.slice(); [next[i],next[j]]=[next[j],next[i]]; onChange(next); };
  const dragI=useRef(null);
  return (
    <ol className="ss-drag">
      {order.map((item,i)=>(
        <li key={item} className="ss-dragitem" draggable
            onDragStart={()=>dragI.current=i}
            onDragOver={e=>e.preventDefault()}
            onDrop={()=>{const from=dragI.current; if(from==null||from===i)return; const next=order.slice(); const [m]=next.splice(from,1); next.splice(i,0,m); onChange(next); dragI.current=null;}}>
          <span className="ss-dragrank ss-mono">{i+1}</span>
          <span className="ss-draglabel">{item}</span>
          <span className="ss-dragctl">
            <button aria-label="Move up" onClick={()=>move(i,-1)} disabled={i===0}>▲</button>
            <button aria-label="Move down" onClick={()=>move(i,1)} disabled={i===order.length-1}>▼</button>
          </span>
        </li>
      ))}
    </ol>
  );
}

function Results({results,readiness,facts,onEdit,onReset}){
  const [anim,setAnim]=useState(false);
  useEffect(()=>{const t=setTimeout(()=>setAnim(true),80);return()=>clearTimeout(t);},[]);
  const inScope=results.filter(r=>["applies","likely_confirm","partial"].includes(r.grade));
  const advisories=results.filter(r=>["advisory","needs_legal_review"].includes(r.grade));
  const overall=readiness.overall;
  const stage=overall!=null?stageFor(overall):null;
  const showSig=!!results.find(r=>r.regime.id==="data_transfer_jurisdiction");

  const counts={
    applies:results.filter(r=>r.grade==="applies").length,
    review:results.filter(r=>r.grade==="needs_legal_review").length,
    advisory:results.filter(r=>r.grade==="advisory").length,
  };

  return (
    <main className="ss-results">
      <div className="ss-eyebrow">Assessment result · indicative</div>

      <div className="ss-hero">
        <div className="ss-herotext">
          <h1 className="ss-h1 sm">{stage?stage.label:"Not yet scored"}</h1>
          <p className="ss-lead">{stage?stage.desc:"Answer the readiness questions to place your organisation on the maturity spine."}</p>
          <div className="ss-statrow ss-mono">
            <span><b>{inScope.length}</b> regimes in scope</span>
            <span><b>{counts.advisory}</b> advisories</span>
            <span><b>{counts.review}</b> need legal review</span>
          </div>
        </div>
        <div className="ss-scorebubble">
          <div className="ss-scoreval ss-mono">{overall!=null?overall:"—"}</div>
          <div className="ss-scorelab">readiness</div>
        </div>
      </div>

      <Gauge current={stage?stage.stage:0} score={overall} anim={anim}/>

      {showSig && <SignaturePanel facts={facts}/>}

      <h2 className="ss-h2 mt">Regimes in scope</h2>
      <div className="ss-regimes">
        {inScope.map(r=><RegimeCard key={r.regime.id} r={r} score={readiness.regimeScores[r.regime.id]}/>)}
        {inScope.length===0 && <p className="ss-blurb">No hard obligations triggered on these answers. Review the advisories below and confirm scope with counsel.</p>}
      </div>

      {advisories.length>0 && (
        <>
          <h2 className="ss-h2 mt">Sovereignty flags</h2>
          <div className="ss-regimes">
            {advisories.map(r=><RegimeCard key={r.regime.id} r={r} score={readiness.regimeScores[r.regime.id]}/>)}
          </div>
        </>
      )}

      <div className="ss-cta">
        <div>
          <div className="ss-eyebrow">What this is — and isn't</div>
          <p className="ss-ctatext">
            This is an indicative screen, not legal advice. It maps which regimes apply and how ready you look today.
            A facilitated LTM assessment validates scope, closes the gaps behind each score, and builds the sovereignty roadmap.
          </p>
        </div>
        <div className="ss-ctabtns">
          <button className="ss-btn ghost" onClick={onEdit}>Review answers</button>
          <button className="ss-btn primary" onClick={onReset}>Start over</button>
        </div>
      </div>
    </main>
  );
}

function Gauge({current,score,anim}){
  const fill=anim&&score!=null?score:0;
  return (
    <div className="ss-gauge">
      <div className="ss-gaugetrack">
        <div className="ss-gaugefill" style={{width:fill+"%"}}/>
        {[20,40,60,80].map(t=><div key={t} className="ss-gaugetick" style={{left:t+"%"}}/>)}
      </div>
      <div className="ss-gaugelabels">
        {STAGES.map(s=>(
          <div key={s.stage} className={"ss-gstage"+(s.stage===current?" on":"")}>
            <span className="ss-gsn ss-mono">0{s.stage}</span>
            <span className="ss-gsl">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function SignaturePanel({facts}){
  const loc=(facts.data_hosting_location||[]).join(" · ")||"—";
  const usReach=(facts.cloud_provider_hq||[]).includes("US")||facts.uses_us_hyperscaler;
  return (
    <div className="ss-sigpanel">
      <div className="ss-sigpanelhead">
        <span className="ss-eyebrow">Residency ≠ sovereignty</span>
        <span className="ss-sigpanelsub">Physical location vs legal reach</span>
      </div>
      <div className="ss-sigdiagram">
        <div className="ss-signode"><div className="ss-sigk">Data location</div><div className="ss-sigv">{loc}</div></div>
        <div className={"ss-sigbridge"+(usReach?" hot":"")}><span>{usReach?"US CLOUD Act reach":"provider jurisdiction"}</span></div>
        <div className="ss-signode alt"><div className="ss-sigk">Legal reach</div><div className="ss-sigv">{usReach?"US (provider HQ)":"aligned"}</div></div>
      </div>
      <p className="ss-sigcopy">{usReach
        ? "Your data may sit inside the EU/UK while remaining reachable by a foreign jurisdiction through your provider's home law. Localisation alone does not close this gap."
        : "Provider jurisdiction appears aligned with your data location — confirm contractual and operational controls to keep it that way."}</p>
    </div>
  );
}

function RegimeCard({r,score}){
  const g=GRADE_META[r.grade];
  const st=score!=null?stageFor(score):null;
  return (
    <details className="ss-card">
      <summary className="ss-cardsum">
        <div className="ss-cardmain">
          <div className="ss-cardname">{r.regime.name}</div>
          <div className="ss-cardshort ss-mono">{r.regime.short}</div>
        </div>
        <div className="ss-cardright">
          {score!=null && <span className="ss-cardstage ss-mono" title="Readiness stage">S{st.stage}</span>}
          <span className="ss-tag" style={{color:g.c,borderColor:g.c}}>{g.label}</span>
          <span className="ss-chev" aria-hidden="true">▾</span>
        </div>
      </summary>
      <div className="ss-cardbody">
        <p className="ss-why">{r.why}</p>
        {score!=null && (
          <div className="ss-readbar">
            <div className="ss-readbartrack"><div className="ss-readbarfill" style={{width:score+"%",background:g.c}}/></div>
            <span className="ss-mono ss-readbarval">{score} · {st.label}</span>
          </div>
        )}
        <div className="ss-oblabel ss-eyebrow">Sovereignty-relevant obligations</div>
        <ul className="ss-obl">{r.regime.obligations.map((o,i)=><li key={i}>{o}</li>)}</ul>
      </div>
    </details>
  );
}

function StyleBlock(){
  return (<style>{`
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

.ss-root{
  --ground:#0A1826; --panel:#0F2438; --panel2:#12304A; --line:#22415C;
  --ink:#E8EFF6; --mut:#93A8BD; --mutd:#6E869C;
  --navy:#003865; --red:#F15F53; --amber:#FBAE40; --steel:#57B6C2; --lilac:#9B82D0; --blue:#58A6E0;
  position:relative; min-height:100%; color:var(--ink); background:var(--ground);
  font-family:'IBM Plex Sans',system-ui,sans-serif; line-height:1.5; overflow-x:hidden;
}
.ss-root *{box-sizing:border-box;}
.ss-gridbg{position:fixed; inset:0; pointer-events:none; opacity:.5;
  background-image:linear-gradient(rgba(87,182,194,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(87,182,194,.05) 1px,transparent 1px);
  background-size:48px 48px; mask-image:radial-gradient(ellipse at 50% 0%,#000 30%,transparent 78%);}

.ss-mono{font-family:'IBM Plex Mono',monospace;}
.ss-eyebrow{font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--steel);}
.ss-h1{font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:clamp(30px,5vw,52px); line-height:1.04; letter-spacing:-.02em; margin:.2em 0;}
.ss-h1.sm{font-size:clamp(26px,4vw,40px);}
.ss-h2{font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:22px; letter-spacing:-.01em; margin:0;}
.ss-h2.mt{margin-top:34px;}
.ss-lead{color:var(--mut); font-size:17px; max-width:52ch;}
.ss-blurb{color:var(--mut); font-size:14px; margin:2px 0 0;}

/* bar */
.ss-bar{position:relative; z-index:2; display:flex; align-items:center; justify-content:space-between; gap:16px;
  padding:16px clamp(16px,4vw,40px); border-bottom:1px solid var(--line); background:rgba(10,24,38,.7); backdrop-filter:blur(6px);}
.ss-brand{display:flex; align-items:center; gap:12px;}
.ss-mark{width:26px; height:26px; border-radius:4px; background:conic-gradient(from 210deg,var(--red),var(--amber),var(--steel),var(--red)); box-shadow:inset 0 0 0 3px var(--ground);}
.ss-brandtitle{font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:16px;}
.ss-brandtag{color:var(--mutd); font-weight:400; font-size:12px; margin-left:8px;}
.ss-tier{display:flex; border:1px solid var(--line); border-radius:999px; padding:3px; background:var(--panel);}
.ss-tierbtn{font-family:'IBM Plex Mono',monospace; font-size:12px; letter-spacing:.04em; color:var(--mut); background:none; border:none; padding:6px 14px; border-radius:999px; cursor:pointer;}
.ss-tierbtn.on{background:var(--navy); color:#fff;}
.ss-tierbtn:disabled{opacity:.4; cursor:not-allowed;}

/* intro */
.ss-intro{position:relative; z-index:1; display:flex; justify-content:center; padding:clamp(28px,7vw,80px) clamp(16px,4vw,40px);}
.ss-introinner{max-width:760px; width:100%;}
.ss-signature{display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:0; margin:34px 0; border:1px solid var(--line); border-radius:14px; overflow:hidden; background:var(--panel);}
.ss-signode{padding:20px 22px;}
.ss-signode.alt{text-align:right; background:linear-gradient(90deg,transparent,rgba(241,95,83,.08));}
.ss-sigk{font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:var(--mutd);}
.ss-sigv{font-family:'Space Grotesk',sans-serif; font-size:20px; font-weight:600; margin-top:4px;}
.ss-sigbridge{position:relative; height:100%; min-height:64px; width:150px; display:flex; align-items:center; justify-content:center; border-left:1px dashed var(--line); border-right:1px dashed var(--line);}
.ss-sigbridge span{font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:.08em; color:var(--amber); text-align:center; padding:0 8px;}
.ss-sigbridge.hot span{color:var(--red);}
.ss-introfoot{margin-top:8px;}
.ss-fine{color:var(--mutd); font-size:12.5px; margin-top:12px;}

/* buttons */
.ss-btn{font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:14px; padding:11px 18px; border-radius:10px; cursor:pointer; border:1px solid transparent; transition:transform .12s ease,background .12s ease,border-color .12s;}
.ss-btn:hover{transform:translateY(-1px);}
.ss-btn.primary{background:var(--red); color:#160404;}
.ss-btn.primary:hover{background:#ff6f63;}
.ss-btn.ghost{background:transparent; color:var(--ink); border-color:var(--line);}
.ss-btn.ghost:hover{border-color:var(--steel);}
.ss-btn.lg{font-size:16px; padding:14px 24px;}

/* shell */
.ss-shell{position:relative; z-index:1; display:grid; grid-template-columns:236px 1fr; gap:0; max-width:1100px; margin:0 auto; min-height:calc(100vh - 60px);}
.ss-rail{border-right:1px solid var(--line); padding:26px 14px; display:flex; flex-direction:column; gap:4px;}
.ss-railitem{display:flex; align-items:center; gap:10px; padding:9px 12px; border-radius:9px; border:none; background:none; color:var(--mut); cursor:pointer; text-align:left; font-size:13.5px; width:100%;}
.ss-railitem:hover{background:var(--panel);}
.ss-railitem.active{background:var(--panel); color:var(--ink);}
.ss-railitem.active .ss-railn{color:var(--red);}
.ss-railn{font-family:'IBM Plex Mono',monospace; font-size:11px; color:var(--mutd);}
.ss-raill{flex:1;}
.ss-railcheck{color:var(--steel); font-size:12px;}
.ss-railitem.done .ss-raill{color:var(--ink);}

.ss-main{padding:26px clamp(18px,3vw,40px) 40px;}
.ss-progress{height:3px; background:var(--line); border-radius:2px; overflow:hidden; margin-bottom:26px;}
.ss-progressfill{height:100%; background:linear-gradient(90deg,var(--steel),var(--amber)); transition:width .3s ease;}
.ss-sechead{display:flex; gap:14px; align-items:flex-start; margin-bottom:24px;}
.ss-secn{font-family:'IBM Plex Mono',monospace; font-size:13px; color:var(--red); border:1px solid var(--line); border-radius:8px; padding:6px 9px;}
.ss-qs{display:flex; flex-direction:column; gap:26px;}
.ss-q{border-top:1px solid var(--line); padding-top:20px;}
.ss-q:first-child{border-top:none; padding-top:0;}
.ss-qtext{font-size:16px; font-weight:500; margin-bottom:4px;}
.ss-qhint{color:var(--amber); font-size:12.5px; margin-bottom:12px; font-family:'IBM Plex Mono',monospace;}
.ss-q .ss-qtext + .ss-opts,.ss-q .ss-qtext + .ss-bool,.ss-q .ss-qtext + .ss-rating,.ss-q .ss-qtext + .ss-rangewrap{margin-top:12px;}

/* options */
.ss-opts{display:flex; flex-direction:column; gap:8px;}
.ss-opt{display:flex; align-items:center; gap:11px; text-align:left; padding:13px 15px; border-radius:10px; border:1px solid var(--line); background:var(--panel); color:var(--ink); cursor:pointer; font-size:14.5px; transition:border-color .12s,background .12s;}
.ss-opt:hover{border-color:var(--steel);}
.ss-opt.sel{border-color:var(--red); background:rgba(241,95,83,.08);}
.ss-optdot{width:13px; height:13px; border-radius:50%; border:2px solid var(--mutd); flex:none;}
.ss-opt.sel .ss-optdot{border-color:var(--red); background:var(--red); box-shadow:inset 0 0 0 2px var(--panel);}
.ss-optbox{width:18px; height:18px; border-radius:5px; border:2px solid var(--mutd); flex:none; display:flex; align-items:center; justify-content:center; font-size:11px; color:var(--ground);}
.ss-opt.sel .ss-optbox{border-color:var(--red); background:var(--red);}
.ss-opt.na{border-style:dashed; color:var(--mut);}

/* bool */
.ss-bool{display:flex; gap:8px;}
.ss-boolbtn{flex:1; padding:13px; border-radius:10px; border:1px solid var(--line); background:var(--panel); color:var(--ink); font-family:'Space Grotesk',sans-serif; font-weight:600; cursor:pointer;}
.ss-boolbtn:hover{border-color:var(--steel);}
.ss-boolbtn.on{border-color:var(--red); background:rgba(241,95,83,.1);}

/* rating */
.ss-rating{display:grid; grid-template-columns:repeat(5,1fr); gap:8px;}
.ss-ratebtn{display:flex; flex-direction:column; align-items:center; gap:4px; padding:12px 6px; border-radius:10px; border:1px solid var(--line); background:var(--panel); color:var(--mut); cursor:pointer;}
.ss-ratebtn:hover{border-color:var(--steel);}
.ss-ratebtn.on{border-color:var(--amber); background:rgba(251,174,64,.1); color:var(--ink);}
.ss-raten{font-family:'Space Grotesk',sans-serif; font-size:20px; font-weight:600;}
.ss-ratel{font-size:10.5px; letter-spacing:.02em;}

/* range */
.ss-rangewrap{display:flex; align-items:center; gap:16px;}
.ss-range{flex:1; accent-color:var(--red);}
.ss-rangeval{font-size:14px; color:var(--ink); min-width:120px;}

/* drag */
.ss-drag{list-style:none; margin:12px 0 0; padding:0; display:flex; flex-direction:column; gap:8px;}
.ss-dragitem{display:flex; align-items:center; gap:12px; padding:11px 14px; border-radius:10px; border:1px solid var(--line); background:var(--panel); cursor:grab;}
.ss-dragrank{color:var(--red); font-size:14px;}
.ss-draglabel{flex:1; font-size:14.5px;}
.ss-dragctl{display:flex; gap:4px;}
.ss-dragctl button{width:26px; height:26px; border-radius:6px; border:1px solid var(--line); background:var(--ground); color:var(--mut); cursor:pointer; font-size:10px;}
.ss-dragctl button:disabled{opacity:.3; cursor:not-allowed;}

.ss-textarea{width:100%; min-height:96px; margin-top:12px; padding:13px 15px; border-radius:10px; border:1px solid var(--line); background:var(--panel); color:var(--ink); font-family:inherit; font-size:14.5px; resize:vertical;}
.ss-textarea:focus{outline:none; border-color:var(--steel);}

/* nav */
.ss-nav{display:flex; align-items:center; justify-content:space-between; gap:12px; margin-top:32px; padding-top:20px; border-top:1px solid var(--line);}
.ss-navmeta{font-size:12px; color:var(--mutd);}

/* results */
.ss-results{position:relative; z-index:1; max-width:920px; margin:0 auto; padding:30px clamp(16px,4vw,40px) 60px;}
.ss-hero{display:flex; align-items:center; justify-content:space-between; gap:24px; margin:8px 0 26px; flex-wrap:wrap;}
.ss-herotext{flex:1; min-width:260px;}
.ss-statrow{display:flex; gap:22px; flex-wrap:wrap; margin-top:14px; font-size:13px; color:var(--mut);}
.ss-statrow b{color:var(--ink);}
.ss-scorebubble{width:120px; height:120px; border-radius:50%; border:1px solid var(--line); background:radial-gradient(circle at 50% 40%,rgba(87,182,194,.14),transparent 70%); display:flex; flex-direction:column; align-items:center; justify-content:center; flex:none;}
.ss-scoreval{font-size:38px; font-weight:600; color:var(--ink);}
.ss-scorelab{font-family:'IBM Plex Mono',monospace; font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--mutd);}

/* gauge */
.ss-gauge{margin:6px 0 30px;}
.ss-gaugetrack{position:relative; height:12px; border-radius:6px; background:var(--panel); border:1px solid var(--line); overflow:hidden;}
.ss-gaugefill{position:absolute; left:0; top:0; bottom:0; background:linear-gradient(90deg,var(--red),var(--amber),var(--steel)); transition:width 1.1s cubic-bezier(.22,1,.36,1);}
.ss-gaugetick{position:absolute; top:-1px; bottom:-1px; width:1px; background:var(--ground);}
.ss-gaugelabels{display:grid; grid-template-columns:repeat(5,1fr); margin-top:10px;}
.ss-gstage{display:flex; flex-direction:column; gap:3px; padding-right:8px;}
.ss-gsn{font-size:11px; color:var(--mutd);}
.ss-gsl{font-size:12px; color:var(--mut);}
.ss-gstage.on .ss-gsn{color:var(--red);}
.ss-gstage.on .ss-gsl{color:var(--ink); font-weight:600;}

/* signature panel */
.ss-sigpanel{border:1px solid var(--line); border-radius:14px; background:var(--panel); padding:22px; margin:6px 0 4px;}
.ss-sigpanelhead{display:flex; align-items:baseline; justify-content:space-between; gap:10px; flex-wrap:wrap; margin-bottom:16px;}
.ss-sigpanelsub{font-size:12.5px; color:var(--mutd);}
.ss-sigdiagram{display:grid; grid-template-columns:1fr auto 1fr; align-items:stretch; border:1px solid var(--line); border-radius:10px; overflow:hidden; background:var(--ground);}
.ss-sigcopy{color:var(--mut); font-size:13.5px; margin:14px 0 0; max-width:64ch;}

/* regime cards */
.ss-regimes{display:flex; flex-direction:column; gap:10px; margin-top:14px;}
.ss-card{border:1px solid var(--line); border-radius:12px; background:var(--panel); overflow:hidden;}
.ss-card[open]{border-color:var(--panel2);}
.ss-cardsum{display:flex; align-items:center; justify-content:space-between; gap:14px; padding:16px 18px; cursor:pointer; list-style:none;}
.ss-cardsum::-webkit-details-marker{display:none;}
.ss-cardname{font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:16px;}
.ss-cardshort{font-size:11.5px; color:var(--mutd); margin-top:2px; letter-spacing:.02em;}
.ss-cardright{display:flex; align-items:center; gap:12px; flex:none;}
.ss-cardstage{font-size:12px; color:var(--steel); border:1px solid var(--line); border-radius:6px; padding:3px 7px;}
.ss-tag{font-family:'IBM Plex Mono',monospace; font-size:11px; letter-spacing:.03em; padding:5px 10px; border-radius:999px; border:1px solid; white-space:nowrap;}
.ss-chev{color:var(--mutd); font-size:11px; transition:transform .2s;}
.ss-card[open] .ss-chev{transform:rotate(180deg);}
.ss-cardbody{padding:0 18px 18px; border-top:1px solid var(--line);}
.ss-why{color:var(--mut); font-size:14px; margin:14px 0 12px;}
.ss-readbar{display:flex; align-items:center; gap:12px; margin-bottom:16px;}
.ss-readbartrack{flex:1; height:7px; border-radius:4px; background:var(--ground); border:1px solid var(--line); overflow:hidden;}
.ss-readbarfill{height:100%; transition:width .9s cubic-bezier(.22,1,.36,1);}
.ss-readbarval{font-size:12px; color:var(--mut); min-width:120px; text-align:right;}
.ss-oblabel{display:block; margin-bottom:8px;}
.ss-obl{margin:0; padding-left:18px; color:var(--ink); font-size:13.5px;}
.ss-obl li{margin:5px 0;}

/* cta */
.ss-cta{display:flex; align-items:center; justify-content:space-between; gap:20px; flex-wrap:wrap; margin-top:36px; padding:22px; border:1px solid var(--line); border-radius:14px; background:linear-gradient(120deg,rgba(0,56,101,.28),rgba(68,38,113,.18));}
.ss-ctatext{color:var(--mut); font-size:14px; max-width:60ch; margin:8px 0 0;}
.ss-ctabtns{display:flex; gap:10px; flex:none;}

.ss-root :focus-visible{outline:2px solid var(--steel); outline-offset:2px;}
@media (max-width:820px){
  .ss-shell{grid-template-columns:1fr;}
  .ss-rail{flex-direction:row; overflow-x:auto; border-right:none; border-bottom:1px solid var(--line); padding:12px;}
  .ss-railitem{flex:none;}
  .ss-railcheck{display:none;}
  .ss-signature,.ss-sigdiagram{grid-template-columns:1fr;}
  .ss-sigbridge{width:auto; min-height:40px; border-left:none; border-right:none; border-top:1px dashed var(--line); border-bottom:1px dashed var(--line);}
  .ss-signode.alt{text-align:left;}
}
@media (prefers-reduced-motion:reduce){
  .ss-root *{transition:none !important;}
}
`}</style>);
}
