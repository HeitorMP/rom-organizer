#!/usr/bin/env python3

import os
import shutil
import sys
import re
import hashlib

def display_help():
    """Displays usage instructions and details about each parameter."""
    help_text = """
ROM Organizer Script
=====================

This script helps you organize ROM files by moving them to a destination directory based on filters like "demo", "unl", "prototype", "pirate", or a specific country.

Usage:
    python script.py <source_directory> <destination_directory> [-d] [-u] [-p] [-P] [--country=<country>] [--dat=<dat_file>] [--verbose] [--help]

Options:
    <source_directory>       Directory where the ROM files are located.
    <destination_directory>  Directory where the filtered ROM files will be moved.

    -d                       Move ROMs containing "(demo)" in their filenames.
    -u                       Move ROMs containing "(unl)" or "(pirate)" in their filenames.
    -p                       Move ROMs containing "(prototype)" or "(proto)" in their filenames.
    -P                       Move ROMs containing "(pirate)" in their filenames (alternative to -u).
    --country=<country>      Move ROMs containing the specified country name in their filenames.
    --dat=<dat_file>         Filter ROMs by MD5 using the provided .dat file.
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
            # Find all MD5 hashes in the format md5 <hash>
            md5_matches = re.findall(r'md5\s+([A-F0-9]{32})', content, re.IGNORECASE)
            md5_set = set(md5_matches)
    except Exception as e:
        print(f"Erro ao ler o arquivo .dat: {e}")
        sys.exit(1)
    
    return md5_set

def get_file_md5(file_path):
    """Calculates the MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # Read the file in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
    except Exception as e:
        print(f"Erro ao calcular o MD5 do arquivo {file_path}: {e}")
        return None
    
    return hash_md5.hexdigest().upper()

def move_roms(source_dir, destination_dir, opt_dict, md5_set, verbose=False):
    """Moves or copies ROM files based on the provided filters."""
    # Check if the destination directory exists, if not, create it
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Compile regular expressions for demo, unl, prototype, and country filter
    demo_pattern = re.compile(r'\(demo\)', re.IGNORECASE) if opt_dict['d'] else None
    unl_pattern = re.compile(r'\(unl\)', re.IGNORECASE) if opt_dict['u'] else None
    pirate_pattern = re.compile(r'\(pirate\)', re.IGNORECASE) if opt_dict['P'] else None
    prototype_pattern = re.compile(r'\((?:prototype|proto)\)', re.IGNORECASE) if opt_dict['p'] else None
    country_pattern = re.compile(rf'{opt_dict["country"]}', re.IGNORECASE) if opt_dict['country'] else None

    seen = set()
    moved_count = 0

    # List files in the source directory (no subdirectories)
    for file in os.listdir(source_dir):
        file_path = os.path.join(source_dir, file)

        # Skip directories
        if not os.path.isfile(file_path):
            continue

        file_name = os.path.splitext(file)[0]  # Get the file name without extension

        # Avoid duplicated file name
        if file_name in seen:
            continue
        seen.add(file_name)

        # Assume the file should be moved, and only change to False if none of the filters match
        should_move = False

        # Check demo filter
        if demo_pattern and demo_pattern.search(file_name):
            should_move = True

        # Check unl filter
        if unl_pattern and unl_pattern.search(file_name):
            should_move = True

        # Check pirate filter
        if pirate_pattern and pirate_pattern.search(file_name):
            should_move = True

        # Check prototype filter
        if prototype_pattern and prototype_pattern.search(file_name):
            should_move = True

        # Check country filter
        if country_pattern and country_pattern.search(file_name):
            should_move = True

        # If a dat file was provided, check the MD5
        if md5_set:
            file_md5 = get_file_md5(file_path)
            if file_md5 and file_md5 in md5_set:
                should_move = True
            else:
                should_move = False

        # If the file matches at least one filter, move or copy
        if should_move:
            dest_file_path = os.path.join(destination_dir, file)
            
            # Check if the file already exists in the destination directory
            if os.path.exists(dest_file_path):
                shutil.copy(file_path, dest_file_path)
                if verbose:
                    print(f"Copied (overwritten) file: {file} to {dest_file_path}")
                os.remove(file_path)
            else:
                shutil.move(file_path, dest_file_path)
                if verbose:
                    print(f"Moved file: {file} to {dest_file_path}")

            moved_count += 1

    # Final summary
    print(f"Organization completed! Total files moved: {moved_count}")

# Main entry point of the script
if __name__ == '__main__':
    # Check if we have the correct number of arguments
    if len(sys.argv) < 4 or '--help' in sys.argv:
        display_help()
        sys.exit(0)

    # Source and destination directories
    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]

    # Define the options dictionary with default values
    opt_dict = {
        "d": False,
        "u": False,
        "p": False,
        "P": False,
        "country": None,
        "dat": None
    }

    verbose = False

    # Process the arguments
    args = sys.argv[3:]
    for arg in args:
        if arg.startswith('-') and not arg.startswith('--'):
            # Start of a filter argument, check each letter after the "-"
            for char in arg[1:]:
                if char in opt_dict:
                    opt_dict[char] = True
                else:
                    print(f"Invalid filter option: -{char}")
                    sys.exit(1)
        elif arg.startswith('--country'):
            # Extract country name from "--country=<country>"
            country = arg.split('=')[1] if '=' in arg else None
            if not country:
                print("Error: Missing country name after --country=")
                sys.exit(1)
            opt_dict["country"] = country
        elif arg.startswith('--dat'):
            # Extract .dat file path from "--dat=<dat_file>"
            dat_file = arg.split('=')[1] if '=' in arg else None
            if not dat_file or not os.path.exists(dat_file):
                print("Error: Invalid .dat file path.")
                sys.exit(1)
            opt_dict["dat"] = dat_file
        elif arg == '--verbose':
            verbose = True

    # If a .dat file was provided, get the MD5 hashes
    md5_set = set()
    if opt_dict["dat"]:
        md5_set = get_md5_from_dat(opt_dict["dat"])

    # Call the move_roms function with the appropriate parameters
    move_roms(source_dir, destination_dir, opt_dict, md5_set, verbose)
