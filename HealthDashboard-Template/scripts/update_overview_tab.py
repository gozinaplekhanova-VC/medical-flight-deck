#!/usr/bin/env python3
"""Overview tab design — health clusters, abnormal markers, action items.

This script replaces the sec-ov (Overview) section in index.html with:
  1. Health index score ring
  2. Health cluster cards (groups of related abnormal findings)
  3. Key abnormal markers with trends
  4. Next actions / recommendations

TODO: Replace placeholder content with your actual health data.
Read from 02_TABLES/*.csv and generate overview dynamically.
"""

import re, os, json

HTML = './/05_SITE/index.html'
RULES_OUT = './/02_TABLES/overview_rules.json'

# The script:
# 1. Reads index.html
# 2. Finds the sec-ov section
# 3. Replaces it with structured overview content
# 4. Writes overview_rules.json with display configuration

# Example overview structure:
#
#   <div id="sec-ov" class="sec active">
#     <p class="section-title">Overview</p>
#     <div class="ov-stats">
#       <div class="ov-stat">
#         <div class="ov-stat-label">Health Index</div>
#         <div class="ov-score-wrap">
#           <svg class="ov-ring" viewBox="0 0 120 120">...</svg>
#         </div>
#       </div>
#     </div>
#     <!-- Health clusters -->
#     <div class="ov-clusters">
#       <div class="ov-cluster" data-status="warning">
#         <div class="ov-cluster-title">[Concern Name]</div>
#         <div class="ov-cluster-body">[Key findings]</div>
#       </div>
#     </div>
#   </div>

# Write default overview rules
rules = {
    "_comment": "Display rules for overview section",
    "overview_markers": [
        {"test_name": "Гемоглобин", "display_name": "Гемоглобин", "category": "Blood", "priority": 1},
        {"test_name": "Глюкоза", "display_name": "Глюкоза", "category": "Metabolism", "priority": 2},
        {"test_name": "ТТГ (TSH)", "display_name": "ТТГ", "category": "Hormones", "priority": 3}
    ]
}

with open(RULES_OUT, 'w', encoding='utf-8') as f:
    json.dump(rules, f, ensure_ascii=False, indent=2)

print(f"overview_rules.json written to {RULES_OUT}")
print("TODO: Implement overview HTML generation from your CSV data.")
