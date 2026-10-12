# ResearchConnect (PRAYAS) - Starter Project

A research collaboration platform that recommends collaborators using four matching methods
(keyword, tag/Jaccard, TF-IDF + cosine, hybrid) with explanations. Works for intra-college,
inter-college and industry matching.

---------------------------------------------------------------------
## 1. What is inside (folder map)

```
prayas/
├── README.md                  <- you are here
├── docker-compose.yml         <- starts PostgreSQL (optional at first)
├── docs/schema.sql            <- database tables written as SQL (for your report)
├── docs/supabase_security.sql <- Supabase lock-down (also done automatically)
├── backend/                   <- Python (FastAPI) = the brain
│   ├── requirements.txt       <- libraries to install
│   ├── .env.example           <- settings template (copy to .env)
│   ├── app/
│   │   ├── main.py            <- starts the API
│   │   ├── config.py, database.py, models.py   <- settings + tables
│   │   ├── schemas.py         <- input validation
│   │   ├── security.py, deps.py                <- password hashing, login tokens, roles
│   │   ├── services.py        <- helper functions
│   │   ├── alerts.py, alert_rules.py, email_service.py  <- match emails to both researchers
│   │   ├── routers/           <- API endpoints (auth, profiles, projects, match, requests, opportunities, admin)
│   │   └── matching/          <- THE RESEARCH PART: keyword.py, tags.py, tfidf.py, hybrid.py, engine.py
│   ├── seed/data_gen.py       <- creates a synthetic test dataset
│   ├── seed/seed_db.py        <- loads that dataset into the database
│   ├── evaluation/run_experiments.py   <- compares the 4 methods (precision, recall, F1, time)
│   ├── tests/test_matching.py <- automatic tests
│   └── data/                  <- generated data files go here
└── frontend/                  <- React website = the face
    ├── package.json, vite.config.js, index.html, .env.example
    └── src/ (main.jsx, App.jsx, api.js, index.css)
```

**Golden rule:** matching code lives ONLY in `backend/app/matching/`. It does not know about the
web or the database, so you can test it alone and use it in your research paper.

---------------------------------------------------------------------
## 2. Install these first (one time)

- Python 3.11 or newer  - https://www.python.org
- Node.js 20 or newer   - https://nodejs.org
- Git                   - https://git-scm.com
- VS Code (editor)      - https://code.visualstudio.com  (Antigravity or Claude Code can be used instead)
- Docker Desktop (only when you want PostgreSQL) - https://www.docker.com

---------------------------------------------------------------------
## 3. Step-by-step: run the BACKEND (start here)

Open a terminal inside the `prayas/backend` folder.

**Step 3.1 - virtual environment (keeps libraries separate)**
```
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Mac / Linux:  source .venv/bin/activate
```

**Step 3.2 - install libraries**
```
pip install -r requirements.txt
```

**Step 3.3 - settings file**
```
# Windows: copy .env.example .env      Mac/Linux: cp .env.example .env
```
Open `.env` and replace `SECRET_KEY` with any long random text. (By default the app uses SQLite,
a simple file database - no setup needed.)

**Step 3.4 - create the test dataset and test the matching engine (no database needed)**
```
python -m seed.data_gen
python -m evaluation.run_experiments
pytest
```
You should see a table with precision, recall, F1 and time for the four methods. The data is SYNTHETIC
(computer-made): label it that way in your report.

**Step 3.5 - fill the database with the test data**
```
python -m seed.seed_db
```
Test logins: `researcher1@prayas.test` / `Password123!`   and admin `admin@prayas.test` / `Password123!`

