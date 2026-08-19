# 02_features.py
# Module 2: Feature Engineering
#
# STATA EQUIVALENT: survival_analysis_22.do (variable construction section)
#
# WHAT THIS DOES:
# Reads assembled.parquet and constructs all analysis-ready variables:
# 1. moved_out       - event indicator (1 = sale observed, 0 = censored)
# 2. duration        - length of homeownership tenure in days
# 3. katrina_tenure  - 1 if HOT overlapped with Hurricane Katrina (Aug 29 2005)
# 4. fema_category   - 0=outside, 100=100yr zone, 500=500yr zone
# 5. black_white_other - individual race from HMDA (0=other, 1=white, 2=Black)
# 6. income_adjusted - HMDA applicant income * CPI adjustment, in $000s
# 7. census_income   - tract-level median income, time-varying, 2021 dollars
# 8. census_percent_black_ho - tract-level Black homeowner share, time-varying
# 9. census_black_categories_ho - categorical version of above (0-3)
#
# KNOWN ISSUES / TODO:
# - SCRAPE_END date (22281 = Jan 1 2021) should be verified against
#   actual OPLR scrape date
# - 90-day minimum duration trim follows housing tenure literature convention
#   explicit citation needed before final submission
# - census inflation factors (1990*2.09, 2000*1.58, 2010*1.25) are hardcoded
#   from original Stata pipeline, source is BLS CPI-U
#   update to 2026 dollars before final submission
# - HMDA race coverage: 41,382 / 301,457 HOTs have usable race data
#   census tract variables serve as robustness check for full sample
# - HMDA income coverage: 22,111 / 301,457 HOTs have usable income data
# - black_white_other None values represent no HMDA match or race not reported
#   255,634 no match, 4,436 missing/not provided, 5 not applicable
#
# OUTPUT: data/processed/analysis_ready.parquet

import pandas as pd
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from config import *

def main():

    df = pd.read_parquet(Path(PROCESSED_DIR) / "assembled.parquet")

    # ── 1: Event indicator ────────────────────────────────
    # current tenure = no recorded sale as of data collection (~2020/2021)
    # these are censored observations in survival terms, not truly current
    df['moved_out'] = df['move_out'].notna().astype(int)

    # ── 2: Duration ───────────────────────────────────────
    # SCRAPE_END = Jan 1 2021 in Stata date format (days since Jan 1 1960)
    # TODO: verify against actual OPLR scrape date
    SCRAPE_END = 22281
    df['duration'] = (df['move_out'] - df['move_in']).fillna(SCRAPE_END - df['move_in'])
    df = df[df['duration'] >= 90]  # drop implausibly short tenures
    # TODO: cite explicit source for 90-day minimum duration threshold

    # ── 3: Katrina tenure ─────────────────────────────────
    KATRINA_DATE = 16677  # August 29 2005 in Stata date format
    df['katrina_tenure'] = (
        (df['move_in'] <= KATRINA_DATE) &
        ((df['move_out'] >= KATRINA_DATE) | (df['current_tenure'] == 1))
    ).astype(int)

    # ── 4: FEMA category ──────────────────────────────────
    # TODO: FEMA map vintage not documented -- has implications for
    # pre/post remapping exposure classification
    # TODO: redo spatial join at block group level
    df['fema_category'] = 0
    df.loc[df['fld_zone'].isin(['A', 'AE', 'AO', 'VE']), 'fema_category'] = 100
    df.loc[(df['fld_zone'] == 'X') & 
           (df['zone_subty'] == '0.2 PCT ANNUAL CHANCE FLOOD HAZARD'), 
           'fema_category'] = 500

    # ── 5: Individual race from HMDA ──────────────────────
    # 0=other, 1=white, 2=Black
    # None = no HMDA match or race not reported
    df['black_white_other'] = None
    mask = (
        df['applicant_race_1'].notna() &
        ~df['applicant_race_1'].isin(['', 'Missing',
            'Information not provided by applicant in mail, Internet, or telephone application',
            'Not applicable'])
    )
    df.loc[mask & ~df['applicant_race_1'].isin(
        ['White', 'Black', 'Black or African American']), 'black_white_other'] = 0
    df.loc[mask & (df['applicant_race_1'] == 'White'), 'black_white_other'] = 1
    df.loc[mask & df['applicant_race_1'].isin(
        ['Black', 'Black or African American']), 'black_white_other'] = 2

    # ── 6: Income adjusted ────────────────────────────────
    # HMDA income reported in $000s, multiplied by CPI factor
    # trim flag applied at model stage for HMDA subsample only
    df['income_adjusted'] = pd.to_numeric(
        df['applicant_income'], errors='coerce') * df['inflation_6_21']
    p1 = df['income_adjusted'].quantile(0.01)
    p99 = df['income_adjusted'].quantile(0.99)
    df['income_trim_flag'] = (
        ~df['income_adjusted'].between(p1, p99)) & df['income_adjusted'].notna()

    # ── 7 & 8: Time-varying census variables ──────────────
    # assign most recent census available at time of move-out
    # inflation factors: BLS CPI-U, hardcoded from original Stata pipeline
    # TODO: update to 2026 dollars before final submission
    df['move_out_year'] = pd.to_datetime(
        df['move_out'], unit='D', origin='1960-01-01').dt.year
    df['move_in_year'] = pd.to_datetime(
        df['move_in'], unit='D', origin='1960-01-01').dt.year

    df['census_income'] = pd.NA
    df['census_percent_black_ho'] = pd.NA

    df.loc[(df['move_out_year'] >= 1985) & (df['move_out_year'] < 1995),
           'census_income'] = df['income_tract_1990'] * 2.09
    df.loc[(df['move_out_year'] >= 1995) & (df['move_out_year'] < 2005),
           'census_income'] = df['income_tract_2000'] * 1.58
    df.loc[(df['move_out_year'] >= 2005) & (df['move_out_year'] <= 2015),
           'census_income'] = df['income_tract_2010'] * 1.25
    df.loc[(df['move_in_year'] <= 2015) & (df['moved_out'] == 0),
           'census_income'] = df['income_tract_2010'] * 1.25

    df.loc[(df['move_out_year'] >= 1995) & (df['move_out_year'] < 2005),
           'census_percent_black_ho'] = df['percent_black_2000_homeowner']
    df.loc[(df['move_out_year'] >= 2005) & (df['move_out_year'] <= 2015),
           'census_percent_black_ho'] = df['percent_black_2010_homeowner']
    df.loc[(df['move_in_year'] <= 2015) & (df['moved_out'] == 0),
           'census_percent_black_ho'] = df['percent_black_2010_homeowner']

    df['census_income'] = pd.to_numeric(df['census_income'], errors='coerce')
    df['census_percent_black_ho'] = pd.to_numeric(
        df['census_percent_black_ho'], errors='coerce')

    # ── 9: Census black categories ────────────────────────
    df['census_black_categories_ho'] = 0
    df.loc[df['census_percent_black_ho'] > 0.25, 'census_black_categories_ho'] = 1
    df.loc[df['census_percent_black_ho'] > 0.50, 'census_black_categories_ho'] = 2
    df.loc[df['census_percent_black_ho'] > 0.75, 'census_black_categories_ho'] = 3

    # ── Save ──────────────────────────────────────────────
    out = Path(PROCESSED_DIR) / "analysis_ready.parquet"
    df.to_parquet(out, index=False)

if __name__ == "__main__":
    main()