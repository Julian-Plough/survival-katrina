
---

## Key Methodological Choices

| Choice | Value | Justification |
|---|---|---|
| Minimum duration | 90 days | Housing tenure literature convention — citation needed |
| Income trim | 1st/99th percentile | Applied at model stage, HMDA subsample only |
| Censoring date | Jan 1 2021 (Stata: 22281) | Approximate OPLR scrape end date — verify |
| Katrina date | Aug 29 2005 (Stata: 16677) | Official landfall date |
| Census geography | Tract | To be redone at block group level |
| FEMA map vintage | Unknown | To be documented |

---

## Known Issues and Future Work

- [ ] Verify exact OPLR scrape date for censoring
- [ ] Identify and document FEMA map vintage
- [ ] Redo spatial join at block group level in geopandas
- [ ] Update inflation adjustment to 2026 dollars
- [ ] Translate full upstream Stata pipeline to Python
- [ ] Find explicit citation for 90-day duration trim
- [ ] Clarify sale_price vs purchase_price distinction in causal_dataset
- [ ] Verify which of data_setup_2_22.do vs Causal_Data_Setup.do was final run