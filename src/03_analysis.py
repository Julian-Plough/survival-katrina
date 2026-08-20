# 03_models.py
# Module 3: Survival Analysis Models and Figures
#
# STATA EQUIVALENT: survival_analysis_22.do, Survival_Census.do, summary_stats.do
#
# WHAT THIS DOES:
# 1. Kaplan-Meier curves -- nonparametric, descriptive
#    - Sample breakdown panel (full, HMDA race, HMDA income subsamples)
#    - By race x katrina_tenure (3 panels)
#    - By income quartile x katrina_tenure (3 panels)
# 2. Distribution comparison figure (appendix)
#    - KM empirical vs Weibull, log-logistic, exponential
#    - AIC/BIC in legend
#    - Log-logistic wins AIC/BIC, Weibull wins visual fit overall
#    - TODO: discuss with advisor whether to switch preferred model
# 3. Cox PH model -- robustness check, HMDA race subsample
# 4. Weibull AFT -- preferred model, HMDA race subsample
# 5. Weibull AFT -- HMDA income subsample (TODO: tomorrow)
# 6. Weibull AFT -- census subsample, robustness (TODO: tomorrow)
# 7. Scenario estimates figure -- main result (TODO: tomorrow)
# 8. Save all figures and tables to outputs/ (TODO: tomorrow)
#
# KEY FINDINGS SO FAR:
# - KM curves: differential separation between Black and white HOTs
#   appears only in Katrina-overlapping tenures, not pre-Katrina
#   same pattern holds for income subsample
#   this is the central visual motivation for the regression
# - Cox: katrina_tenure HR=0.27, massive suppression of sales post-Katrina
#   black_x_katrina adds significant additional suppression for Black HOTs
# - Weibull AFT: katrina_tenure TR=3.08, Katrina HOTs took 3x longer to sell
#   black_x_katrina TR=1.20, Black HOTs took additional 20% longer
#   triple interaction terms (race x fema x katrina) largely insignificant
#   flood zone x race x Katrina story noisier than race x Katrina alone
#
# KNOWN ISSUES / TODO:
# - WeibullAFTFitter does not support cluster_col (frailty) directly
#   robust=True gives heteroskedasticity-robust SEs but is not equivalent
#   to Stata's xtstreg parcel-level random effects
#   true frailty modeling may require lifelines WeibullFitter with frailty
#   parameter or statsmodels survival with frailty
#   TODO: investigate before final submission, discuss with advisor
# - FLAG: verify Cox/Weibull specification matches dissertation methods
#   section, confirm no additional covariates in main spec
# - FLAG: fema dummies introduced in 03, consider moving to 02_features.py
# - ci_show=True on KM curves plots 95% CIs via Greenwood's formula
# - x-axis is duration in days from move-in, not calendar time
#   Katrina line removed -- no meaningful interpretation on duration axis
# - move_in trim at Stata day 0 applied here
#   TODO: move to 02_features.py, evaluate appropriate cutoff
# - sample composition KM panel to move to appendix alongside calibration
#   brief mention in paper of HMDA subsample differences
# - calibration weights (Deville-Sarndal) not yet implemented
#   will need scipy.optimize -- goes to appendix
#
# OUTPUT: outputs/figures/, outputs/tables/

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import (KaplanMeierFitter, CoxPHFitter, WeibullAFTFitter,
                       WeibullFitter, LogLogisticFitter, ExponentialFitter)
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent))
from config import *

KATRINA_DATE = 16677

