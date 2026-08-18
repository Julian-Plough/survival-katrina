#####################################################
# SURVIVAL ANALYSIS REPO SETUP - COMMAND LOG
# Project: survival-katrina
# Date: August 2026
#####################################################

# STEP 1: Switch to external drive
cd /d "D:\Survival Analysis 2026"

# STEP 2: Initialize git repo
# "git init <name>" creates a new folder with git tracking inside it
git init survival-katrina
cd survival-katrina

# Reinitialize if needed (safe to run again, no data lost)
git init

# STEP 3: Set global git identity
# This tells git who you are for commit history
# Use the email you signed up to GitHub with
git config --global user.name "Julian Plough"
git config --global user.email "your@email.com"

# STEP 4: Fix external drive ownership warning
# Git is cautious about repos on external drives - this adds an exception
git config --global --add safe.directory "D:/Survival Analysis 2026/survival-katrina"

# STEP 5: Verify git is working
# Should say "On branch master, No commits yet"
git status

# STEP 6: Connect local repo to GitHub
# "remote add origin" tells git where to push your code
# Do this AFTER creating a blank repo at github.com
# Same-name folders on local and GitHub is convention, not required
git remote add origin https://github.com/Julian-Plough/survival-katrina.git

# Verify the remote connection
# Should print "origin" with fetch and push URLs
git remote -v

#####################################################
# HOW GIT WORKS
#####################################################

# You have TWO copies of your repo:
# LOCAL:  D:\Survival Analysis 2026\survival-katrina\  (where you work)
# REMOTE: github.com/Julian-Plough/survival-katrina    (backup + public)

# GitHub does NOT update automatically.
# Nothing goes to GitHub until you explicitly run "git push".

# The three commands you will use 90% of the time:
git add .                    # stage all changed files
git commit -m "message"      # save a local snapshot with a label
git push                     # send snapshot to GitHub

# Files are NOT duplicated per version.
# Git tracks changes invisibly in the .git folder.
# You can always roll back to any previous commit.

#####################################################
# WHEN TO COMMIT
#####################################################

# Commit when you've done ONE meaningful thing.
# Test: can you write a clear one-sentence description of what changed?
# If yes, commit.

# Rules of thumb:
# - Commit when something WORKS, before you start changing it
# - Commit when you finish a logical unit of work
# - Commit BEFORE doing anything experimental or risky
# - Never commit broken code if you can help it
# - Think of commits as save points in a video game

# Natural commit points for this project:
# "Initial repo structure - folders and starter files"
# "Add config file with data paths"
# "Module 1 complete - data assembly running"
# "Module 2 complete - feature engineering"
# "Module 3 complete - KM curves and Cox model"
# "Module 4 complete - Weibull AFT and scenario figures"
# "Add output figures and tables"
# "Manuscript draft complete"

#####################################################
# STEP 7: Create folder structure
#####################################################

# Creates all project folders in one command
# data/raw      = .dta files copied from Samsung T5
# data/external = census, CPI, shapefiles
# data/processed = intermediate outputs (not committed)
# src           = all Python scripts
# notebooks     = scratch/exploration
# outputs       = figures and tables (not committed)
# docs          = data provenance documentation
mkdir data\raw data\external data\processed src notebooks outputs\figures outputs\tables docs
#####################################################
# REPO STRUCTURE
#####################################################

# The repo lives at:
# D:\Survival Analysis 2026\survival-katrina\

# Root files (sit directly in survival-katrina/):
# .gitignore      - tells git what NOT to track (data, outputs, caches)
# README.md       - project overview, shows on GitHub front page
# requirements.txt - Python packages needed to run the pipeline
# SETUP.md        - this file, setup guide and command log

# Folders:
# data/raw/       - .dta source files copied from Samsung T5
# data/external/  - census, CPI, shapefiles
# data/processed/ - intermediate outputs (not committed to git)
# src/            - all Python scripts (the pipeline)
# notebooks/      - scratch exploration
# outputs/        - figures and tables (not committed to git)
# docs/           - data provenance notes

# Key principle: if you deleted everything except data/raw/ and src/,
# you should be able to regenerate everything else by running the pipeline.

#####################################################
# STEP 8: Create root files
#####################################################

# Create these four files in the survival-katrina root in VSCode:
# Right-click survival-katrina in Explorer panel -> New File

# .gitignore      - paste gitignore content
# README.md       - paste README content
# requirements.txt - paste requirements content
# SETUP.md        - this file

#####################################################
# STEP 9: First commit and push to GitHub
#####################################################

# Stage all files (tells git to include everything in next snapshot)
git add .

# Take the snapshot with a descriptive message
git commit -m "Initial repo structure - folders and starter files"

# Push to GitHub (-u sets origin master as default, only needed first time)
git push -u origin master

# Browser will open for GitHub authentication on first push - complete it
# After this, future pushes just need: git push

# Verify at: github.com/Julian-Plough/survival-katrina
# The three core commands, what they actually do:
git add .        # load the tray (stage) - everything MINUS what is in .gitignore
git commit -m "message"      # take the photo (snapshot, LOCAL only)
git push         # send the photo to GitHub (REMOTE update)

# Always save in VSCode before git add .
# Git cannot see unsaved changes.


#####################################################
# STEP 10: Python Environment Setup
#####################################################

# We use the myenv conda environment stored in C:\Users\ploug\miniconda3\envs\myenv
# To activate it from any directory:
C:\Users\ploug\miniconda3\Scripts\activate && conda activate myenv

# Verify you are in the right place:
# Prompt should show: (myenv) D:\Survival Analysis 2026\survival-katrina>

# Key packages (verify with: conda list | findstr "pandas pyreadstat lifelines")
# pandas        - data manipulation
# pyreadstat    - reads Stata .dta files into pandas
# lifelines     - survival analysis (KM, Cox, Weibull AFT)
# geopandas     - spatial operations (for future spatial join translation)

# Install if missing:
conda install pyreadstat -y
pip install lifelines