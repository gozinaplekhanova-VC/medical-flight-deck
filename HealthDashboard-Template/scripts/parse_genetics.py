#!/usr/bin/env python3
"""
Parse genetics_raw.vcf and extract clinically significant SNPs into category CSVs.

Sources: ClinVar, PharmGKB, published GWAS/clinical literature.

Output files (02_TABLES/):
  genetics_metabolism.csv     — drug metabolism, caffeine, alcohol, lactose, folate
  genetics_cardiovascular.csv — CVD risk, lipids, thrombosis
  genetics_gut.csv            — celiac, lactose, gut inflammation, MTHFR
  genetics_nutrients.csv      — vitamin D, B12, iron, omega-3
"""

import csv
import gzip
import os
import re

VCF_PATH   = './/02_TABLES/genetics_raw.vcf'
OUT_DIR    = './/02_TABLES'

# ---------------------------------------------------------------------------
# rsID catalogue
# Each entry: rsid → { category, gene, trait, ref_allele, alt_allele,
#                       risk_allele, effect, source }
# risk_allele: the allele associated with the described effect (REF or ALT)
# ---------------------------------------------------------------------------

CATALOGUE = {
    # ── METABOLISM ──────────────────────────────────────────────────────────
    'rs762551':   dict(category='metabolism', gene='CYP1A2',      trait='Caffeine metabolism',
                       risk_allele='A', effect='Fast metaboliser (AA) / Slow (AC/CC)', source='PharmGKB'),
    'rs2472297':  dict(category='metabolism', gene='CYP1A2',      trait='Caffeine habitual intake',
                       risk_allele='T', effect='Higher caffeine consumption', source='GWAS'),
    'rs4880':     dict(category='metabolism', gene='SOD2',        trait='Oxidative stress / antioxidant',
                       risk_allele='G', effect='Reduced mitochondrial SOD2 activity', source='ClinVar'),
    'rs1801133':  dict(category='metabolism', gene='MTHFR',       trait='Folate metabolism (C677T)',
                       risk_allele='A', effect='Reduced MTHFR enzyme activity; elevated homocysteine', source='ClinVar'),
    'rs1801131':  dict(category='metabolism', gene='MTHFR',       trait='Folate metabolism (A1298C)',
                       risk_allele='G', effect='Mild MTHFR reduction; compound het with C677T is significant', source='ClinVar'),
    'rs1799853':  dict(category='metabolism', gene='CYP2C9',      trait='Drug metabolism (warfarin, NSAIDs)',
                       risk_allele='T', effect='*2 allele — reduced CYP2C9 activity', source='PharmGKB'),
    'rs1057910':  dict(category='metabolism', gene='CYP2C9',      trait='Drug metabolism (warfarin, NSAIDs)',
                       risk_allele='C', effect='*3 allele — significantly reduced CYP2C9 activity', source='PharmGKB'),
    'rs3892097':  dict(category='metabolism', gene='CYP2D6',      trait='Drug metabolism (antidepressants, opioids)',
                       risk_allele='A', effect='*4 allele — poor metaboliser', source='PharmGKB'),
    'rs5030655':  dict(category='metabolism', gene='CYP2D6',      trait='Drug metabolism',
                       risk_allele='A', effect='*6 allele — poor metaboliser (frameshift)', source='PharmGKB'),
    'rs4244285':  dict(category='metabolism', gene='CYP2C19',     trait='Drug metabolism (PPIs, clopidogrel, SSRIs)',
                       risk_allele='A', effect='*2 allele — poor metaboliser', source='PharmGKB'),
    'rs4986893':  dict(category='metabolism', gene='CYP2C19',     trait='Drug metabolism',
                       risk_allele='A', effect='*3 allele — poor metaboliser', source='PharmGKB'),
    'rs12248560': dict(category='metabolism', gene='CYP2C19',     trait='Drug metabolism',
                       risk_allele='T', effect='*17 allele — ultra-rapid metaboliser', source='PharmGKB'),
    'rs1045642':  dict(category='metabolism', gene='ABCB1',       trait='Drug transport / bioavailability',
                       risk_allele='T', effect='Reduced P-glycoprotein activity; altered drug CNS entry', source='PharmGKB'),
    'rs228697':   dict(category='metabolism', gene='CYP3A5',      trait='Drug metabolism (tacrolimus, statins)',
                       risk_allele='T', effect='*3 allele — poor expresser', source='PharmGKB'),
    'rs1799945':  dict(category='metabolism', gene='HFE',         trait='Iron metabolism (H63D)',
                       risk_allele='G', effect='Mild haemochromatosis risk; elevated iron absorption', source='ClinVar'),
    'rs1800562':  dict(category='metabolism', gene='HFE',         trait='Iron metabolism (C282Y)',
                       risk_allele='A', effect='Main haemochromatosis mutation; high iron overload risk if homozygous', source='ClinVar'),
    'rs4680':     dict(category='metabolism', gene='COMT',        trait='Dopamine / catecholamine metabolism',
                       risk_allele='A', effect='Val158Met — slow COMT; higher dopamine, pain sensitivity', source='ClinVar'),
    'rs1800497':  dict(category='metabolism', gene='ANKK1/DRD2',  trait='Dopamine receptor / reward',
                       risk_allele='T', effect='Taq1A — reduced D2 density; addiction / impulsivity risk', source='ClinVar'),
    'rs698':      dict(category='metabolism', gene='ADH1C',       trait='Alcohol metabolism',
                       risk_allele='A', effect='Slow alcohol metabolism (Ile349Val)', source='PharmGKB'),
    'rs1229984':  dict(category='metabolism', gene='ADH1B',       trait='Alcohol metabolism',
                       risk_allele='C', effect='Fast acetaldehyde build-up; flushing reaction', source='PharmGKB'),
    'rs671':      dict(category='metabolism', gene='ALDH2',       trait='Alcohol / aldehyde metabolism',
                       risk_allele='A', effect='*2 — deficient ALDH2; toxic aldehyde accumulation', source='ClinVar'),

    # ── CARDIOVASCULAR ──────────────────────────────────────────────────────
    'rs1333049':  dict(category='cardiovascular', gene='CDKN2B-AS1', trait='Coronary artery disease risk',
                       risk_allele='C', effect='Strong CAD GWAS signal', source='ClinVar/GWAS'),
    'rs10757274': dict(category='cardiovascular', gene='CDKN2A/B',   trait='CAD / MI risk',
                       risk_allele='G', effect='CAD risk locus', source='GWAS'),
    'rs6725887':  dict(category='cardiovascular', gene='WDR12',      trait='CAD risk',
                       risk_allele='C', effect='CAD risk allele', source='GWAS'),
    'rs1799963':  dict(category='cardiovascular', gene='F2',         trait='Prothrombin G20210A — thrombosis',
                       risk_allele='A', effect='Elevated prothrombin; VTE / DVT risk', source='ClinVar'),
    'rs6025':     dict(category='cardiovascular', gene='F5',         trait='Factor V Leiden — thrombosis',
                       risk_allele='A', effect='APC resistance; high VTE risk (het ~5×, hom ~80×)', source='ClinVar'),
    'rs1800801':  dict(category='cardiovascular', gene='MTHFR',      trait='Homocysteine / CVD',
                       risk_allele='A', effect='Elevated homocysteine → CVD risk', source='ClinVar'),
    'rs5370':     dict(category='cardiovascular', gene='EDN1',       trait='Endothelin / hypertension',
                       risk_allele='T', effect='Lys198Asn — vascular tone, hypertension risk', source='ClinVar'),
    'rs1799752':  dict(category='cardiovascular', gene='ACE',        trait='ACE insertion/deletion — hypertension',
                       risk_allele='C', effect='D allele — higher ACE activity; hypertension', source='ClinVar'),
    'rs4149056':  dict(category='cardiovascular', gene='SLCO1B1',    trait='Statin myopathy risk',
                       risk_allele='C', effect='*5 allele — reduced OATP1B1; simvastatin myopathy risk', source='PharmGKB/ClinVar'),
    'rs2228671':  dict(category='cardiovascular', gene='LDLR',       trait='LDL receptor / familial hypercholesterolaemia',
                       risk_allele='T', effect='Possible reduced LDL-R activity', source='ClinVar'),
    'rs3135506':  dict(category='cardiovascular', gene='APOA5',      trait='Triglycerides',
                       risk_allele='C', effect='Ser19Trp — elevated TG risk', source='ClinVar'),
    'rs662799':   dict(category='cardiovascular', gene='APOA5',      trait='Triglycerides',
                       risk_allele='G', effect='Elevated TG, lower HDL', source='GWAS'),
    'rs1800777':  dict(category='cardiovascular', gene='CETP',       trait='HDL cholesterol',
                       risk_allele='A', effect='Lower CETP activity; higher HDL', source='GWAS'),
    'rs708272':   dict(category='cardiovascular', gene='CETP',       trait='HDL cholesterol',
                       risk_allele='A', effect='Taq1B — higher HDL', source='GWAS'),

    # ── GUT ─────────────────────────────────────────────────────────────────
    'rs2187668':  dict(category='gut', gene='HLA-DQA1',  trait='Coeliac disease / gluten sensitivity',
                       risk_allele='C', effect='DQ2.5 haplotype — strongest coeliac risk', source='ClinVar'),
    'rs7454108':  dict(category='gut', gene='HLA-DQB1',  trait='Coeliac disease',
                       risk_allele='C', effect='DQ2.2 component — coeliac risk', source='ClinVar'),
    'rs4713586':  dict(category='gut', gene='HLA-DQA1',  trait='Coeliac / DQ8 haplotype',
                       risk_allele='A', effect='DQ8 allele — second major coeliac haplotype', source='ClinVar'),
    'rs4988235':  dict(category='gut', gene='MCM6/LCT',  trait='Lactase persistence / lactose intolerance',
                       risk_allele='G', effect='G = lactase non-persistence (intolerance); A = persistence', source='ClinVar'),
    'rs182549':   dict(category='gut', gene='MCM6/LCT',  trait='Lactase persistence',
                       risk_allele='C', effect='C = non-persistence (intolerance)', source='ClinVar'),
    'rs1800925':  dict(category='gut', gene='IL13',      trait='Gut inflammation / IBS / IBD risk',
                       risk_allele='T', effect='Elevated IL-13 signalling', source='ClinVar'),
    'rs3024505':  dict(category='gut', gene='IL10',      trait='IBD / gut inflammation',
                       risk_allele='C', effect='Lower IL-10 → reduced anti-inflammatory response', source='ClinVar'),
    'rs2241880':  dict(category='gut', gene='ATG16L1',   trait="Crohn's disease risk",
                       risk_allele='G', effect='Thr300Ala — autophagy impairment; Crohn risk', source='ClinVar'),
    'rs17221417': dict(category='gut', gene='PTPN22',    trait='IBD / autoimmune',
                       risk_allele='T', effect='Autoimmune risk allele', source='ClinVar'),
    # MTHFR repeated in gut for completeness
    'rs1801133_gut': dict(category='gut', gene='MTHFR',  trait='Folate/homocysteine — gut mucosa',
                       risk_allele='A', effect='Reduced methylation capacity; mucosal inflammation risk', source='ClinVar'),

    # ── NUTRIENTS ────────────────────────────────────────────────────────────
    'rs2282679':  dict(category='nutrients', gene='GC',        trait='Vitamin D binding protein',
                       risk_allele='A', effect='Lower 25-OH-D levels', source='ClinVar/GWAS'),
    'rs7041':     dict(category='nutrients', gene='GC',        trait='Vitamin D binding protein',
                       risk_allele='T', effect='Reduced vitamin D transport efficiency', source='ClinVar'),
    'rs10741657': dict(category='nutrients', gene='CYP2R1',    trait='Vitamin D 25-hydroxylation',
                       risk_allele='A', effect='Lower 25-OH-D synthesis', source='GWAS'),
    'rs12785878': dict(category='nutrients', gene='DHCR7/NADSYN1', trait='Vitamin D synthesis',
                       risk_allele='T', effect='Lower vitamin D status', source='GWAS'),
    'rs1544410':  dict(category='nutrients', gene='VDR',       trait='Vitamin D receptor (BsmI)',
                       risk_allele='T', effect='Reduced VDR function; lower calcium absorption', source='ClinVar'),
    'rs731236':   dict(category='nutrients', gene='VDR',       trait='Vitamin D receptor (TaqI)',
                       risk_allele='C', effect='VDR variant affecting vitamin D signalling', source='ClinVar'),
    'rs2060793':  dict(category='nutrients', gene='CYP24A1',   trait='Vitamin D catabolism',
                       risk_allele='G', effect='Higher 25-OH-D degradation', source='GWAS'),
    'rs602662':   dict(category='nutrients', gene='FUT2',      trait='Vitamin B12 absorption',
                       risk_allele='A', effect='Non-secretor — lower B12; altered gut microbiome', source='ClinVar'),
    'rs492602':   dict(category='nutrients', gene='FUT2',      trait='Vitamin B12 / gut microbiome',
                       risk_allele='G', effect='Non-secretor haplotype', source='ClinVar'),
    'rs1801198':  dict(category='nutrients', gene='TCN2',      trait='Vitamin B12 transport (transcobalamin II)',
                       risk_allele='A', effect='Pro259Arg — reduced B12 cellular delivery', source='ClinVar'),
    'rs1051266':  dict(category='nutrients', gene='SLC19A1',   trait='Folate transport (RFC1)',
                       risk_allele='A', effect='Reduced folate uptake', source='ClinVar'),
    'rs174537':   dict(category='nutrients', gene='FADS1',     trait='Omega-3/6 fatty acid conversion',
                       risk_allele='G', effect='Higher FADS1 activity; higher AA, lower EPA/DHA from ALA', source='GWAS'),
    'rs1535':     dict(category='nutrients', gene='FADS2',     trait='Omega-3/6 fatty acid conversion',
                       risk_allele='A', effect='Reduced FADS2; lower long-chain PUFA synthesis', source='GWAS'),
    'rs174575':   dict(category='nutrients', gene='FADS2',     trait='Omega-3/6 desaturation',
                       risk_allele='G', effect='Reduced EPA/DHA conversion efficiency', source='GWAS'),
    'rs738409':   dict(category='nutrients', gene='PNPLA3',    trait='Liver fat / iron storage',
                       risk_allele='G', effect='Ile148Met — NAFLD risk; altered hepatic iron', source='ClinVar'),
    'rs4291':     dict(category='nutrients', gene='ACE',       trait='Iron absorption (indirect)',
                       risk_allele='A', effect='ACE variant affecting nutrient homeostasis', source='ClinVar'),
    'rs1049296':  dict(category='nutrients', gene='TF',        trait='Transferrin (iron transport)',
                       risk_allele='C', effect='Pro570Ser — altered iron-binding; anaemia risk', source='ClinVar'),
    'rs855791':   dict(category='nutrients', gene='TMPRSS6',   trait='Hepcidin regulation / iron',
                       risk_allele='A', effect='Val736Ala — lower hepcidin suppression; iron-deficiency anaemia risk', source='ClinVar/GWAS'),
}

