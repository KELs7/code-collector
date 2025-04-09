# Code Collector

A simple Python script that recursively traverse a project directory, collect source code, and concatenate them into a single output file. This is particularly useful for:

*   Consolidating code for analysis.
*   Creating a snapshot of project code for documentation.
*   Providing context to Large Language Models (LLMs) by feeding them relevant parts of a codebase in one go.

## Features

*   **Recursive Traversal:** Scans all subdirectories starting from the root where the script is run.
*   **Customizable Ignore Lists:** Uses a simple `.code_collector_ignore` configuration file to specify folders and filename patterns to exclude.
*   **Sensible Defaults:** Comes with built-in defaults to ignore common non-code files (media, archives, configs) and folders (build artifacts, `node_modules`, `.git`, etc.).
*   **Clear Output Format:** Separates content from different files with clear headers indicating the file path.
*   **Encoding Fallback:** Tries to read files as UTF-8 and falls back to latin-1 to handle a wider range of text files.
*   **No External Dependencies:** Uses only Python's standard library (`os`, `fnmatch`).

## Prerequisites

*   Python 3.6 or later.

## Installation

1.  Download or copy the `collect_code.py` script.
2.  Place the `collect_code.py` script in the **root directory** of the project you want to scan.

## Usage

1.  Open your terminal or command prompt.
2.  Navigate (`cd`) to the root directory of your project (where you placed `collect_code.py`).
3.  Run the script:
    ```bash
    python collect_code.py
    ```
    or if you use `python3`:
    ```bash
    python3 collect_code.py
    ```
4.  The script will traverse the directory, process the files, and create (or overwrite) a file named `collected_code.txt` in the same root directory. Progress messages will be printed to the console.

## Configuration

You can customize which folders and files are ignored by creating a file named `.code_collector_ignore` in the **same root directory** as the script. You can use the `.code_collector_ignore` file already provided in the repo. If this file is not present, the script will use its built-in default ignore lists.

**`.code_collector_ignore` File Format:**

*   Lines starting with `#` are treated as comments and ignored.
*   Empty lines are ignored.
*   The file is divided into sections denoted by `[SECTION_NAME]` (case-insensitive).
*   Currently supported sections are `[FOLDERS]` and `[PATTERNS]`.

**`[FOLDERS]` Section:**
*   List the **names** (not full paths) of directories you want to completely ignore. The script will not descend into these folders.
*   One folder name per line.

**`[PATTERNS]` Section:**
*   List filename patterns (using [glob syntax](https://docs.python.org/3/library/fnmatch.html)) to ignore.
*   Patterns are matched against the filename (case-insensitively).
*   One pattern per line.
*   Examples:
    *   `*.log` (ignore all files ending in `.log`)
    *   `temp_*.txt` (ignore text files starting with `temp_`)
    *   `.env` (ignore specific files named `.env`)
    *   `*.config.js` (ignore JavaScript config files following a pattern)
    *   `Makefile` (ignore a specific file named Makefile)