import json
kb = json.load(open('ds-knowledge-base.finance.json'))
prec = kb['meta']['grade_precedence']

def leaf(c, f):
    v = f.get(c['fact']); op = c['op']; val = c.get('value')
    if op=='is_true': return v is True
    if op=='is_false': return v is False
    if op=='eq': return v==val
    if op=='neq': return v!=val
    if op=='in': return v in val
    if op=='not_in': return v not in val
    if op=='gte': return v is not None and v>=val
    if op=='lte': return v is not None and v<=val
    if op=='includes_any': return bool(set(v or []) & set(val))
    if op=='includes_all': return set(val).issubset(set(v or []))
    return False

def ev(c, f):
    if 'all' in c: return all(ev(x,f) for x in c['all'])
    if 'any' in c: return any(ev(x,f) for x in c['any'])
    if 'not' in c: return not ev(c['not'],f)
    return leaf(c,f)

def assess(facts):
    out=[]
    for r in kb['regimes']:
        fired=[(rl['grade'], rl['rationale']) for rl in r['applicability_rules'] if ev(rl['when'],facts)]
        if fired:
            grade=min((g for g,_ in fired), key=lambda g: prec.index(g))
            why=[ra for g,ra in fired if g==grade][0]
            out.append((r['name'], grade, why))
    order={g:i for i,g in enumerate(prec)}
    return sorted(out, key=lambda x: order[x[1]])

# Sample: UK+EU-operating bank, EU/UK data subjects, standard US-hyperscaler region, credit-scoring AI, medium
profile = {
  'entity_role':'financial_entity','fin_entity_type':'credit_institution',
  'establishment_eu':True,'establishment_uk':True,'offers_services_eu':True,'offers_services_uk':True,
  'processes_personal_data':True,'data_subjects_geo':['EU','UK'],
  'data_hosting_location':['EU'],'cloud_provider_hq':['US'],'uses_us_hyperscaler':True,'sovereign_offering_status':'no',
  'company_size':'medium','uses_high_risk_ai':True,'is_or_uses_designated_ctp':'yes','ict_concentration_risk':True
}
print("PROFILE: UK+EU credit institution, EU/UK data subjects, EU-region but US-HQ hyperscaler (standard), credit-scoring AI, medium size\n")
for name,grade,why in assess(profile):
    print(f"[{grade.upper():17}] {name}")
    print(f"                     -> {why[:150]}...")
    print()
