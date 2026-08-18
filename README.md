# Survival Analysis of Homeownership Tenure After Hurricane Katrina

## Overview
This repository contains the full analysis pipeline for a study of 
homeownership tenure duration in Orleans Parish, Louisiana following 
Hurricane Katrina (2005). The study examines how race, flood zone 
designation, and storm exposure interact to shape the time until 
home sale, using survival analysis methods applied to a novel 
parcel-level dataset constructed from public records.

## Data Sources
- **Orleans Parish Land Records (OPLR):** Web-scraped residential 
  transaction records 1985-2020
- **HMDA Loan Application Records:** Matched to OPLR records to 
  assign parcel-level race and income demographics
- **FEMA Flood Insurance Rate Maps (FIRM):** Spatial join assigning 
  100-year and 500-year flood zone designation per parcel
- **US Census:** Tract-level demographics (1990, 2000, 2010)

## Methods
Kaplan-Meier nonparametric survival curves and Weibull accelerated 
failure time (AFT) models with parcel-level frailty terms. Key 
specification includes a triple interaction of race × flood zone × 
Katrina exposure.

## Pipeline