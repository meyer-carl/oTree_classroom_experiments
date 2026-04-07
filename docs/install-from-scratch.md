# Install From Scratch

## Who This Is For

Use this guide if you are starting from a blank or nearly blank computer and want the simplest path to a working local setup.

## Important Question

Do I need to install oTree separately? No.

When you run `./scripts/bootstrap.sh`, it creates a local Python environment for this project and installs the required Python packages, including oTree, into that local `.venv`.

## Recommended Setup

The simplest local path for non-technical instructors is:

- a Mac or Linux computer
- Python `3.12`
- a terminal
- a web browser

If you are on Windows, the easiest teaching path is usually to use `Heroku` instead of running the project locally first.

## Step 1: Install Python 3.12

1. Go to [python.org/downloads](https://www.python.org/downloads/).
2. Download Python `3.12`.
3. Run the installer.
4. Open a terminal and check that Python is available.

Paste this into Terminal:

```bash
python3.12 --version
```

You should see a Python `3.12.x` version number.

## Step 2: Put The Project On Your Computer

Choose one of these:

### Option A: Download A ZIP

1. Download the project ZIP file.
2. Unzip it somewhere easy to find, such as `Documents`.
3. Open a terminal.
4. Change into the project folder.

Paste this into Terminal and replace the sample path with your own:

```bash
cd /path/to/oTree_classroom_experiments
```

### Option B: Clone With Git

1. Install Git if it is not already installed.
2. Open a terminal.
3. Clone the project and enter the folder.

Paste this into Terminal and replace `REPO_URL_HERE` with the real repository URL:

```bash
git clone REPO_URL_HERE
cd oTree_classroom_experiments
```

If someone sent you a ZIP file instead of a repository link, use Option A.

## Step 3: Install The Project

Paste this into Terminal from the project root:

```bash
./scripts/bootstrap.sh
```

This creates the local `.venv` folder and installs the required Python packages, including oTree.

## Step 4: Verify The Installation

Paste this into Terminal:

```bash
./scripts/verify.sh
```

If you want the broader pre-class check, paste this into Terminal:

```bash
./scripts/verify_high_coverage.sh
```

## Step 5: Set The Admin Password

Paste this into Terminal and replace the example password with your own:

```bash
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
```

## Step 6: Start oTree Locally

Paste this into Terminal:

```bash
source .venv/bin/activate
otree devserver
```

Then open the local oTree URL shown in the terminal.

## Step 7: Run One Demo Before Anything Else

1. Open the local site in your browser.
2. Log in as `admin`.
3. Create one `live_demo` session.
4. Open that session in a second browser or private window.
5. Confirm that you can move through the first few screens.

If that works, your local setup is ready.

## Step 8: Choose How Students Will Connect

Once the local demo works, choose your public access method:

- `Heroku`: easiest managed option
- `ngrok`: free option for small live classes
- `Ubuntu/Linux server`: advanced option

Then read `01_instructor_pdfs/03_hosting_and_deployment.pdf` or the matching website page in `02_docs_site/`.

## If Something Fails

- If `python3.12` is not found, Python is not installed correctly yet.
- If `./scripts/bootstrap.sh` fails, re-check that you are in the project root.
- If `./scripts/verify.sh` fails, stop there and fix the local setup before trying `Heroku` or `ngrok`.
- If `otree devserver` works locally but students cannot connect, the problem is the hosting method, not the local app.

## What To Read Next

Continue in this order:

1. `01_instructor_pdfs/02_instructor_quickstart.pdf`
2. `01_instructor_pdfs/03_hosting_and_deployment.pdf`
3. `01_instructor_pdfs/04_identity_and_grading.pdf`

If you prefer clickable docs inside the ZIP, open `02_docs_site/index.html`.