def km_curves(df_trim):

    income_cuts = [0, 25, 50, 100, 500]
    income_labels = ['$0-25k', '$25-50k', '$50-100k', '$100k+']
    income_colors = ['purple', 'green', 'orange', 'brown']
    df_trim['income_cut'] = pd.cut(df_trim['income_adjusted'],
                                    bins=income_cuts, labels=income_labels)

    fig, axes = plt.subplots(2, 4, figsize=(28, 12))

    # panel 1: sample breakdown
    ax = axes[0, 0]
    for mask, label, color in [
        (df_trim['duration'].notna(), 'All HOTs', 'black'),
        (df_trim['black_white_other'].notna(), 'HMDA race sample', 'green'),
        (df_trim['income_adjusted'].notna() & ~df_trim['income_trim_flag'],
         'HMDA income sample', 'orange'),
    ]:
        n = mask.sum()
        kmf = KaplanMeierFitter()
        kmf.fit(df_trim.loc[mask, 'duration'], df_trim.loc[mask, 'moved_out'],
                label=f'{label} (n={n:,})')
        kmf.plot_survival_function(ax=ax, color=color, ci_show=True)
    ax.set_title('Sample Breakdown')
    ax.set_xlabel('Days')
    ax.set_ylabel('Survival Probability')
    ax.legend(fontsize=8)

    # row 1: race panels
    race_panels = [
        (axes[0, 1], None, 'By Race — Full Sample'),
        (axes[0, 2], 0,    'By Race — Non-Katrina Tenures'),
        (axes[0, 3], 1,    'By Race — Katrina-Overlapping Tenures'),
    ]
    for ax, katrina_val, title in race_panels:
        for race, label, color in [(1, 'White', 'blue'), (2, 'Black', 'red')]:
            if katrina_val is None:
                mask = df_trim['black_white_other'] == race
            else:
                mask = ((df_trim['black_white_other'] == race) &
                        (df_trim['katrina_tenure'] == katrina_val))
            n = mask.sum()
            kmf = KaplanMeierFitter()
            kmf.fit(df_trim.loc[mask, 'duration'], df_trim.loc[mask, 'moved_out'],
                    label=f'{label} (n={n:,})')
            kmf.plot_survival_function(ax=ax, color=color, ci_show=True)
        ax.set_title(title)
        ax.set_xlabel('Days')
        ax.set_ylabel('Survival Probability')
        ax.legend(fontsize=8)

    # row 2: income panels
    income_panels = [
        (axes[1, 1], None, 'By Income — Full Sample'),
        (axes[1, 2], 0,    'By Income — Non-Katrina Tenures'),
        (axes[1, 3], 1,    'By Income — Katrina-Overlapping Tenures'),
    ]
    for ax, katrina_val, title in income_panels:
        for label, color in zip(income_labels, income_colors):
            if katrina_val is None:
                mask = df_trim['income_cut'] == label
            else:
                mask = ((df_trim['income_cut'] == label) &
                        (df_trim['katrina_tenure'] == katrina_val))
            n = mask.sum()
            kmf = KaplanMeierFitter()
            kmf.fit(df_trim.loc[mask, 'duration'], df_trim.loc[mask, 'moved_out'],
                    label=f'{label} (n={n:,})')
            kmf.plot_survival_function(ax=ax, color=color, ci_show=True)
        ax.set_title(title)
        ax.set_xlabel('Days')
        ax.set_ylabel('Survival Probability')
        ax.legend(fontsize=8, loc='upper right')

    axes[1, 0].axis('off')
    plt.tight_layout()
    out = Path(FIGURES_DIR) / "km_curves.png"
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.show()


def distribution_comparison(df_trim):

    fig, ax = plt.subplots(figsize=(10, 6))

    kmf = KaplanMeierFitter()
    kmf.fit(df_trim['duration'], df_trim['moved_out'],
            label='Kaplan-Meier (empirical)')
    kmf.plot_survival_function(ax=ax, color='black', ci_show=False)

    for fitter, label, color, ls in [
        (WeibullFitter(),     'Weibull',      'blue',  '-'),
        (LogLogisticFitter(), 'Log-Logistic', 'red',   '--'),
        (ExponentialFitter(), 'Exponential',  'green', '-.'),
    ]:
        fitter.fit(df_trim['duration'], df_trim['moved_out'])
        full_label = f'{label} (AIC={fitter.AIC_:,.0f}, BIC={fitter.BIC_:,.0f})'
        fitter.plot_survival_function(ax=ax, color=color, linestyle=ls,
                                      ci_show=False, label=full_label)

    ax.set_title('Distribution Comparison — Full Sample (Appendix)')
    ax.set_xlabel('Days')
    ax.set_ylabel('Survival Probability')
    ax.legend(fontsize=9)
    plt.tight_layout()
    out = Path(FIGURES_DIR) / "distribution_comparison.png"
    plt.savefig(out, dpi=300, bbox_inches='tight')
    plt.show()


