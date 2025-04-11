#!/usr/bin/env python3
import os
import fnmatch # For filename pattern matching

# --- Configuration ---
CONFIG_FILENAME = ".code_collector_ignore"
OUTPUT_FILENAME = "collected_code.txt"
ROOT_DIR = "."  # Run from the current directory

# Default ignored folders (case-sensitive on Linux/macOS, insensitive on Windows often)
# Using lowercase for broader matching potential if needed later, but direct comparison is fine for now.
DEFAULT_IGNORED_FOLDERS = {
    "node_modules",
    "build",
    "dist",
    "public",
    "static",
    "vendor",
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    ".git",
    ".svn",
    ".hg",
    ".vscode",
    ".idea",
    "target", # Common for Java/Rust
    "out",    # Common for various builds
    "bin",    # Often contains compiled binaries, not source
    "obj",    # Often contains intermediate compile objects
    "logs",
    "tmp",
    "temp",
    "coverage",
}

# Default ignored filename patterns (using glob syntax, case-insensitive matching)
# Includes common media, archives, config, data, lock files, specific config patterns etc.
DEFAULT_IGNORED_PATTERNS = {
    # --- Requested ---
    "*.config.js",
    "*.config.ts",
    # --- Media ---
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.svg", "*.tif", "*.tiff",
    "*.mp4", "*.mkv", "*.avi", "*.mov", "*.wmv", "*.flv",
    "*.mp3", "*.wav", "*.ogg", "*.flac", "*.aac",
    "*.webp", "*.ico",
    # --- Archives ---
    "*.zip", "*.tar", "*.gz", "*.bz2", "*.rar", "*.7z",
    "*.whl",
    # --- Config / Data / Lock files ---
    "*.json", "*.yaml", "*.yml", "*.toml", "*.ini", "*.cfg", ".conf", # .conf might be too broad? keep for now
    "*.xml", "*.csv", "*.tsv",
    "*.lock", "yarn.lock", "package-lock.json", "composer.lock", "poetry.lock",
    ".gitignore", ".gitattributes", ".gitmodules",
    ".env", ".env.example", ".env.*",
    ".prettierrc", ".prettierignore",
    # --- Compiled / Object / Binary / Libs ---
    "*.pyc", "*.pyo",
    "*.class", "*.jar",
    "*.o", "*.so", "*.dll", "*.a", "*.lib",
    "*.exe", "*.app", "*.dmg", "*.pkg",
    "*.pdf", "*.doc", "*.docx", "*.xls", "*.xlsx", "*.ppt", ".pptx", "*.odt", "*.ods", "*.odp",
    "*.wasm",
    # --- Database ---
    "*.db", "*.sqlite", "*.sqlite3", "*.sql",
    # --- Other common non-code / temp ---
    "*.log",
    "*.tmp", "*.temp",
    "*.bak", "*.swp", "*.swo", "*~", # Editor backup/swap files
    "*.md", # Often documentation, could be included if desired by removing this
    "*.markdown",
    "*.ipynb", # Jupyter notebooks have a specific format, often not plain code
    # --- Fonts ---
     "*.otf",
    # --- Typescript ---
     "*.d.ts",
}
# --- End Configuration ---

def load_ignore_config(config_path, default_folders, default_patterns):
    """Loads ignore patterns from a config file, combining with defaults."""
    ignored_folders = set(default_folders)
    ignored_patterns = set(p.lower() for p in default_patterns) # Store lowercase

    if not os.path.exists(config_path):
        print(f"Info: Config file '{config_path}' not found. Using default ignore lists.")
        return ignored_folders, ignored_patterns

    print(f"Info: Loading ignore configuration from '{config_path}'...")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            current_section = None
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue # Skip empty lines and comments

                if line.lower() == '[folders]':
                    current_section = 'folders'
                    continue
                elif line.lower() == '[patterns]': # Changed from [EXTENSIONS] to [PATTERNS]
                    current_section = 'patterns'
                    continue
                elif line.startswith('[') and line.endswith(']'):
                    # Handle unknown sections if needed, or just ignore
                    print(f"  Warning: Unknown section '{line}' in config file at line {line_num}. Ignoring.")
                    current_section = None # Stop adding to previous section
                    continue


                if current_section == 'folders':
                    ignored_folders.add(line)
                    # print(f"  Ignoring folder: {line}") # Optional debug print
                elif current_section == 'patterns':
                    ignored_patterns.add(line.lower())
                    # print(f"  Ignoring pattern: {line.lower()}") # Optional debug print
                # else: No current section, ignore line unless it's a section header


    except IOError as e:
        print(f"Warning: Could not read config file '{config_path}': {e}. Using defaults.")
        return set(default_folders), set(p.lower() for p in default_patterns) # Revert to defaults on error

    print("Info: Ignore configuration loaded successfully.")
    return ignored_folders, ignored_patterns

def is_ignored(filename, ignored_patterns):
    """Check if a filename matches any of the ignored patterns (case-insensitive)."""
    filename_lower = filename.lower()
    for pattern in ignored_patterns:
        if fnmatch.fnmatch(filename_lower, pattern):
            return True
    return False