# Deduplicate entries with suffix workarounds (e.g. rs1801133_gut)
def canonical_rsid(key):
    return key.split('_')[0]

# Build rsid → list of entries (one rsid can appear in multiple categories)
from collections import defaultdict
rsid_to_entries = defaultdict(list)
for key, meta in CATALOGUE.items():
    rsid_to_entries[canonical_rsid(key)].append(dict(rsid=canonical_rsid(key), **meta))

# ---------------------------------------------------------------------------
# Parse VCF
# ---------------------------------------------------------------------------

def parse_vcf(path):
    """Yield (rsid, chrom, pos, ref, alt, genotype_str) for rs* entries."""
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt', encoding='utf-8', errors='replace') as fh:
        sample_col = None
        format_col = None
        for line in fh:
            if line.startswith('##'):
                continue
            if line.startswith('#CHROM'):
                cols = line.lstrip('#').rstrip('\n').split('\t')
                if 'FORMAT' in cols:
                    format_col = cols.index('FORMAT')
                    # First sample column is right after FORMAT
                    if len(cols) > format_col + 1:
                        sample_col = format_col + 1
                continue
            fields = line.rstrip('\n').split('\t')
            if len(fields) < 5:
                continue
            chrom, pos, rsid_field, ref, alt = fields[0], fields[1], fields[2], fields[3], fields[4]
            # Extract rsID(s) — field may contain multiple IDs separated by ';'
            ids = [x for x in rsid_field.split(';') if x.startswith('rs')]
            if not ids:
                continue
            rsid = ids[0]  # take first rsID

            # Genotype
            genotype_str = '.'
            if sample_col is not None and len(fields) > sample_col and format_col is not None:
                fmt = fields[format_col].split(':')
                smp = fields[sample_col].split(':')
                if 'GT' in fmt:
                    gt_idx = fmt.index('GT')
                    if gt_idx < len(smp):
                        genotype_str = smp[gt_idx]

            yield rsid, chrom, pos, ref, alt, genotype_str


