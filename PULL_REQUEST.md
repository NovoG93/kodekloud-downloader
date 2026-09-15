# PR Title

`feat: modernize auth to Firebase tokens, add resource downloads, zero-padded module & lesson indexing, and expand test suite`

---

# PR Description

## Summary

KodeKloud has migrated its authentication architecture from legacy server-side session cookies (`session-cookie`) to Firebase Authentication stored in client-side IndexedDB (`firebaseLocalStorageDb`). Furthermore, the modern Next.js platform serves article notes, presentation slides, and downloadable resources via REST APIs rather than legacy WordPress LearnDash HTML templates.

This PR:
1. **Modernizes Authentication**: Adds direct Firebase ID token input (`--token` / `-t`) and automated headless session-cookie exchange via Playwright.
2. **Global Sequential & Zero-Padded Indexing**:
   - Numbers lessons with 3-digit zero-padding continuously across the entire course (`001 - <lesson-name>`, `002 - ...`) rather than restarting at `1` inside every module folder.
   - Numbers module directories with 2-digit zero-padding (`01 - <module-name>`, `02 - ...`) to ensure clean alphabetical and chronological sorting.
3. **Adds Resource & Article Downloads**: Downloads course presentation decks, study guides, PDFs, slides, and archive attachments (with automatic GitHub blob URL normalization to raw content), while saving lesson reading materials and notes as clean Markdown files (`.md`).
4. **TUI Course Search & Instructor Visibility**: Adds an "Instructor" column to the course selection table, supports interactive keyword filtering directly in the prompt, and introduces the `--search` / `-s` CLI flag for `kodekloud dl`.
5. **Fixes Downloader Bugs**: Solves subtitle overwrites, path shortening bugs, CLI argument forwarding, and quiz question ordering races.
6. **Expands Test Suite**: Adds 42 automated tests across 6 test modules, taking test coverage from 1% to over 60%.
7. **Modernizes Google Colab Notebook**: Adds token prompts, browser exchange, and batch MP3 audio conversion.


---

## Key Changes

### 1. Zero-Padded & Sequential File/Folder Indexing
- **2-Digit Zero-Padded Modules**: Updated [`create_file_path`](src/kodekloud_downloader/main.py) to format module directories as `f"{module_index:02d} - {module_name}"` (`01`, `02`, ..., `10`).
- **Continuous Lesson Counter**: Modified [`download_course`](src/kodekloud_downloader/main.py) to maintain a single continuous lesson counter across all modules so tracks stay sequentially ordered in operating systems and media players.
- **3-Digit Zero-Padded Lessons**: Formatted all lesson filenames with leading zeros (`f"{lesson_index:03d} - {lesson_name}"`), eliminating sorting bugs in file explorers and cloud storage.

### 2. Course Resources & Article Downloads
- **REST API Integration**: Updated [`main.py`](src/kodekloud_downloader/main.py) to fetch lesson content directly from `https://learn-api.kodekloud.com/api/lessons/{lesson.id}` instead of trying to scrape legacy WordPress `div.learndash_content_wrap` elements.
- **Resource Extraction & Download**: Added [`download_all_resources`](src/kodekloud_downloader/helpers.py) to parse Markdown links and URLs for downloadable course materials (`.pdf`, `.zip`, `.tar.gz`, `.pptx`, `.docx`, `.xlsx`, `.yaml`, etc.), streaming and saving them directly into the module folder alongside the videos.
- **Markdown Notes**: Automatically saves all article lessons (study guides, lecture notes, external references) as `{lesson_name}.md`.
- **Deduplication**: Automatically detects and skips already-downloaded resources to avoid redundant downloads.

### 3. Authentication Modernization
- **Direct Token Input (`--token` / `-t`)**: Added CLI option allowing users to supply their Firebase ID token directly (`kodekloud dl -t <JWT>`).
- **Automated Cookie Exchange**: Added headless Playwright automation ([`browser.py`](src/kodekloud_downloader/browser.py)) that takes exported cookies containing `_secure-user-session`, boots headless Chromium, and extracts `stsTokenManager.accessToken` from IndexedDB.
- **Optional Browser Extra**: Added `[browser]` extra to `pyproject.toml` (`playwright>=1.40.0`).

### 4. Core Bug Fixes
- **CLI Argument Forwarding ([`cli.py`](src/kodekloud_downloader/cli.py))**: Fixed bug where `--cookie` parameter was parsed but never passed to the `KodeKloud` instance.
- **Subtitle Collisions ([`helpers.py`](src/kodekloud_downloader/helpers.py))**: Fixed filename collision when multiple subtitle streams are extracted.
- **Path Shortening ([`main.py`](src/kodekloud_downloader/main.py))**: Fixed path truncation bug that corrupted directory paths.
- **Quiz Ordering ([`models/quiz.py`](src/kodekloud_downloader/models/quiz.py))**: Ensured quiz questions maintain sequential ordering and avoid dictionary/set ordering races.

### 5. Google Colab Notebook Overhaul ([`colab_notebook.ipynb`](colab_notebook.ipynb))
- **Direct Token Prompt**: Added an interactive masked prompt using `getpass.getpass()` for fast downloads without file uploads.
- **Automated Cookie Exchange**: Added cell for uploading `cookies.txt` with automated Chromium setup.
- **Fast Startup**: Removed slow `!sudo apt update && sudo apt upgrade` calls (FFmpeg is pre-installed in Colab).
- **Batch MP3 Conversion**: Added post-processing cell that scans downloaded videos, zero-pads track numbering (`01 - ...`), and exports MP3 audio tracks via `ffmpeg`.

### 6. Course Search & Instructor Visibility
- **Instructor Column**: Added "Instructor" to course selection table so authors and tutors are immediately visible.
- **Interactive Search / Filtering**: Users can type search keywords directly in the course selection prompt to filter the table.
- **CLI Search Flag**: Added `--search` / `-s` flag to `kodekloud dl`.
- **GitHub Raw Normalization**: Converts GitHub blob URLs to raw file URLs to ensure valid binary downloads.

### 7. Test Suite Expansion
- Added **42 automated tests** across 6 test modules:
  - `tests/test_main.py`: Module zero-padding (`01 - ...`), global cross-module sequential indexing (`001 - ...`), path shortening, 401 error handling.
  - `tests/test_helpers.py`: Table rendering with instructors, interactive search/filter, resource extraction (Markdown & bare URLs), GitHub blob URL rewriting, streaming downloads, subtitle handling, filename sanitization.
  - `tests/test_cli.py`: CLI flags (`--token`, `--cookie`, `--search`, help, error handling).
  - `tests/test_auth_exchange.py`: Headless cookie-to-token exchange.
  - `tests/test_models.py`: Quiz question ordering.
  - `tests/test_kodekloud_dl.py`: Integration smoke tests.

---

## Verification & Testing

All quality checks and tests pass cleanly across Python 3.10–3.14:

```bash
uv run ruff check src tests
# All checks passed!

uv run ruff format --check src tests
# 18 files already formatted

uv run mypy src
# Success: no issues found in 11 source files

uv run pytest
# ================= 42 passed in 8.27s =================
```

