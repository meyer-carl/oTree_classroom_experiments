Subject: Please test the oTree classroom experiments before first use

Hi all,

I am sharing an instructor-ready oTree classroom experiment bundle for live behavioral and experimental economics classes.

The attached ZIP file contains the project plus a folder called `instructor_pdfs` with the main PDFs.

Before using it with students, please do this once on your own computer:

1. If you are starting from a blank computer, open `docs/install-from-scratch.md` or `instructor_pdfs/install_from_scratch.pdf`.
2. Then open `INSTRUCTOR_QUICKSTART.md` or `instructor_pdfs/instructor_quickstart.pdf`.
3. Decide how students will connect by opening `docs/hosting-and-deployment.md` or `instructor_pdfs/hosting_and_deployment.pdf`.
4. Run `./scripts/bootstrap.sh`.
5. Run `./scripts/verify.sh`.
6. Set an admin password:

```bash
export OTREE_ADMIN_PASSWORD='choose-a-strong-password'
```

7. Launch a local demo:

```bash
source .venv/bin/activate
otree devserver
```

8. Open the local site, log in as `admin`, and create one `live_demo` session.
9. Test the `live_demo` session in a second browser or private window.
10. If you plan to use ngrok or Heroku, test that public access path before class as well.

After that, please look at these three documents before your first real class:

- `instructor_pdfs/instructor_runbook.pdf`
- `instructor_pdfs/headcount_and_fallbacks.pdf`
- `instructor_pdfs/hosting_and_deployment.pdf`

What I would like you to check:

- Does the project install cleanly on your machine?
- Can you open the admin page and create a demo session?
- Can you run one app from start to finish?
- If you will use a public URL, can a second device reach it?
- Are the setup notes and classroom instructions clear enough without extra help?

If anything is confusing or fails, please tell me:

- which step failed
- what operating system you are using
- the exact error message or screenshot
- which hosting option you were trying to use

Thanks.
