# oTree Classroom Experiments

Instructor-first oTree package for live behavioral and experimental economics classes.

This repository contains classroom-ready experiments, release assets for non-technical instructors, and the operational notes needed to run sessions reliably in person or online.

## Start Here

Use one of these entry points:

1. If you downloaded the release ZIP, open `02_docs_site/index.html` for the clickable website version or `01_instructor_pdfs/00_instructor_packet.pdf` for the single combined PDF.
2. If you are starting from a blank computer, read `01_instructor_pdfs/01_install_from_scratch.pdf` or [docs/install-from-scratch.md](docs/install-from-scratch.md).
3. Then read `01_instructor_pdfs/02_instructor_quickstart.pdf` or [INSTRUCTOR_QUICKSTART.md](INSTRUCTOR_QUICKSTART.md).
4. Before inviting students, read `01_instructor_pdfs/03_hosting_and_deployment.pdf` or [docs/hosting-and-deployment.md](docs/hosting-and-deployment.md).
5. Before your first real class, read `01_instructor_pdfs/04_identity_and_grading.pdf`, `01_instructor_pdfs/05_classroom_readiness.pdf`, `01_instructor_pdfs/06_experiment_catalog.pdf`, `01_instructor_pdfs/07_headcount_and_fallbacks.pdf`, and `01_instructor_pdfs/08_instructor_runbook.pdf`.

If you are a non-technical instructor, use the packaged release ZIP from GitHub Releases rather than browsing the repo directly.

## Package Layout

- `01_instructor_pdfs/`: numbered instructor PDFs in the recommended reading order.
- `02_docs_site/`: clickable static website version of the same instructor docs.
- `_rooms/`: participant label files.
- `settings.py`: session catalog and room setup.

## Install And Verify

Paste this into Terminal from the project root:

```bash
./scripts/bootstrap.sh
./scripts/verify.sh
```

`bootstrap.sh` creates a project-local `.venv` and installs this project's Python packages, including oTree. `verify.sh` runs the smoke checks against that local environment.

## Release Info

- Current release version: see `VERSION`
- Release summary: see `RELEASE_NOTES.md`
- Instructor download: GitHub Releases
- Artifact checksum: `dist/SHA256SUMS.txt`

## Support

- This package is maintained by the instructor or repository owner distributing it.
- If you received a ZIP directly, contact the person who sent it to you for support.
- When reporting a problem, include your operating system, the step that failed, the exact command or error message, and whether you were using local setup, `Heroku`, or `ngrok`.
- For instructor-facing recovery steps, start with [docs/troubleshooting.md](docs/troubleshooting.md) or the matching file in `01_instructor_pdfs/`.
