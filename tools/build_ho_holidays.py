#!/usr/bin/env python3
"""Add school holidays to the Human Override list (human-override/extension/lists.json -> "holidays").
Source: OpenHolidays API data (github.com/openpotato/openholidaysapi.data), licence ODbL 1.0 (attribution in the list).
    git clone --depth 1 https://github.com/openpotato/openholidaysapi.data /tmp/oh
    python3 tools/build_ho_holidays.py /tmp/oh
Then run tools/build_ho_lists.py as usual."""
import csv, datetime, json, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
# region code -> (csv file, group short name or None = the whole file)
REGIONS = {
    'BE-NL': ('be/holidays/holidays.school.nl.csv', None), 'BE-FR': ('be/holidays/holidays.school.fr.csv', None),
    'NL-NO': ('nl/holidays/holidays.school.csv', 'NO'), 'NL-MI': ('nl/holidays/holidays.school.csv', 'MI'),
    'NL-ZU': ('nl/holidays/holidays.school.csv', 'ZU'),
    'FR-ZA': ('fr/holidays/holidays.school.csv', 'ZA'), 'FR-ZB': ('fr/holidays/holidays.school.csv', 'ZB'),
    'FR-ZC': ('fr/holidays/holidays.school.csv', 'ZC'),
}
today = datetime.date.today(); lo, hi = (today - datetime.timedelta(days=60)).isoformat(), f'{today.year + 2}-12-31'
out = {}
for code, (rel, grp) in REGIONS.items():
    rows = []
    with open(os.path.join(SRC, 'src', rel), encoding='utf-8-sig') as f:
        for r in csv.DictReader(f, delimiter=';'):
            groups = [g.strip() for g in (r.get('Groups') or r.get('Subdivisions') or '').split(',') if g.strip()]
            if grp and grp not in groups: continue
            s, e = r['StartDate'], r['EndDate']
            if e < lo or s > hi: continue
            datetime.date.fromisoformat(s); datetime.date.fromisoformat(e)   # validate
            rows.append([s, e])
    if not rows: print('WARN no future dates for', code); continue   # (the German-speaking community had none in Nov 2026)
    out[code] = sorted({tuple(x) for x in rows})
    out[code] = [list(x) for x in out[code]]
    print(code, len(out[code]), out[code][:1])
p = 'human-override/extension/lists.json'
L = json.load(open(p))
L['holidays'] = {'source': 'OpenHolidays API data (openholidaysapi.org), licence ODbL 1.0', 'regions': out}
json.dump(L, open(p, 'w'), indent=1)
