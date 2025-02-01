# Library Release Instructions

## Table of Contents
1. [Overview](#1-overview)  
2. [Prerequisites & Assumptions](#2-prerequisites--assumptions)  
3. [Versioning & Branching Strategy](#3-versioning--branching-strategy)  
4. [Pre-Release Checks](#4-pre-release-checks)  
5. [Build & Test Pipeline](#5-build--test-pipeline)  
6. [Publishing / Distribution](#6-publishing--distribution)  
   - 6.1. [PyPI Publication Steps](#61-pypi-publication-steps)  
   - 6.2. [GitHub Release Process](#62-github-release-process)  
7. [Post-Release Tasks](#7-post-release-tasks)  
8. [Release Checklist Template](#8-release-checklist-template)  
9. [Troubleshooting & Common Issues](#9-troubleshooting--common-issues)  
10. [Future Enhancements](#10-future-enhancements)  

---

## 1. Overview

The **Context-Tracking Framework** is designed to be maintained with **regular releases**, each **tagged** and documented for clarity. This guide ensures that maintainers have a consistent procedure for:

- **Versioning** new changes  
- Running **tests** and verifying code quality  
- **Publishing** the library to package registries (PyPI, GitHub, etc.)  
- Updating **documentation** and **release notes**  

---

## 2. Prerequisites & Assumptions

1. **Local Environment**:
   - Python 3.8+  
   - Installed dependencies (e.g., `pytest`, `wheel`, etc.)  
2. **Access**:
   - Permissions to push tags to the **GitHub repository**.  
   - Permissions or credentials to **publish** on PyPI (if applicable).  
3. **CI/CD**:
   - A configured **CI pipeline** (GitHub Actions or similar) that runs tests, lint checks, and coverage on push or pull requests.  
4. **Documentation**:
   - The codebase must include up-to-date docstrings and reference docs.  
   - Changelog or release notes must be maintained.

---

## 3. Versioning & Branching Strategy

We follow **Semantic Versioning (SemVer)**: `MAJOR.MINOR.PATCH`.

- **MAJOR**: Breaking changes to APIs or major refactors that are not backward-compatible.  
- **MINOR**: New features added in a backward-compatible manner.  
- **PATCH**: Bug fixes or small improvements that do not affect public APIs.

**Branching**:
1. **Main Branch**: Always stable, containing the latest production-ready code.  
2. **Feature Branches**: Prefixed by `feature/` or `fix/`, merged into `main` via pull requests after review.  
3. **Release Branches** (optional): For staging release candidates if you want to finalize multiple changes at once.

---

## 4. Pre-Release Checks

Before publishing a release:

1. **Pull Latest Changes**: Ensure your local `main` is up-to-date with remote.  
2. **Check Tests**:  
   - `pytest --cov` or `make test` (depending on your dev setup)  
   - Confirm **all tests** pass and coverage remains above the threshold.  
3. **Update Version**:  
   - Bump the version in `setup.py` or `pyproject.toml` (depending on the packaging approach).  
   - Update any relevant version references in documentation.  
4. **Update Changelog** (if maintained separately):  
   - Summarize new features, bug fixes, deprecations, or breaking changes.  
5. **Review Security & Compliance**:  
   - If changes affect data storage or context keys, confirm that security notes and compliance docs remain valid.

---

## 5. Build & Test Pipeline

1. **Local Build**:  
   ```bash
   # Example using setuptools
   python setup.py sdist bdist_wheel
   ```
   or
   ```bash
   # If using poetry
   poetry build
   ```
2. **Local Installation Test**:  
   ```bash
   pip install dist/context_framework-<version>-py3-none-any.whl
   # Then run a basic import test in Python
   python -c "import context_framework; print(context_framework.__version__)"
   ```
3. **Continuous Integration**:  
   - Push changes or open a PR to trigger the CI pipeline.  
   - CI will run your **unit** + **integration** tests, **lint checks**, and **coverage**.  
   - Only proceed if everything passes.

---

## 6. Publishing / Distribution

### 6.1. PyPI Publication Steps

1. **Check PyPI Credentials**:  
   - Ensure you have an **account** on PyPI with maintain permissions to the package.  
   - Store credentials in a secure manner (e.g., environment variables or GitHub secrets).  
2. **Publish**:  
   ```bash
   # Twine is a common tool for uploading distributions
   twine upload dist/* 
   ```
   or
   ```bash
   # Poetry approach
   poetry publish --build
   ```
3. **Verify Upload**:  
   - Go to [https://pypi.org](https://pypi.org) and confirm the new version is live.  
   - Test installation from PyPI:
     ```bash
     pip install context_framework==<new_version>
     ```

### 6.2. GitHub Release Process

1. **Tag & Push**:  
   ```bash
   git tag v<version>
   git push origin v<version>
   ```
2. **Create a Release**:  
   - In the GitHub UI, go to “Releases” → “Draft a new release.”  
   - Title it `v<version>` (e.g., `v1.2.0`) and copy relevant **changelog** entries.  
   - Mark as a **pre-release** if you’re testing a release candidate.  
3. **CI Workflows** (optional):  
   - Some workflows automatically build and upload the package on creation of a tagged release.

---

## 7. Post-Release Tasks

1. **Update Documentation**:
   - If using readthedocs or a similar service, trigger a **docs build** to reflect the new version.  
   - Merge any doc changes from release branches back into `main`.  
2. **Announce Release**:  
   - Notify relevant teams, create a GitHub release note, or post in your community channels.  
3. **Monitor**:  
   - Look out for any user feedback or issues.  
   - If critical bugs emerge, prepare a **patch** release (e.g., from `1.2.0` to `1.2.1`).

---

## 8. Release Checklist Template

You can copy and paste the following **checklist** for each release:

1. **[ ]** Pull latest `main` and ensure no pending merges conflict.  
2. **[ ]** Run `pytest` (unit + integration tests) → All pass.  
3. **[ ]** Update version in `setup.py`/`pyproject.toml`: `__version__ = "<MAJOR.MINOR.PATCH>"`.  
4. **[ ]** Update **changelog** or **release notes**.  
5. **[ ]** Local build & install test.  
6. **[ ]** Commit changes, push, ensure CI passes.  
7. **[ ]** Create git tag (e.g., `v1.2.0`) and push.  
8. **[ ]** Draft GitHub release, attach notes.  
9. **[ ]** Publish package to PyPI (`twine upload ...` or `poetry publish`).  
10. **[ ]** Verify package on PyPI or test installation.  
11. **[ ]** Final docs build (if relevant).  
12. **[ ]** Announce release and monitor issues.

---

## 9. Troubleshooting & Common Issues

1. **Credentials Fail**:  
   - Confirm your `.pypirc` or environment variables are correct.  
   - Check 2FA or token-based auth if configured.  
2. **Version Conflicts**:  
   - Make sure you increment the version in `setup.py` or `pyproject.toml` *before* tagging.  
   - If you need to re-publish a corrected release, you must **delete** or **bump** the version on PyPI (PyPI does not allow overwriting the same version).  
3. **CI Fails on Tag**:  
   - Check if your CI pipeline triggers on tag pushes. Update your CI config if it doesn’t.  
4. **Incompatible Dependencies**:  
   - If dependency versions cause breakage, update your `requirements.txt` or `poetry.lock` and re-run tests.

---

## 10. Future Enhancements

- **Automated Release Pipeline**: Configure a GitHub Action that automatically tags and publishes to PyPI once a PR is merged and you confirm a release version.  
- **Changelog Automation**: Use tools like [**GitHub Release Drafter**](https://github.com/release-drafter/release-drafter) to auto-generate release notes from PR titles.  
- **Multi-Package Releases**: If you publish multiple related packages, consider a monorepo approach or a unified release script.  

---

**Conclusion**

These **library release instructions** streamline how maintainers prepare, test, and publish new versions of the Context-Tracking Framework. By following this document—especially the **checklist** and **semantic versioning** guidelines—you help ensure each release is **stable**, **traceable**, and **efficiently** deployed to users.