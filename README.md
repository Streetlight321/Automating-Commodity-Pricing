# Automating Commodity Pricing (copy of "Automating Commodity Guidance")

This repository scrapes commodity pricing (LME and COMEX) and uploads daily price facts to a Supabase table. It's a copy of a project called "Automating Commodity Guidance" and was inspired by a project done at ABB.

## Contents
- `Scraper.py` — main scraping logic using Selenium (Firefox/geckodriver) + BeautifulSoup.
- `SupaUpload.py` — helper that inserts scraped records into a Supabase table using environment variables for credentials.
- `.github/workflows/daily-lme.yml` — GitHub Actions workflow that can run the scraper on a schedule or manually.

## Quick overview
- The scraper fetches the 3‑month rows from LME commodity pages (Aluminum, Zinc, Copper) and extracts Bid/Offer values (converted from lb to kg by dividing by 2204.62).
- It also scrapes COMEX copper highs/lows/opens and uploads records to the `price_facts` table in Supabase.

## Prerequisites
- Python 3.8+
- Firefox browser installed
- Geckodriver (matching Firefox) available on PATH (Windows: place `geckodriver.exe` on PATH or next to the scripts)
- Python packages: selenium, beautifulsoup4, pandas, python-dotenv, supabase

Install example (PowerShell):

```powershell
python -m pip install --upgrade pip
pip install selenium beautifulsoup4 pandas python-dotenv supabase
```

## Environment variables
Create a `.env` file in the repository root (or set env vars in your environment):

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=eyJ...your_key...
```

## Suggested Supabase table schema
Use the SQL below in the Supabase SQL editor to create the `price_facts` table used by the scripts:

```sql
create table if not exists public.price_facts (
  id bigserial primary key,
  date date not null,
  commodity text not null,
  low numeric,
  high numeric,
  last numeric,
  inserted_at timestamptz default now()
);
```

## How to run locally
1. Ensure Firefox + geckodriver are installed and geckodriver is on PATH.
2. Create `.env` with Supabase credentials.
3. From a PowerShell prompt in the repo folder run:

```powershell
python Scraper.py
```

The script prints scraped values and uploads rows to the configured `price_facts` table.

## GitHub Actions
This repo includes a workflow at `.github/workflows/daily-lme.yml` to run the scraper on a schedule and/or manually via workflow_dispatch.

Key details:
- The workflow runs on `ubuntu-latest` and installs Python dependencies before running `python Scraper.py`.
- Add the following repository secrets (Settings → Secrets and variables → Actions):
  - `SUPABASE_URL`
  - `SUPABASE_KEY`

Important: If the workflow requires a headless browser, ensure the runner supports the chosen browser and driver; this workflow uses Selenium and expects the environment to support running headless Firefox. If you hit errors in CI, consider using a Docker container with Firefox and geckodriver or adjust the workflow to install geckodriver and a matching Firefox package.

## Data sharing
I am open to sharing the collected data. If you'd like access to the exported dataset or daily extracts, please open an issue in this repository or contact the repo owner directly. We can provide CSV exports, grant read-only access on Supabase, or add an API endpoint depending on your needs.

## Troubleshooting & notes
- Geckodriver not found: add `geckodriver.exe` to PATH or next to the script.
- Selenium timeouts: increase WebDriverWait time in `Scraper.py` or inspect page markup to update selectors.
- HTML changes: the LME pages can change structure or column labels; update selectors in `LME_commodities` if scraping fails.
- Upload errors: validate `SUPABASE_URL` and `SUPABASE_KEY`. Use an appropriate key with write permissions.
- Defensive improvements: `Scraper.py` currently assumes the scraper returns valid values; consider adding checks to avoid uploading when values are None.

## Scheduling locally
- Windows: use Task Scheduler to run `python c:\path\to\Scraper.py` daily. Configure working directory and run permissions.
- Linux/macOS: use cron or systemd timers.

## Next steps (suggestions)
- Add CLI flags and a `--dry-run` mode that scrapes but does not upload.
- Add retries and robust logging.
- Add unit/integration tests and a pinned `requirements.txt`.
- Provide an export endpoint or a public dataset CSV if data-sharing demand grows.

## Acknowledgements
Inspired by a project done at ABB. This repository is a copy of "Automating Commodity Guidance" adapted for personal use and sharing.
