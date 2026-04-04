#!/usr/bin/env python3
"""Replace sec-meds section based on medications.csv.

Reads medications.csv and generates the medications dashboard section
with current and past medications, organized by status (active/completed).

TODO: Replace placeholder content with your actual medication data.
"""

with open('.//05_SITE/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD_START = '  <div id="sec-meds" class="sec">'
OLD_END   = '\n  <div id="sec-supp" class="sec">'

si = content.find(OLD_START)
ei = content.find(OLD_END)
if si == -1 or ei == -1:
    print(f'ERROR: markers not found (start={si}, end={ei})')
    exit(1)

# TODO: Read from 02_TABLES/medications.csv and generate HTML
# Expected CSV format: date_start;date_end;name;dosage;frequency;reason
#
# Example HTML structure for a medication card:
#
#   <div class="med-card">
#     <div class="med-header">
#       <span class="med-name">[Medication Name]</span>
#       <span class="med-dose">[Dosage] · [Frequency]</span>
#     </div>
#     <div class="med-dates">[Start Date] – [End Date or "настоящее время"]</div>
#     <div class="med-reason">[Reason for use]</div>
#   </div>

print("TODO: Implement with your medication data from medications.csv")
