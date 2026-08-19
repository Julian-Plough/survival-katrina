# 01_assemble.py
# Module 1: Data Assembly
#
# STATA EQUIVALENT: data_setup_2_22.do / Causal_Data_Setup.do
# (note: two nearly identical files existed, data_setup_2_22.do
#  is assumed to be the final version - verify modification dates
#  on drive if needed)
#
# WHAT THIS DOES:
# 1. Loads core parcel-tenure dataset (causal_dataset.dta)
# 2. Merges tract spatial data (FEMA zones, tract IDs) on geopin
#    - drops overlapping columns from causal before merging
# 3. Forces tract IDs to Int64
# 4. Merges census tract demographics (1990, 2000, 2010)
# 5. Merges homeowner race data (2000, 2010)
# 6. Inflation adjusts sale_price using move_in date, rounded to nearest $100
# 7. Saves assembled dataset to data/processed/assembled.parquet
#
# KNOWN ISSUES / TODO:
# - sale_price vs purchase_price distinction not fully understood
#   not all HOTs have a sale_price -- possible explanations: inherited
#   properties, tax sales, data gaps in OPLR scrape, or current tenures
#   needs investigation when upstream pipeline is redone
# - inflation adjustment uses move_in date as the price date
#   should be verified against original Stata code
# - inflation file adjusts to 2021 dollars (BLS CPI-U)
#   update to 2026 dollars before final submission
# - entire upstream pipeline needs to be redone from raw data products:
#   * spatial join should be redone at block group level (not tract)
#   * FEMA flood plain map vintage needs to be identified and documented
#     (has implications for pre/post remapping exposure classification)
#   * HMDA matching, census formatting, HOT construction all need
#     clean Python translations
#   * web scraper (session_scrape.py) does NOT need to be rerun
#     raw scraped data products are preserved
#
# NOTE: causal_dataset.dta was built upstream by:
#       - data_setup_2_22.do (OPLR sales -> HOT construction)
#       - Untitled_3.do (HMDA LAR append and match quality filter)
#       - session_scrape.py (Orleans Parish web scraper)
#       - LAR_Reader.py / 2007_2014_LAR.py (HMDA LAR parsing)
#       That upstream pipeline is documented in docs/data_sources.md

import pandas as pd
import pyreadstat
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from config import *

def load_dta(path):
    """Load a Stata .dta file into a pandas DataFrame."""
    df, _ = pyreadstat.read_dta(str(path))
    return df

def main():

    # ── Step 1: Core dataset ──────────────────────────────
    causal = load_dta(CAUSAL_DATASET)

    # ── Step 2: Spatial merge on geopin ───────────────────
    spatial = load_dta(TRACT_SPATIAL)
    cols_to_drop = [c for c in causal.columns if c in spatial.columns and c != 'geopin']
    causal = causal.drop(columns=cols_to_drop)
    df = causal.merge(spatial, on='geopin', how='inner')

    # ── Step 3: Force tract IDs to Int64 ──────────────────
    for col in ['tract_1990', 'tract_2000', 'tract_2010']:
        df[col] = df[col].fillna(-1).astype(int).astype('Int64').replace(-1, pd.NA)

    # ── Step 4: Census and homeowner merges ───────────────
    census_files = [
        (CENSUS_1990,    'tract_1990'),
        (CENSUS_2000,    'tract_2000'),
        (CENSUS_2010,    'tract_2010'),
        (CENSUS_HO_2000, 'tract_2000'),
        (CENSUS_HO_2010, 'tract_2010'),
    ]
    for path, key in census_files:
        data = load_dta(path)
        data[key] = data[key].fillna(-1).astype(int).astype('Int64').replace(-1, pd.NA)
        df = df.merge(data, on=key, how='left')

    # ── Step 5: Inflation adjustment ──────────────────────
    # use move_in date (Stata format: days since 1960-01-01)
    # rounded to nearest $100 to reflect precision in raw data
    # TODO: verify move_in is correct date for price adjustment
    # TODO: update inflation to 2026 dollars before final submission
    df['move_in_date'] = pd.to_datetime(df['move_in'], unit='D', origin='1960-01-01')
    df['l_year'] = df['move_in_date'].dt.year.astype('Int64')
    df['l_month'] = df['move_in_date'].dt.month.astype('Int64')

    infl = load_dta(INFLATION)
    infl['l_year'] = infl['l_year'].astype('Int64')
    infl['l_month'] = infl['l_month'].astype('Int64')

    df = df.merge(infl, on=['l_year', 'l_month'], how='left')
    df['sale_price_adj'] = (df['sale_price'] * df['inflation_6_21']).round(-2).fillna(pd.NA).astype('Int64')

    # ── Step 6: Save ──────────────────────────────────────
    out = Path(PROCESSED_DIR) / "assembled.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)

if __name__ == "__main__":
    main()