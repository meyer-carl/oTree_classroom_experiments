# Release Notes

## Version 2026.04.01

This is the current instructor-distribution release of the oTree classroom experiment bundle.

## What This Release Includes

- 31 oTree apps covering the classroom experiment catalog
- 35 tested session configs, including classroom bundles and preference modules
- instructor-facing Markdown docs plus packaged PDFs under `01_instructor_pdfs/`
- a clickable packaged website under `02_docs_site/`
- blank-computer setup guidance in `docs/install-from-scratch.md`
- hosting guidance for `Heroku`, `ngrok`, and advanced `Ubuntu/Linux server` setups
- headcount compatibility guidance, identity/grading workflow notes, and classroom troubleshooting docs

## Validation Completed For This Release

- package built successfully with `./scripts/make_instructor_package.sh`
- instructor PDFs built successfully with `./scripts/build_instructor_pdfs.sh`
- repo preflight checks passed with `./scripts/run_preflight.sh`
- clean extracted package test passed:
  - `./scripts/bootstrap.sh`
  - `./scripts/verify.sh`

## Recommended Recipient Checks

Ask each instructor to do these before first classroom use:

1. follow `docs/install-from-scratch.md` if starting from a blank machine
2. run `./scripts/bootstrap.sh`
3. run `./scripts/verify.sh`
4. launch `otree devserver`
5. create one `live_demo` session
6. test the chosen public access method before class

## Known Practical Limits

- local setup is documented most directly for Mac and Linux; Windows users are encouraged to prefer `Heroku`
- `ngrok` is viable for small classes but depends on the instructor laptop and network staying up
- multiplayer apps still have real headcount constraints; check `docs/headcount-and-fallbacks.md` before class
- a live browser/admin dry run is still recommended before using the package with students

## Integrity Check

If you distribute the packaged ZIP, send `SHA256SUMS.txt` with it so recipients can verify that the archive matches the released artifact.
