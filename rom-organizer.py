#!/usr/bin/env python3

import os
import shutil
import sys
import re
import hashlib
import zipfile
import tempfile


def display_help():
    """Displays usage instructions and details about each parameter."""
    help_text = """
ROM Organizer Script
=====================

This script helps you organize ROM files by copying or moving them to a destination directory based on filters like "demo", "unl", "prototype", "pirate", or a specific country.

Usage:
    python script.py <source_directory> <destination_directory> [-d] [-u] [-p] [-P] [--country=<country>] [--dat=<dat_file>] [--move] [--verbose] [--help]

Options:
    <source_directory>       Directory where the ROM files are located.
    <destination_directory>  Directory where the filtered ROM files will be copied or moved.

    -d                       Process ROMs containing "(demo)" in their filenames.
    -u                       Process ROMs containing "(unl)" or "(pirate)" in their filenames.
    -p                       Process ROMs containing "(prototype)" or "(proto)" in their filenames.
    -P                       Process ROMs containing "(pirate)" in their filenames (alternative to -u).
    --country=<country>      Process ROMs containing the specified country name in their filenames.
    --dat=<dat_file>         Filter ROMs by MD5 using the provided .dat file.
                             If the file is a .zip, it will be temporarily extracted for MD5 checking.
    --move                   Move files instead of copying them. If this flag is omitted, files will be copied.
    --verbose                Print detailed logs of the operations being performed.
    --help                   Display this help message and exit.
"""
    print(help_text)


def get_md5_from_dat(dat_file):
    """Reads a .dat file and returns a set of MD5 hashes from the ROM entries."""
    md5_set = set()
    try:
        with open(dat_file, 'r', encoding='utf-8') as f:
            content = f.read()

            md5_matches = re.findall(r'md5\s+([A-F0-9]{32})', content, re.IGNORECASE)
            md5_set = set(md5_matches)
    except Exception as e:
        print(f"Error reading the .dat file: {e}")
        sys.exit(1)

    return md5_set


def get_file_md5(file_path):
    """Calculates the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        print(f"Error calculating MD5 of the file {file_path}: {e}")
        return None

    return hash_md5.hexdigest().upper()


def process_zip_file(zip_path, md5_set, verbose):
    """Processes a zip file by extracting, checking MD5s, and re-zipping if necessary."""
    temp_dir = tempfile.mkdtemp()

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Check extracted files against the MD5 set
        matched = False
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                file_md5 = get_file_md5(file_path)
                if file_md5 and file_md5 in md5_set:
                    matched = True
                    if verbose:
                        print(f"Matched MD5 for file inside zip: {file}")
                    break

        # Re-zip the content back
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, temp_dir)
                    zip_ref.write(full_path, arcname)

        return matched
    finally:
        shutil.rmtree(temp_dir)


def process_roms(source_dir, destination_dir, opt_dict, md5_set, move_files, verbose=False):
    """Copies or moves ROM files based on the provided filters."""
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # RE
    demo_pattern = re.compile(r'\(demo\)', re.IGNORECASE) if opt_dict['d'] else None
    unl_pattern = re.compile(r'\(unl\)', re.IGNORECASE) if opt_dict['u'] else None
    pirate_pattern = re.compile(r'\(pirate\)', re.IGNORECASE) if opt_dict['P'] else None
    prototype_pattern = re.compile(r'\((?:prototype|proto)\)', re.IGNORECASE) if opt_dict['p'] else None
    country_pattern = re.compile(rf'{opt_dict["country"]}', re.IGNORECASE) if opt_dict['country'] else None

    seen = set()
    processed_count = 0

    for file in os.listdir(source_dir):
        file_path = os.path.join(source_dir, file)

        if not os.path.isfile(file_path):
            continue

        file_name = os.path.splitext(file)[0]  # Get the file name without extension

        if file_name in seen:
            continue
        seen.add(file_name)

        should_process = False

        if demo_pattern and demo_pattern.search(file_name):
            should_process = True

        if unl_pattern and unl_pattern.search(file_name):
            should_process = True

        if pirate_pattern and pirate_pattern.search(file_name):
            should_process = True

        if prototype_pattern and prototype_pattern.search(file_name):
            should_process = True

        if country_pattern and country_pattern.search(file_name):
            should_process = True

        # DAT file filtering
        if md5_set:
            if file.lower().endswith('.zip'):
                if process_zip_file(file_path, md5_set, verbose):
                    should_process = True
            else:
                file_md5 = get_file_md5(file_path)
                if file_md5 and file_md5 in md5_set:
                    should_process = True
                else:
                    should_process = False

        if should_process:
            dest_file_path = os.path.join(destination_dir, file)

            # Move or copy file
            if move_files:
                if os.path.exists(dest_file_path):
                    shutil.copy(file_path, dest_file_path)
                    if verbose:
                        print(f"Copied (overwritten) file: {file} to {dest_file_path}")
                    os.remove(file_path)
                else:
                    shutil.move(file_path, dest_file_path)
                    if verbose:
                        print(f"Moved file: {file} to {dest_file_path}")
            else:
                shutil.copy(file_path, dest_file_path)
                if verbose:
                    print(f"Copied file: {file} to {dest_file_path}")

            processed_count += 1

    print(f"Organization completed! Total files processed: {processed_count}")


# Main entry point of the script
if __name__ == '__main__':
    if len(sys.argv) < 4 or '--help' in sys.argv:
        display_help()
        sys.exit(0)

    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]

    opt_dict = {
        "d": False,
        "u": False,
        "p": False,
        "P": False,
        "country": None,
        "dat": None
    }

    verbose = False
    move_files = False

    args = sys.argv[3:]
    for arg in args:
        if arg.startswith('-') and not arg.startswith('--'):
            for char in arg[1:]:
                if char in opt_dict:
                    opt_dict[char] = True
                else:
                    print(f"Invalid filter option: -{char}")
                    sys.exit(1)
        elif arg.startswith('--country'):
            country = arg.split('=')[1] if '=' in arg else None
            if not country:
                print("Error: Missing country name after --country=")
                sys.exit(1)
            opt_dict["country"] = country
        elif arg.startswith('--dat'):
            dat_file = arg.split('=')[1] if '=' in arg else None
            if not dat_file or not os.path.exists(dat_file):
                print("Error: Invalid .dat file path.")
                sys.exit(1)
            opt_dict["dat"] = dat_file
        elif arg == '--verbose':
            verbose = True
        elif arg == '--move':
            move_files = True

    # If a .dat file was provided, get the MD5 hashes
    md5_set = set()
    if opt_dict["dat"]:
        md5_set = get_md5_from_dat(opt_dict["dat"])

    process_roms(source_dir, destination_dir, opt_dict, md5_set, move_files, verbose)