def collect_code(root_dir, output_file, ignored_folders, ignored_patterns):
    """Traverses directories, reads code files, and appends to the output file."""
    collected_count = 0
    abs_root_dir = os.path.abspath(root_dir)
    # Get the name of the directory the script is running in
    root_folder_name = os.path.basename(abs_root_dir)

    # Handle edge case where script is run from filesystem root (e.g., '/')
    # In this case, os.path.basename might return '' or '/', we might not want a leading '/' or empty segment
    if not root_folder_name and abs_root_dir == os.path.abspath(os.sep):
         root_folder_name = '' # Avoid double slashes later if joining with path starting with /
         print("Info: Running from filesystem root. Paths will not be prefixed.")
    elif not root_folder_name:
         # Should not happen often, but handle potential empty basename from '.'
         root_folder_name = '.' # Use '.' explicitly if basename is empty but not root
         print("Warning: Could not determine root folder name reliably, using '.' as prefix.")


    print(f"Starting code collection from: '{abs_root_dir}'")
    print(f"Output will be saved to: '{output_file}'")
    print(f"Path prefix in output file: '{root_folder_name}/' (if applicable)") # Inform user
    print("-" * 70)
    print("Ignored Folders:", ", ".join(sorted(list(ignored_folders))) if ignored_folders else "None")
    print("Ignored Patterns:", ", ".join(sorted(list(ignored_patterns))) if ignored_patterns else "None")
    print("-" * 70)


    try:
        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Use abs_root_dir for traversal start to ensure relpath works correctly even if root_dir='.'
            for current_dir, dirs, files in os.walk(abs_root_dir, topdown=True):
                # --- Folder Exclusion ---
                # Compare basenames for exclusion
                dirs[:] = [d for d in dirs if os.path.basename(d) not in ignored_folders]

                # --- Current Directory Check ---
                # Need to check if the *current directory itself* should be skipped.
                # We need to compare the *name* of the directory being entered.
                # os.walk yields the *path* to the directory (current_dir).
                current_dir_basename = os.path.basename(current_dir)
                # Avoid skipping the root folder itself based on its name if it's the starting point
                if current_dir != abs_root_dir and current_dir_basename in ignored_folders:
                    # If we skip here, os.walk won't descend further, but modifying dirs[:]
                    # is the primary mechanism for pruning *before* descending.
                    # This adds an extra layer but might be redundant if dirs[:] works perfectly.
                    # print(f"Skipping traversal into ignored directory: {os.path.relpath(current_dir, abs_root_dir)}")
                    continue


                for filename in files:
                    # --- File Exclusion ---
                    file_path = os.path.join(current_dir, filename)
                    # Calculate path relative to the *absolute* root directory now
                    relative_path = os.path.relpath(file_path, abs_root_dir)

                    # --- Construct the Desired Output Path ---
                    # Prepend the root folder's name to the relative path
                    # os.path.join handles cases where relative_path might be '.' or just the filename
                    if root_folder_name and root_folder_name != '.':
                        output_display_path = os.path.join(root_folder_name, relative_path)
                    else:
                         # If root_folder_name is empty (e.g. running from '/') or '.', just use relative path
                         output_display_path = relative_path

                    # Ensure consistent forward slashes for output
                    output_display_path = output_display_path.replace(os.sep, '/')

                    # --- Ignore self/config/output files ---
                    # Check absolute paths to be safe
                    abs_file_path = os.path.abspath(file_path)
                    if abs_file_path == os.path.abspath(os.path.join(ROOT_DIR, CONFIG_FILENAME)) or \
                       abs_file_path == os.path.abspath(__file__) or \
                       abs_file_path == os.path.abspath(OUTPUT_FILENAME) :
                        continue

                    # Check ignored patterns (using the base filename)
                    if is_ignored(filename, ignored_patterns):
                        # print(f"Skipping ignored pattern match: {output_display_path}") # Debug
                        continue

                    # --- File Processing ---
                    print(f"Processing: {output_display_path}") # Use the new path for logging too
                    try:
                        content = None
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='strict') as infile:
                                content = infile.read()
                        except UnicodeDecodeError:
                            try:
                                print(f"  Warning: Could not decode {output_display_path} as UTF-8. Trying latin-1...")
                                with open(file_path, 'r', encoding='latin-1', errors='ignore') as infile:
                                     content = infile.read()
                            except Exception as inner_e:
                                print(f"  Error reading file {output_display_path} even with fallback: {inner_e}")
                                content = f"[Error reading file content: {inner_e}]"
                        except Exception as e: # Catch other file reading errors (permissions etc.)
                             print(f"  Error reading file {output_display_path}: {e}")
                             content = f"[Error reading file: {e}]"


                        outfile.write("=" * 70 + "\n")
                        # Use the NEW output_display_path here
                        outfile.write(f"File: {output_display_path}\n")
                        outfile.write("=" * 70 + "\n")
                        outfile.write(content if content is not None else "[Error: Could not read file content]")
                        if content is not None and not content.endswith('\n'):
                             outfile.write("\n")
                        outfile.write("\n")
                        collected_count += 1

                    except Exception as e:
                        print(f"  Unexpected error processing file {output_display_path}: {e}")
                        try:
                            outfile.write("=" * 70 + "\n")
                            outfile.write(f"File: {output_display_path}\n")
                            outfile.write("=" * 70 + "\n")
                            outfile.write(f"[Unexpected error during processing: {e}]\n\n")
                        except Exception:
                             print(f"  Critical: Failed to write error message for {output_display_path} to output file.")


    except IOError as e:
        print(f"\nError: Could not open output file '{output_file}' for writing: {e}")
        return False
    except Exception as e:
        print(f"\nAn unexpected error occurred during traversal: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("-" * 70)
    print(f"Finished! Collected code from {collected_count} files into '{output_file}'.")
    return True

if __name__ == "__main__":
    ignored_folders, ignored_patterns = load_ignore_config(
        os.path.join(ROOT_DIR, CONFIG_FILENAME),
        DEFAULT_IGNORED_FOLDERS,
        DEFAULT_IGNORED_PATTERNS
    )

    collect_code(ROOT_DIR, OUTPUT_FILENAME, ignored_folders, ignored_patterns)