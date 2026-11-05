# Repository tools

- fetch_dataset.py: restore all1761 exact image files from the matching GitHub release; --verify-only checks an existing download. It uses Python's standard library.
- verify_publication_paths.py: verify portable data resolution, frozen CSV/labels and original trained checkpoint identities in the current project.
- build_image_release.py: maintainer-only construction of the bounded image ZIP assets, with source image SHA256 and ZIP CRC checks.
- build_repository_handoff.py: maintainer-only construction of the current small handoff ZIP and publication manifest, leaving machine-only teacher text extraction out of the public archive.
- build_member04_report_collection.py: collect the available member04 report sources and current figures. Historical slide render caches are optional; the final editable slides and figure copies are retained in reports/member04.
- publish_github.ps1: maintainer-only publish/resume helper. It requires a GitHub CLI login and refuses to silently replace a release asset with a different size or checksum.
- prepare_github_publication.py: one-time local migration record for the original D-drive project. It is not a normal clone/reproduction entry.

Ordinary teammates should start with the root README and PROJECT_GUIDE, download images once, and use run_project.py. All build caches and authentication configuration stay under .runtime and are ignored by Git.
