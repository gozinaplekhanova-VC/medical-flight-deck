#!/usr/bin/env python3
"""Restructure sec-hormones → Endocrinology tab. Also update CSV files.

This script replaces the hormones section in index.html with a structured
view of endocrine data organized by groups:
  - Thyroid (TSH, FT3, FT4)
  - Autoimmune screening (Anti-TPO, Anti-TG)
  - Reproductive hormones (LH, FSH, Estradiol, Progesterone, AMH)
  - Androgens (Testosterone, DHEA-S)
  - Adrenal (Cortisol, Leptin)
  - Metabolic (HbA1c, Insulin, HOMA-IR)
  - Growth (IGF-1)
  - Parathyroid (PTH, Ca, P)
  - GI hormones (Gastrin)

TODO: Replace the placeholder HTML below with your actual hormone data.
Read data from 02_TABLES/hormones.csv and build the HTML dynamically,
or hardcode your results following the structure shown below.
"""

import re, os

INDEX = './/05_SITE/index.html'
HORMONES_CSV = './/02_TABLES/hormones.csv'

with open(INDEX, 'r', encoding='utf-8') as f:
    html = f.read()

# The script finds the sec-hormones section and replaces it with structured content.
# Structure: each hormone group is a <details> element with data-bg-group attribute.
#
# Example group structure:
#
#   <details class="bg-group" open data-bg-group="horm-thyroid">
#     <summary class="bg-group-sum">
#       <span class="bg-group-label">Thyroid</span>
#       <span class="bg-group-arrow">▾</span>
#     </summary>
#     <div class="tbl-wrap lab-tbl-wrap"><table>
#     <thead><tr>
#       <th style="width:24px"></th><th>Marker</th><th>Unit</th><th>Range</th>
#       <th>[Date 1]</th><th>[Date 2]</th>
#     </tr></thead><tbody>
#     <tr data-prio="1">
#       <td class="prio-cell"><span class="prio-dot p1"></span></td>
#       <td class="test-name"><span class="tip" data-tip="[tooltip]">[Test Name]</span></td>
#       <td class="unit">[unit]</td><td class="norm">[range]</td>
#       <td><span class="badge badge-ok">[value]</span></td>
#       <td><span class="badge badge-high">[value]</span></td>
#     </tr>
#     </tbody></table></div>
#   </details>
#
# Badge classes: badge-ok (normal), badge-low (below range), badge-high (above range)
# Priority dots: p1 (critical), p2 (important), p3 (monitor)

print("TODO: Implement with your hormone data from hormones.csv")
print("See script comments for expected HTML structure.")