**Step 3.6 - start the API**
```
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs - you can click and test every endpoint there.

---------------------------------------------------------------------
## 4. Step-by-step: run the FRONTEND

Open a SECOND terminal inside `prayas/frontend`:
```
npm install
# Windows: copy .env.example .env      Mac/Linux: cp .env.example .env
npm run dev
```
Open http://localhost:5173 and log in with a test user. Try: Recommendations -> change the matching
method and the "search within" option (my college / other colleges / industry).

---------------------------------------------------------------------
## 5. Switch to PostgreSQL (when SQLite works)

You have two choices. Both use the SAME code - only `DATABASE_URL` in `backend/.env` changes.

### Option A - Supabase (recommended: hosted PostgreSQL, free tier, nothing to install)

1. Go to https://supabase.com, sign up, click **New project**. Choose a name, a region near you, and a
   strong **database password** (save it - you cannot see it again).
2. Wait about 2 minutes. Click **Connect** at the top of the project page and copy the **Session pooler**
   connection string (it ends in `:5432/postgres`).
3. Put it in `backend/.env` and replace the password placeholder with your real password:
   `DATABASE_URL=postgresql://postgres.xxxx:YOUR_PASSWORD@aws-0-xxxx.pooler.supabase.com:5432/postgres`
   (If the password contains `@`, `#`, `/` etc., URL-encode it: `@` becomes `%40`.)
4. Test the connection: `python -m app.check_db`  (should print "Connected to: postgresql").
5. Start the API once (`uvicorn app.main:app --reload`) - the tables are created automatically.
6. Load the demo data: `python -m seed.seed_db`. Look at your data in Supabase: **Table Editor**.

**Security - already handled:** Supabase can publish tables through its own public web API. On start-up this
project switches on *Row Level Security* with no policies (`ENABLE_RLS=true`), so that public API returns nothing
while our FastAPI backend keeps full access. A manual backup is `docs/supabase_security.sql` (paste into
Supabase SQL Editor). Never put the database password or the `service_role` key inside the React app.

**Free-tier warning:** free Supabase projects pause after about one week of inactivity. If the app suddenly
cannot connect, open the Supabase dashboard and click **Restore**. Do this the day before your demo.
Check current limits at https://supabase.com/pricing.

### Option B - PostgreSQL with Docker on your laptop
1. `docker compose up -d`  (in the `prayas` folder)
2. In `backend/.env` set:
   `DATABASE_URL=postgresql+psycopg2://prayas:prayas_pw@localhost:5432/prayas`
3. Run `python -m seed.seed_db`, then restart uvicorn.

Tables are created automatically from `app/models.py`. `docs/schema.sql` shows the same tables as SQL.

---------------------------------------------------------------------
## 6. Where do I put new code? (cheat sheet)

| I want to...                         | Edit this file |
|--------------------------------------|----------------|
| Add a database column/table          | `backend/app/models.py` (+ `docs/schema.sql`) |
| Change what a form accepts           | `backend/app/schemas.py` |
| Add a new API endpoint               | new file in `backend/app/routers/`, then add it in `app/main.py` |
| Change how matching works            | `backend/app/matching/` |
| Add more acronyms (ML = machine learning) | `SYNONYMS` in `matching/preprocess.py` |
| Change hybrid weights                | `DEFAULT_WEIGHTS` in `matching/hybrid.py` |
| Change when emails are sent / email text | `app/alert_rules.py`, `app/alerts.py`, `app/email_service.py` |
| Add a new web page                   | new function in `frontend/src/App.jsx` + a tab in the `tabs` list |
| Add a new API call for the website   | `frontend/src/api.js` |

---------------------------------------------------------------------
## 7. Intra-college, inter-college and industry (already designed in)

- `organizations` table: each college, university or company is an organisation.
- Roles: researcher, coordinator, industry, admin.
- Visibility on profiles/projects: `public` (all) or `org` (own organisation only).
- Matching scope: my college / other colleges / industry / everyone.
- Opportunities include `industry_challenge`, posted by industry or coordinators.

---------------------------------------------------------------------
## 7b. Email alerts when researchers match

When two researchers (or their projects/domains) match strongly, BOTH receive an email that says who the
other person is (name, organisation, department, domain), the match percentage, why they match (shared
topics and skills, related projects) and a link to connect.