def decode_genotype(ref, alt, gt_str):
    """Convert GT string (e.g. '0/1', '1|1') to nucleotide pair."""
    alleles_raw = alt.split(',')
    allele_map = {str(i): a for i, a in enumerate([ref] + alleles_raw)}
    sep = '|' if '|' in gt_str else '/'
    parts = gt_str.replace('|', '/').split('/')
    if len(parts) != 2:
        return None, None
    a1 = allele_map.get(parts[0], '?')
    a2 = allele_map.get(parts[1], '?')
    return a1, a2


def risk_status(a1, a2, risk_allele):
    """Return 'homozygous_risk', 'heterozygous', 'homozygous_ref', or 'unknown'."""
    if a1 is None or a2 is None or '?' in (a1, a2):
        return 'unknown'
    count = sum(1 for a in (a1, a2) if a == risk_allele)
    if count == 2:
        return 'homozygous_risk'
    if count == 1:
        return 'heterozygous'
    return 'homozygous_ref'


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    categories = ['metabolism', 'cardiovascular', 'gut', 'nutrients']
    fieldnames = ['rsid', 'gene', 'trait', 'chrom', 'pos', 'ref', 'alt',
                  'genotype', 'allele1', 'allele2', 'risk_allele',
                  'risk_status', 'effect', 'source']

    # Prepare output writers
    writers = {}
    handles = {}
    for cat in categories:
        out_path = os.path.join(OUT_DIR, f'genetics_{cat}.csv')
        fh = open(out_path, 'w', newline='', encoding='utf-8')
        w  = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        writers[cat] = w
        handles[cat] = fh

    found    = defaultdict(set)   # cat → set of rsids written
    hit_meta = {}                 # rsid → (chrom, pos, ref, alt, genotype_str)

    print(f'Scanning {VCF_PATH} …')
    n_lines = 0
    for rsid, chrom, pos, ref, alt, gt_str in parse_vcf(VCF_PATH):
        n_lines += 1
        if rsid in rsid_to_entries:
            hit_meta[rsid] = (chrom, pos, ref, alt, gt_str)

    print(f'Processed {n_lines:,} variant lines. Catalogue hits: {len(hit_meta)}')

    for rsid, entries in rsid_to_entries.items():
        meta_tuple = hit_meta.get(rsid)
        for entry in entries:
            cat = entry['category']
            if rsid in found[cat]:
                continue
            found[cat].add(rsid)

            row = dict(rsid=rsid, gene=entry['gene'], trait=entry['trait'],
                       risk_allele=entry['risk_allele'], effect=entry['effect'],
                       source=entry['source'],
                       chrom='', pos='', ref='', alt='',
                       genotype='not_found', allele1='', allele2='',
                       risk_status='not_found')

            if meta_tuple:
                chrom, pos, ref, alt, gt_str = meta_tuple
                a1, a2 = decode_genotype(ref, alt, gt_str)
                row.update(chrom=chrom, pos=pos, ref=ref, alt=alt,
                            genotype=gt_str, allele1=a1 or '', allele2=a2 or '',
                            risk_status=risk_status(a1, a2, entry['risk_allele']))

            writers[cat].writerow(row)

    for cat in categories:
        handles[cat].close()
        n = len(found[cat])
        out_path = os.path.join(OUT_DIR, f'genetics_{cat}.csv')
        print(f'  {out_path}  ({n} SNPs written, {len(rsid_to_entries) - n} not found in VCF)')

    print('Done.')


if __name__ == '__main__':
    main()
