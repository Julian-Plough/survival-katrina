# 01_assemble.py
# Module 1: Data Assembly
#
# STATA EQUIVALENT: data_setup_2_22.do / Causal_Data_Setup.do
# (note: two nearly identical files existed, data_setup_2_22.do
#  is assumed to be the final version - verify modification dates
#  on drive if needed)
#
# WHAT THIS DOES:
# Replicates the data merging steps from the Stata pipeline:
# 1. Loads the core parcel-tenure dataset (causal_dataset.dta)
#    which was built by the Stata do files from raw OPLR sales data
#    and HMDA matched loan records
# 2. Merges in FEMA flood zone and census tract IDs (tract_spatial.dta)
# 3. Merges in tract-level demographics from 1990, 2000, 2010 census
# 4. Merges in homeowner-specific race data from 2000 and 2010 census
# 5. Merges in CPI inflation adjustment factors
#
# OUTPUT: data/processed/assembled.parquet
#         (parquet is faster and smaller than csv for large dataframes)
#
# NOTE: causal_dataset.dta itself was built upstream by:
#       - data_setup_2_22.do (OPLR sales -> HOT construction)
#       - Untitled_3.do (HMDA LAR append and match quality filter)
#       - session_scrape.py (Orleans Parish web scraper)
#       - LAR_Reader.py / 2007_2014_LAR.py (HMDA LAR parsing)
#       That upstream pipeline is documented in docs/data_sources.md
#
# TODO: the upstream Stata pipeline (data_setup_2_22.do etc.) should
#       eventually be fully translated to Python for complete
#       reproducibility. Low priority for current submission.
#       Target files to translate:
#       - data_setup_2_22.do
#       - Causal_Data_Setup.do
#       - Untitled_3.do
#       - census_format.do
#       - hmdamatch (currently documented via Bayer et al. method)

import pandas as pd
import pyreadstat
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from config import *

def load_dta(path):
    """Load a Stata .dta file into a pandas DataFrame."""
    df, meta = pyreadstat.read_dta(str(path))
    return df

def main():
    print("=" * 50)
    print("MODULE 1: DATA ASSEMBLY")
    print("=" * 50)

    # ── Step 1: Core dataset ──────────────────────────────
    print("\n[1/5] Loading causal_dataset...")
    df = load_dta(CAUSAL_DATASET)
    print(f"      {len(df):,} records, {df.shape[1]} columns")
    print(f"      Columns: {list(df.columns)}")

    # ── Step 2: FEMA zones and census tract IDs ───────────
    print("\n[2/5] Merging tract spatial data (FEMA zones, tract IDs)...")
    spatial = load_dta(TRACT_SPATIAL)
    n_before = len(df)
    df = df.merge(spatial, on="geopin", how="inner")
    print(f"      {n_before:,} -> {len(df):,} records after inner merge")
    # resolve column name collisions from spatial merge
    # causal_dataset already has tract IDs and hand/acres
    # tract_spatial brings fld_zone and zone_subty (the new things we need)
    # drop the _y duplicates, rename _x back to originals
    df = df.drop(columns=['acres_y', 'hand_y', 'tract_2000_y', 
                           'tract_2010_y', 'tract_1990_y'])
    df = df.rename(columns={
        'acres_x': 'acres',
        'hand_x': 'hand',
        'tract_1990_x': 'tract_1990',
        'tract_2000_x': 'tract_2000',
        'tract_2010_x': 'tract_2010'
    })
    print(f"      Columns after spatial merge: {list(df.columns)}")

    # ── Step 3: Census tract demographics ─────────────────
    print("\n[3/5] Merging census tract demographics...")
    c1990 = load_dta(CENSUS_1990)
    c2000 = load_dta(CENSUS_2000)
    c2010 = load_dta(CENSUS_2010)
    df = df.merge(c1990, on="tract_1990", how="left")
    df = df.merge(c2000, on="tract_2000", how="left")
    df = df.merge(c2010, on="tract_2010", how="left")
    print(f"      {len(df):,} records after census merge")

    # ── Step 4: Homeowner race data ───────────────────────
    print("\n[4/5] Merging homeowner census data...")
    ho2000 = load_dta(CENSUS_HO_2000)
    ho2010 = load_dta(CENSUS_HO_2010)
    df = df.merge(ho2000, on="tract_2000", how="left")
    df = df.merge(ho2010, on="tract_2010", how="left")
    print(f"      {len(df):,} records after homeowner merge")

    print(df[['move_in', 'move_out', 'purchase_price', 'sale_price', 'l_date', 'applicant_income']].describe())
    # ── Step 5: Inflation adjustment ──────────────────────
    print("\n[5/5] Inflation adjustment...")
    # TODO: properly implement inflation adjustment in Module 2
    # need to verify price columns and date formats first
    # inflation_6_21.dta loaded but merge deferred
    infl = load_dta(INFLATION)
    print(f"      Inflation file loaded, merge deferred to Module 2")

    # ── Save ──────────────────────────────────────────────
    print("\nSaving assembled dataset...")
    out = Path(PROCESSED_DIR) / "assembled.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"      Saved to {out}")
    print(f"      Final shape: {df.shape}")
    print("\nModule 1 complete.")

if __name__ == "__main__":
    main()
