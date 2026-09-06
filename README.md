# Expense Tracker

A mobile-first, offline personal finance app for tracking day-to-day spending, built with [Flet](https://flet.dev) (Python + Flutter).

Most budgeting apps either require an account, sync your transactions to a server, or bury simple daily tracking under features you'll never use. Expense Tracker is the opposite: a fast, single-purpose app for logging what you spend, seeing where it goes, and knowing when you're about to blow a monthly budget — with every byte of data staying on your device.

## What it does

- **Log expenses in seconds** — amount, category, date, and an optional note. Every entry shows up immediately on a calendar view of the current month, with a colored dot per category on any day you spent money.
- **Understand your spending** — pie charts break down the month by category (with and without a "Bills" category factored in, since fixed bills often skew the picture), and a running monthly total keeps you oriented.
- **Set monthly budgets that actually reset** — an overall budget and a per-category budget, scoped to each month independently, with an instant alert the moment you go over. Setting up a new month is a single tap: "Copy last month's budgets" carries every value forward instead of making you retype them.
- **Save automatically** — a built-in Savings category holds a monthly target. It keeps its full value for the month unless another category runs over budget, in which case the overage is deducted from Savings automatically — a simple, honest way to see the real cost of overspending.
- **Make it yours** — custom categories with color tags, and a choice of currency.

All data lives in a local SQLite database on the phone. There is no backend, no account, and no network access required — nothing you enter ever leaves the device.

## Download

This repo is private, so links below only work while signed in to a GitHub account with access to it.

### Version 2.1 (current)

**[Download v2.1](https://github.com/rohanchadhadev/expense-tracker/releases/download/v2.1/expense-tracker.apk)**

- Home screen is now fully scrollable — the calendar and the selected day's transaction list scroll together as one page instead of competing for space
- Fixed the Savings budget calculation: an overage in another category now correctly deducts from Savings instead of appearing to add to it

### Version 2.0

**[Download v2.0](https://github.com/rohanchadhadev/expense-tracker/releases/download/v2.0/expense-tracker.apk)**

- Per-month budgets, with one-tap copy from the previous month
- Automatic Savings category
- Calendar-based Home screen

### Version 1.0

**[Download v1.0](https://github.com/rohanchadhadev/expense-tracker/releases/download/v1.0/expense-tracker.apk)**

The original release: expenses, categories, charts, and a single budget per category shared across all months.

---

Every push to `master` also rebuilds a rolling **[latest development build](https://github.com/rohanchadhadev/expense-tracker/releases/download/latest/expense-tracker.apk)**, which may be ahead of v2.1 with unreleased changes.

## Installing on Android

1. Open a download link above on your phone (or download it elsewhere and transfer the `.apk` file over).
2. When prompted, allow your browser/file manager to **install unknown apps** — Android asks for this the first time you install an app from outside the Play Store.
3. Tap the downloaded file and install.

## Features

- Add, edit, and delete expenses
- Custom categories with color tags
- A calendar-based Home screen — spending shown as colored dots per day, tap any date to see its transactions
- Pie charts summarizing spending by category, with and without Bills
- Monthly budgets (overall and per-category), scoped per month, with a one-tap copy from the previous month and over-budget alerts
- An automatic Savings category that keeps its full target unless another category goes over budget that month
- Currency selection

## How it's built

The app is written entirely in Python using [Flet](https://flet.dev), which compiles to a native Flutter app under the hood — no Dart or Java required to develop it. The Android APK is built and published automatically by GitHub Actions on every push to `master`, so shipping a new build never requires a local Android SDK or Flutter toolchain.

Data is persisted locally with Python's built-in `sqlite3` module — no ORM, no external database, no server.

## Running locally (development)

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

This runs the app in a native desktop window (the fastest way to iterate on Windows), backed by the exact same code that ships to Android.
