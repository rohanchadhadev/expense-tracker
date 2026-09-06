# Expense Tracker

A mobile-first, offline expense tracker built with [Flet](https://flet.dev). Track expenses, organize them by category, view spending charts, and set monthly budgets with over-budget alerts. All data is stored locally on-device (SQLite) — nothing leaves your phone.

## Install on Android

**[Download the APK](https://github.com/rohanchadhadev/expense-tracker/releases/download/latest/expense-tracker.apk)**

1. Open the link above on your phone (or download it there and transfer the `.apk` file over).
2. When prompted, allow your browser/file manager to **install unknown apps** (Android will ask the first time).
3. Tap the downloaded file and install.

This repo is private, so the link above only works while you're signed in to a GitHub account with access to it.

Every push to `master` rebuilds the APK automatically and updates the `latest` release, so the link always points to the newest build.

## Features

- Add, edit, and delete expenses
- Custom categories with color tags and filtering
- Pie and bar charts summarizing spending by category and by month
- Monthly budgets (overall and per-category) that reset each month, with a one-tap copy from the previous month and over-budget alerts
- A Savings category that keeps its full target unless another category goes over budget that month, in which case the overage is deducted from it
- Currency selection

## Running locally (development)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
