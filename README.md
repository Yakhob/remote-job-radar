# remote-job-radar
Multi-source remote job scanner for QA, automation, frontend, AI and junior-to-mid technical roles. Pulls from 8+ job boards and outputs a filtered Excel sheet.
```
# Remote Job Radar (Engine A)
```
A Python automation that scans multiple remote job boards and builds a filtered, high-signal job list for QA, automation, frontend, AI, and junior-to-mid technical roles.

Instead of scraping one platform, this engine aggregates **real hiring feeds** from:
```
- Remotive
- Remotive Community
- Flexa
- TestDevJobs
- ChatGPT-Jobs
- RemoteOK
- WorkingNomads
- WeWorkRemotely
- Jobspresso
```
Then applies intelligent filters for:
- Skill relevance (QA, testing, automation, frontend, AI, etc)
- Seniority blocking (no staff / principal / infra / ML roles)
- Location eligibility (India + worldwide)
- Recency window (last 14 days)

The result is a daily Excel sheet of only jobs worth applying to.

---

## What it does

1. Pulls job data from multiple public APIs and job boards
2. Filters out:
   - Senior-only roles
   - ML, infra, and research positions
   - Country-restricted jobs
3. Keeps:
   - QA, automation, frontend, AI, and creative jobs
   - Global or India-friendly roles
4. Exports the result to `daily_jobs.xlsx`

---

## How to run

### 1. Install Python 3.9+

### 2. Install dependencies
```bash
pip install -r requirements.txt