How it works:
- Trigger: runs automatically in the background after a profile is saved or a project is created
  (`routers/profiles.py`, `routers/projects.py`). Also: the "Check matches now" button, `POST /alerts/run`.
- Rule: hybrid score >= `MATCH_ALERT_THRESHOLD` (default 0.30), or same domain and score >= half of it.
  Tune it in `.env`. Logic: `app/alert_rules.py` (matching) and `app/alerts.py` (who gets emailed).
- No repeats: each pair is stored in the `match_alerts` table and emailed only once.
- No spam: at most `MATCH_ALERT_MAX` (default 3) new alerts per trigger.
- Privacy: only people with "email alerts" ON receive and trigger emails; both must be able to see each
  other (visibility rules); the other person's email address is shown ONLY if both profiles are public.
- Email text and design: `build_match_email()` in `app/email_service.py`.

Try it WITHOUT any email account (dev mode):
```
python -m seed.data_gen && python -m seed.seed_db
python -m seed.run_alerts
```
Open the `.eml` files in `backend/outbox/` (double-click, or open in any text editor).

Send REAL emails: fill these in `backend/.env`, then restart the API.
- Gmail: `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_USER=you@gmail.com`,
  `SMTP_PASSWORD=<16-character app password>` (Google Account > Security > 2-Step Verification > App passwords)
- Or use a free tier of Brevo / SendGrid / Resend SMTP (better for production, avoids Gmail limits).
- For a real launch: get users' consent in the sign-up form and add an unsubscribe link.

Upgrading an old copy? The tables changed (`email_alerts`, `match_alerts`). With SQLite, delete
`backend/prayas.db` and run `python -m seed.seed_db` again. With PostgreSQL, run the new parts of `docs/schema.sql`.

---------------------------------------------------------------------
## 8. Real data for your research

1. Download real researcher data from OpenAlex (https://developers.openalex.org) - free, open licence.
2. Convert each author to the same JSON format as `backend/data/researchers.json`.
3. Ask faculty to judge pairs and save them as `backend/data/labels_faculty.csv`
   (columns: researcher_a, researcher_b, relevant).
4. Run `python -m evaluation.run_experiments --labels faculty`.
Report ONLY numbers from this run. Never type numbers by hand.

---------------------------------------------------------------------
## 9. Deployment (when the app works locally)

- **Database:** Supabase (section 5) or a PostgreSQL service on Render/Railway.
- **API:** Render or Railway. Add `DATABASE_URL` (your Supabase pooler URL), `SECRET_KEY`, `CORS_ORIGINS`, `APP_URL` as environment variables.
  Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`  (root folder: `backend`).
- **Frontend:** Vercel. Root folder: `frontend`. Add environment variable `VITE_API_URL` = your API URL.
- On the API set `CORS_ORIGINS` to your Vercel URL, and a strong `SECRET_KEY`.
- Never upload `.env` to GitHub. Delete the demo users (Password123!) before real use.

Antigravity / Claude Code are tools to WRITE code faster; the hosting is Render/Railway/Vercel.

---------------------------------------------------------------------
## 10. Suggested order of work

1. Run everything above once (Day 1).
2. Read `matching/` files and `evaluation/run_experiments.py`; change a weight and re-run (Day 2).
3. Replace the synthetic data with real/anonymised data and faculty labels.
4. Improve the UI (design screens in Google Stitch, then rebuild them in React).
5. Add: project-to-researcher match page, industry challenge form, charts for admin (Recharts).
6. Write tests, deploy, write the report.

## Known limits of this starter
- Matching engine, dataset generator and evaluation were run and tested. The API and website were
  written carefully but not run end-to-end in the environment that built this zip, so expect to fix a
  small bug or two on first run - paste the error to your assistant.
- Login rate limiting is a simple in-memory version; use a proper tool (e.g. slowapi + Redis) in production.
