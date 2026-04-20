# OfferWatch

**OfferWatch** is a data-driven job search platform built by Ansh Vats, Rudra Patel, Vansh Kumar, Amogh Peddapothla, and Brian Skiles for CS 3200 — Spring 2026.

Instead of scattered spreadsheets and self-reported email updates, OfferWatch centralizes the entire hiring pipeline — every application, interview, and offer — into a single shared platform powered by a relational database. It transforms raw job search activity into meaningful insights for students, career advisors, recruiters, and administrators, helping every stakeholder make smarter decisions and approach the hiring process with greater clarity and confidence.

---

## Table of Contents

- [About the App](#about-the-app)
- [User Personas](#user-personas)
- [Prerequisites](#prerequisites)
- [Repo Structure](#repo-structure)
- [Setting Up the Repo](#setting-up-the-repo)
- [Running the Docker Containers](#running-the-docker-containers)
- [Frontend (Streamlit)](#frontend-streamlit)
- [Backend (Flask REST API)](#backend-flask-rest-api)
- [Database (MySQL)](#database-mysql)
- [Important Tips](#important-tips)

---

## About the App

The hiring process is fragmented and opaque. Students lose track of applications, advisors have no visibility into which students are falling behind, and recruiters lack the data they need to identify top candidates efficiently.

OfferWatch solves this by providing:

- A **personalized application tracking dashboard** with analytics so students can visualize their own hiring funnel
- A **cohort-level analytics view** for career advisors and program directors to spot trends, flag struggling students, and measure placement outcomes
- A **recruiter-facing pipeline view** to surface qualified candidates and track applicant volume by position
- A **system administration layer** for maintaining data integrity, correcting records, and keeping the platform reliable

---

## User Personas

### 1. Alex Chen — Job-Seeking Student
Alex can log and track every job application, interview, and offer in one place. The dashboard visualizes Alex's personal hiring funnel (applied → interviewing → offered → accepted), surfaces key metrics like interview conversion rate and average time-to-offer, and allows comparison between resume versions and target industries.

---

### 2. Lisa Rodriguez — Program Director / Advisor
Lisa oversees a large cohort of students and needs high-level visibility into how the group is performing across companies and industries. She can analyze aggregated placement data, identify trends in hiring outcomes, detect bottlenecks in the funnel, and drill down into individual student records when a concern arises.

---

### 3. Dr. Maria Patel — University Career Advisor
Dr. Patel works one-on-one with students to improve their job search outcomes. She can view cohort-wide conversion rates (applied → interview → offer), flag "silent strugglers" (students with zero applications or no activity in 14+ days), compare resume version effectiveness by industry, and log coaching notes directly against individual student applications.

---

### 4. Jordan Kim — Pipeline Recruiter
Jordan uses OfferWatch to identify high-potential candidates, see how many applicants have applied to specific open positions, and contact universities with strong pipelines in their target hiring areas. The recruiter view makes it easy to search and filter students by major, GPA, or target industry.

---

### 5. Evan Carter — System Administrator
Evan is responsible for keeping the platform accurate and reliable. He can update or correct any application record, manage user accounts, audit data for inconsistencies, and trigger any maintenance tasks needed to keep the database healthy.

---

## Prerequisites

- A GitHub account
- A terminal-based or GUI Git client (e.g., [GitHub Desktop](https://desktop.github.com/) or the Git plugin for VSCode)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running on your machine
- A distribution of Python running on your laptop. The course-supported distribution is [Anaconda](https://www.anaconda.com/download) or [Miniconda](https://www.anaconda.com/docs/getting-started/miniconda/install).

  Create a new Python 3.11 environment named `db-proj`:
  ```bash
  conda create -n db-proj python=3.11
  conda activate db-proj
  ```

  Install the Python dependencies for both the API and app locally (so your IDE can provide autocompletion and linting):
  ```bash
  cd api
  pip install -r requirements.txt
  cd ../app/src
  pip install -r requirements.txt
  ```

  > **Why install locally if everything runs in Docker?** Installing the packages locally lets your IDE (VSCode) provide autocompletion, linting, and error highlighting as you write code. The app itself always runs inside the Docker containers — the local install is just for editor support.

- **VSCode** with the Python plugin installed (course staff will only support VSCode)

---

## Repo Structure

```
offerwatch/
├── app/                    # Streamlit frontend
│   └── src/
│       ├── pages/          # One .py file per page, prefixed by persona number
│       ├── modules/
│       │   └── nav.py      # Role-based sidebar navigation
│       ├── Home.py         # Landing page with persona selector
│       └── .streamlit/
│           └── config.toml # Disables default Streamlit sidebar
├── api/                    # Flask REST API
│   ├── backend/
│   │   ├── student/        # Routes for Alex Chen persona
│   │   ├── program_director/ # Routes for Lisa Rodriguez persona
│   │   ├── university_career/ # Routes for Dr. Maria Patel persona
│   │   ├── recruiter/      # Routes for Jordan Kim persona
│   │   └── admin/          # Routes for Evan Carter persona
│   └── requirements.txt
├── database-files/         # SQL scripts to initialize MySQL (run alphabetically)
├── datasets/               # Source datasets
├── ml-src/                 # ML model development (notebooks, training scripts)
├── docker-compose.yaml     # Main Docker Compose config
├── sandbox.yaml            # Personal testing Docker Compose config
└── README.md
```

---

## Setting Up the Repo

### One team member (Repo Owner) must do this first:

1. **Fork** this template repo into your own GitHub account and rename it to match your project.
2. Under **Settings → Collaborators and Teams**, add all teammates with **Write** access.

### All other team members:

1. Accept the GitHub invitation.
2. Clone the team repo to your local machine:
   ```bash
   git clone <your-team-repo-url>
   ```
3. Set up the `.env` file in the `api/` folder:
   ```bash
   cd api
   cp .env.template .env
   ```
   Open `.env` and replace the `<...>` placeholder on the last line with a password. Do not reuse a password from any other service.

---

## Running the Docker Containers

All three services (Streamlit app, Flask API, MySQL database) run inside Docker containers coordinated by `docker-compose.yaml`.

**Start all containers** (runs in the background):
```bash
docker compose up -d
```

**Stop and remove containers**:
```bash
docker compose down
```

**Restart a specific service** (replace `app` with `api` or `db` as needed):
```bash
docker compose up app -d
```

**Stop containers without deleting them**:
```bash
docker compose stop
```

**Fully rebuild the database** (required any time you edit a `.sql` file):
```bash
docker compose down db -v && docker compose up db -d
```

> You can also manage containers visually through the **Docker Desktop** GUI after the first run.

### Personal Sandbox (Optional)

If you want a separate copy of the repo to experiment without touching the team repo, use `sandbox.yaml` instead:

```bash
docker compose -f sandbox.yaml up -d    # start
docker compose -f sandbox.yaml down     # stop and delete
docker compose -f sandbox.yaml stop     # stop without deleting
```

---

## Frontend (Streamlit)

The frontend lives in `app/src/` and is built with [Streamlit](https://streamlit.io/). When the app loads, `Home.py` presents a persona selector that sets the user's role in `session_state`. `app/src/modules/nav.py` uses that role to render the correct sidebar links for the session, and `app/src/.streamlit/config.toml` disables the default Streamlit navigation panel so the app controls it entirely.

Any saved changes to `.py` files in `app/src/` are hot-reloaded — click **Always Rerun** in the browser tab to pick them up. If a bug crashes the container, fix it and run `docker compose restart app`.

---

## Backend (Flask REST API)

The REST API lives in `api/backend/` and is organized into one Blueprint per persona, each handling the routes for that user's feature set. All four HTTP verbs are used — for example, `GET /advisor/<id>/dashboard` returns cohort-wide conversion rates, `POST` adds coaching notes, `PUT` corrects application records, and `DELETE` removes notes. The API hot-reloads on file save.

---

## Database (MySQL)

The MySQL database is initialized by running all `.sql` files in `database-files/` in **alphabetical order** when the container is first created. File naming conventions reflect this ordering (e.g., `00_schema.sql` before `01_data.sql`).

### Key Entities

| Entity | Description |
|---|---|
| `Student` | Job-seeking students with GPA, major, activity tracking |
| `User` | Shared user table for login and role assignment |
| `Job_Application` | Applications linking students to positions, with status and resume used |
| `Position` | Open roles at employers |
| `Employer` | Companies with industry classification and location |
| `Industry` | Industry tags with placement rate and market share data |
| `Interview` | Interview records linked to applications |
| `Job_Offer` | Offer records including salary, deadline, and acceptance status |
| `Resume` | Resume versions with conversion rate tracking |
| `Advisor` | Career advisors linked to student cohorts |
| `StudentIndustry` | Bridge table for many-to-many student↔target industry |

### Updating the Database

If you modify any `.sql` file, you **must recreate** the MySQL container — restarting it alone will not re-run the SQL scripts:

```bash
docker compose down db -v && docker compose up db -d
```

Check the MySQL container's **Logs** tab in Docker Desktop (search for `Error`) to debug any SQL issues.

---

## Important Tips

1. **Always Rerun:** After saving changes to the Streamlit app, click the **Always Rerun** button in the browser tab so it picks up the latest code.
2. **Container crashes:** A Python bug will sometimes shut down the `app` container. Fix the bug, then restart with `docker compose restart`.
3. **MySQL logs are your friend:** If the database fails to initialize, open Docker Desktop → MySQL container → **Logs** tab and search for `Error`.
4. **Don't edit `.env` files into version control.** The `.env` file is in `.gitignore` for a reason — it contains your database password.
5. **SQL file order matters.** Files in `database-files/` run alphabetically. If table B depends on table A, make sure A's file sorts before B's.