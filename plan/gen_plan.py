"""Writes the default plan (the athlete's starting config) for the app to use offline before its first sync.

The plan engine itself lives in server/app/engine and runs on the server, so editing races in the app regenerates
the plan there. This script only refreshes the bundled copy.

    python3 plan/gen_plan.py          # write plan/plan.json and app/assets/plan.json
    python3 plan/gen_plan.py --check  # CI: fail if the bundled copy is out of date
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, 'server'))
from app.engine.build import plan_text  # noqa: E402

TARGET_FILES = [os.path.join(HERE, 'plan.json'), os.path.join(ROOT, 'app', 'assets', 'plan.json')]

if __name__ == '__main__':
    text = plan_text()
    if '--check' in sys.argv:
        bad = [p for p in TARGET_FILES if not os.path.exists(p) or open(p, encoding='utf-8').read() != text]
        if bad:
            print('Out of date (run python3 plan/gen_plan.py and commit):', *bad, sep='\n  ')
            sys.exit(1)
        print('plan.json is up to date in both places')
    else:
        for p in TARGET_FILES:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(text)
        print('wrote', len(text) // 1024, 'KB to', len(TARGET_FILES), 'files')
