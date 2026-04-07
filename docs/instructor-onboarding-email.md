Subject: Please test the oTree classroom experiments before first use

Hi all,

I am sharing an instructor-ready oTree classroom experiment bundle for live behavioral and experimental economics classes.

The ZIP contains two instructor-friendly entry points:

- `01_instructor_pdfs/` for numbered PDFs
- `02_docs_site/index.html` for a clickable website version of the same docs

Before using it with students, please do this once on your own computer:

1. If you are starting from a blank computer, open `01_instructor_pdfs/01_install_from_scratch.pdf`.
2. Then open `01_instructor_pdfs/02_instructor_quickstart.pdf`.
3. Then open `01_instructor_pdfs/03_hosting_and_deployment.pdf`.
4. Run `./scripts/bootstrap.sh`.
5. Run `./scripts/verify.sh`.
6. Paste this into Terminal to set an admin password:

```bash
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
```

7. Paste this into Terminal to launch a local demo:

```bash
source .venv/bin/activate
otree devserver
```

8. Open the local site, log in as `admin`, and create one `live_demo` session.
9. Test the `live_demo` session in a second browser or private window.
10. If you plan to use `ngrok` or `Heroku`, test that public access path before class as well.

After that, please keep going in this order before your first real class:

1. `01_instructor_pdfs/04_identity_and_grading.pdf`
2. `01_instructor_pdfs/05_classroom_readiness.pdf`
3. `01_instructor_pdfs/06_experiment_catalog.pdf`
4. `01_instructor_pdfs/07_headcount_and_fallbacks.pdf`
5. `01_instructor_pdfs/08_instructor_runbook.pdf`
6. `01_instructor_pdfs/09_data_and_export.pdf`
7. `01_instructor_pdfs/10_troubleshooting.pdf`

What I would like you to check:

- does the project install cleanly on your machine?
- can you open the admin page and create a demo session?
- can you run one app from start to finish?
- if you will use a public URL, can a second device reach it?
- are the setup notes and classroom instructions clear enough without extra help?

If anything is confusing or fails, please tell me:

- which step failed
- what operating system you are using
- the exact error message or screenshot
- which hosting option you were trying to use

Thanks.