def build_interaction_dummies(df):
    df = df.copy()
    df['black'] = (df['black_white_other'] == 2).astype(int)
    df['other_race'] = (df['black_white_other'] == 0).astype(int)
    df['fema_100'] = (df['fema_category'] == 100).astype(int)
    df['fema_500'] = (df['fema_category'] == 500).astype(int)
    df['black_x_katrina'] = df['black'] * df['katrina_tenure']
    df['other_x_katrina'] = df['other_race'] * df['katrina_tenure']
    df['fema100_x_katrina'] = df['fema_100'] * df['katrina_tenure']
    df['fema500_x_katrina'] = df['fema_500'] * df['katrina_tenure']
    df['black_x_fema100'] = df['black'] * df['fema_100']
    df['black_x_fema500'] = df['black'] * df['fema_500']
    df['other_x_fema100'] = df['other_race'] * df['fema_100']
    df['other_x_fema500'] = df['other_race'] * df['fema_500']
    df['black_x_fema100_x_katrina'] = df['black'] * df['fema_100'] * df['katrina_tenure']
    df['black_x_fema500_x_katrina'] = df['black'] * df['fema_500'] * df['katrina_tenure']
    df['other_x_fema100_x_katrina'] = df['other_race'] * df['fema_100'] * df['katrina_tenure']
    df['other_x_fema500_x_katrina'] = df['other_race'] * df['fema_500'] * df['katrina_tenure']
    return df


cox_cols = [
    'black', 'other_race', 'fema_100', 'fema_500', 'katrina_tenure',
    'black_x_katrina', 'other_x_katrina',
    'fema100_x_katrina', 'fema500_x_katrina',
    'black_x_fema100', 'black_x_fema500',
    'other_x_fema100', 'other_x_fema500',
    'black_x_fema100_x_katrina', 'black_x_fema500_x_katrina',
    'other_x_fema100_x_katrina', 'other_x_fema500_x_katrina',
]


def cox_hmda(df_trim):
    df_trim = build_interaction_dummies(df_trim)
    hmda_race = df_trim[df_trim['black_white_other'].notna()].copy()
    cph = CoxPHFitter()
    cph.fit(hmda_race[cox_cols + ['duration', 'moved_out']],
            duration_col='duration',
            event_col='moved_out')
    cph.print_summary()
    return cph


def weibull_aft_hmda_race(df_trim):
    df_trim = build_interaction_dummies(df_trim)
    hmda_race = df_trim[df_trim['black_white_other'].notna()].copy()
    waf = WeibullAFTFitter()
    waf.fit(hmda_race[cox_cols + ['duration', 'moved_out']],
            duration_col='duration',
            event_col='moved_out',
            robust=True)
    waf.print_summary()
    return waf


def weibull_aft_hmda_income(df_trim):
    # TODO: implement tomorrow
    # same spec as race model but add income_adjusted as covariate
    # subset to income_adjusted notna and income_trim_flag == False
    pass


def weibull_aft_census(df_trim):
    # TODO: implement tomorrow
    # census subsample -- full sample, tract-level demographics
    # census_percent_black_ho (continuous) and census_black_categories_ho (categorical)
    # census_income instead of income_adjusted
    # interaction spec: census_black_categories_ho x fema_category x katrina_tenure
    pass


def scenario_estimates(waf):
    # TODO: implement tomorrow
    # compute predicted time ratios for each of 6 scenarios:
    # race (Black/White) x fema_category (0/100/500) x katrina_tenure (0/1)
    # from preferred Weibull AFT model
    # visualize as bar chart or dot plot
    pass


def save_outputs():
    # TODO: implement tomorrow
    # save all figures to outputs/figures/
    # save coefficient tables to outputs/tables/
    pass


def main():
    df = pd.read_parquet(Path(PROCESSED_DIR) / "analysis_ready.parquet")
    df_trim = df[df['move_in'] >= 0].copy()

    km_curves(df_trim)
    distribution_comparison(df_trim)
    df_trim = build_interaction_dummies(df_trim)
    cox_hmda(df_trim)
    weibull_aft_hmda_race(df_trim)
    weibull_aft_hmda_income(df_trim)
    weibull_aft_census(df_trim)
    scenario_estimates(None)
    save_outputs()


if __name__ == "__main__":
    main()