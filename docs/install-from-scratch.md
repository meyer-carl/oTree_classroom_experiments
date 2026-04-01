# Install From Scratch

## Who This Is For

Use this guide if you are starting from a blank or nearly blank computer and want the simplest path to a working local oTree setup.

This guide assumes:

- you are comfortable opening a terminal
- you do not already have this project running
- you want to confirm the project works locally before you choose Heroku or ngrok

## Recommended Setup

The simplest local path for non-technical instructors is:

- a Mac or Linux computer
- Python `3.12`
- a terminal
- a web browser

If you are on Windows, the easiest teaching path is usually to use Heroku instead of trying to run the project locally first.

## Step 1: Install Python 3.12

1. Go to [python.org/downloads](https://www.python.org/downloads/).
2. Download Python `3.12`.
3. Run the installer.
4. After installation, open a terminal and check that Python is available:

```bash
python3.12 --version
```

You should see a Python `3.12.x` version number.

## Step 2: Get The Project Onto Your Computer

Choose one of these:

### Option A: Download a ZIP File

1. Download the project ZIP file that was shared with you.
2. Unzip it somewhere easy to find, such as `Documents`.
3. Open a terminal.
4. Change into the project folder:

```bash
cd /path/to/oTree_classroom_experiments
```

### Option B: Clone With Git

1. Install Git if it is not already installed.
2. Open a terminal.
3. Clone the project:

```bash
git clone REPO_URL_HERE
cd oTree_classroom_experiments
```

If someone sent you a ZIP file instead of a Git repository, use Option A.

## Step 3: Create The Local Python Environment

From the project root, run:

```bash
./scripts/bootstrap.sh
```

This creates a local `.venv` folder and installs the required Python packages, including oTree.

## Step 4: Verify The Installation

Run:

```bash
./scripts/verify.sh
```

If you want a broader confidence check before class, run:

```bash
./scripts/verify_high_coverage.sh
```

## Step 5: Set The Admin Password

Before launching oTree, set an admin password:

```bash
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
```

Keep this password in your private teaching notes.

## Step 6: Start oTree Locally

Run:

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

Then read [hosting-and-deployment.md](hosting-and-deployment.md).

## If Something Fails

- If `python3.12` is not found, Python is not installed correctly yet.
- If `./scripts/bootstrap.sh` fails, re-check that you are in the project root.
- If `./scripts/verify.sh` fails, stop there and fix the local setup before trying Heroku or ngrok.
- If `otree devserver` works locally but students cannot connect, the problem is your public hosting method, not the local app.

## What To Read Next

- [../INSTRUCTOR_QUICKSTART.md](../INSTRUCTOR_QUICKSTART.md)
- [hosting-and-deployment.md](hosting-and-deployment.md)
- [classroom-readiness.md](classroom-readiness.md)
