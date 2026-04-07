# Instructor Feedback Log

This file records the instructor-facing issues raised during review, the intended fix, and whether the issue now has a recurring release check.

## Packaging and Reading Order

- Number the PDF folder and PDF files so they sort in reading order.
  - Status: implemented via `01_instructor_pdfs/` and numbered PDF filenames.
  - Release check: `scripts/audit_instructor_docs.py`
- Keep reading order consistent across quick start, onboarding email, package layout, and website.
  - Status: implemented through the canonical manifest in `docs/instructor-docs-manifest.tsv`.
  - Release check: `scripts/audit_instructor_docs.py`
- Add a clickable website version as a backup to the PDFs.
  - Status: implemented via `scripts/build_instructor_site.sh` and `02_docs_site/`.
  - Release check: package build and site build
- Standardize the packaged website folder name across docs, scripts, and release assets.
  - Status: implemented with `02_docs_site/` as the single package name.
  - Release check: `scripts/audit_instructor_docs.py` plus `scripts/verify_instructor_package.py`
- Keep internal maintainer files out of the instructor ZIP.
  - Status: implemented by excluding contributor/internal docs from `scripts/make_instructor_package.sh`.
  - Release check: `scripts/verify_instructor_package.py`

## Install and Hosting Clarity

- Clarify that `bootstrap.sh` installs oTree locally.
  - Status: implemented in `docs/install-from-scratch.md` and `INSTRUCTOR_QUICKSTART.md`.
  - Release check: `scripts/audit_instructor_docs.py`
- Replace raw Markdown references in “What To Read Next” with numbered PDFs or website guidance.
  - Status: implemented.
  - Release check: `scripts/audit_instructor_docs.py`
- Mention Heroku student-credit possibility but warn that instructors should not assume eligibility.
  - Status: implemented in `docs/hosting-and-deployment.md`.
  - Release check: `scripts/audit_instructor_docs.py`
- Explain what `Procfile` is.
  - Status: implemented in `docs/hosting-and-deployment.md`.
  - Release check: `scripts/audit_instructor_docs.py`
- Give a clearer demo-run walkthrough.
  - Status: implemented in install and hosting docs.
  - Release check: manual doc review plus PDF/site build

## Layout and Presentation

- Replace wide instructor-facing tables that do not fit on the page.
  - Status: implemented for identity, catalog, headcount, and troubleshooting docs.
  - Release check: `scripts/audit_instructor_docs.py` bans Markdown tables in instructor docs
- Remove internal planning or maintainer-only notes from instructor-facing docs.
  - Status: implemented by removing `Planning Notes` and `When To Escalate`.
  - Release check: `scripts/audit_instructor_docs.py`
- Retire `docs/classroom-playbooks.md` from the instructor packet.
  - Status: implemented.
  - Release check: `scripts/audit_instructor_docs.py`

## Command Explainability

- Explain instructor-facing terminal commands in plain language.
  - Status: implemented around room-label and quarter-earnings commands, plus bootstrap, verify, and startup commands.
  - Release check: `scripts/audit_instructor_docs.py`
- Reformat long commands so they do not wrap badly in PDFs.
  - Status: implemented with multiline command blocks.
  - Release check: PDF build plus doc audit

## Headcount and Classroom Operations

- Document which apps are resilient and which still need exact multiples.
  - Status: implemented in `docs/headcount-and-fallbacks.md` with machine-readable backing data in `docs/project/headcount-matrix.tsv`.
  - Release check: `scripts/audit_headcount_matrix.py`
- Add safer classroom options for beauty contest and public goods.
  - Status: implemented through `guess_two_thirds_classroom` and `public_goods_flexible`.
  - Release check: app tests and session verification
- Track the remaining uneven-headcount redesign opportunities in one machine-readable backlog.
  - Status: implemented in `docs/project/headcount-flexibility-backlog.tsv`.
  - Release check: contributor review when new flexible modes are added
