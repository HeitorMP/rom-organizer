#!/usr/bin/env python3

import os
import shutil
import sys
import re
import hashlib
import zipfile
import tempfile
import requests
import json
import time


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


# SUA API KEY DO RETROACHIEVEMENTS
RETRO_ACHIEVEMENTS_API_KEY = os.getenv("RETRO_ACHIEVEMENTS_API_KEY")
RETRO_ACHIEVEMENTS_BASE_URL_GAMES = "https://retroachievements.org/API/API_GetGameList.php"
RETRO_ACHIEVEMENTS_BASE_URL_SYSTEM = "https://retroachievements.org/API/API_GetConsoleIDs.php"


def is_file_expired (path):
    """Checks if the file is expired (24 hours)."""
    if os.path.exists(path):
        file_time = os.path.getmtime(path)
        current_time = time.time()
        return current_time - file_time > 86400
    else:
        return True

def get_RA_console_ids():
    """ Generates a list of consoles.
        Creates a file with the list of consoles if it doesn't exist or is expired.
    """
    consoles = None

    if not is_file_expired(".consoles.json"):
        print("File is not expired")
        with open(".consoles.json", "r") as file:
            consoles = json.load(file)
    else:
        url = f"{RETRO_ACHIEVEMENTS_BASE_URL_SYSTEM}?y={RETRO_ACHIEVEMENTS_API_KEY}&a=1&g=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            consoles = response.json()
            with open(".consoles.json", "w") as file:
                json.dump(consoles, file)
        except requests.RequestException as e:
            print(f"Error to get information from API RetroAchievements: {e}")

    return consoles

def parsing_RA_console_ids(name):
    """ Returns the ID of a console based on its name. """
    consoles = get_RA_console_ids()
    for console in consoles:
        if console["Name"] == name:
            return console["ID"]

    return None

def get_RA_game_info(console_id):
    """ Generates a list of games for a specific console ID.
        Creates a file with the list of games if it doesn't exist or is expired.
    """
    games = None

    if not is_file_expired(f".{console_id}.json"):
        print("File is not expired")
        with open(f".{console_id}.json", "r") as file:
            games = json.load(file)
            print("arquivo do 32x aberto")
    else:
        url = f"{RETRO_ACHIEVEMENTS_BASE_URL_GAMES}?y={RETRO_ACHIEVEMENTS_API_KEY}&i={console_id}&h=1&f=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            games = response.json()
            with open(f".{console_id}.json", "w") as file:
                json.dump(games, file)
        except requests.RequestException as e:
            print(f"Error to get information from API RetroAchievements: {e}")
    return games
    
def has_cheevos(games, game_hash):
    """ Checks if a game has achievements based on its hash. """
    print(f'game hash: {game_hash.lower()}')
    for game in games:
        if "Hashes" in game and game_hash.lower() in game["Hashes"]:
            return True
    return False


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

def calculate_md5(file_path):
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

def get_md5(file_path):
    """ Returns the MD5 hash of a file. """
    if not os.path.isfile(file_path):
        print("Error: File does not exist.")
        return None

    if file_path.lower().endswith('.zip'):
        temp_dir = tempfile.mkdtemp()
        zip_name = os.path.basename(file_path)
        extracted_file_path = None

        try:
            # Extrair o arquivo ZIP
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_names = zip_ref.namelist()
                
                if len(file_names) != 1:
                    print(f"Error: {len(file_names)}.")
                    return None

                extracted_file_path = zip_ref.extract(file_names[0], temp_dir)

            file_md5 = calculate_md5(extracted_file_path)

            new_zip_path = os.path.join(temp_dir, zip_name)
            with zipfile.ZipFile(new_zip_path, 'w', zipfile.ZIP_DEFLATED) as new_zip:
                new_zip.write(extracted_file_path, os.path.basename(extracted_file_path))

            shutil.move(new_zip_path, file_path)

            return file_md5

        except Exception as e:
            print(f"Error: {file_path}: {e}")
            return None

        finally:
            shutil.rmtree(temp_dir)
    
    return calculate_md5(file_path)

def process_roms(source_dir, destination_dir, opt_dict, md5_set, move_files, verbose=False):
    """Copies or moves ROM files based on the provided filters."""

    console_id = None
    game_hashes = None

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
            
    # RE
    demo_pattern = re.compile(r'\(demo\)', re.IGNORECASE) if opt_dict['d'] else None
    unl_pattern = re.compile(r'\(unl\)', re.IGNORECASE) if opt_dict['u'] else None
    pirate_pattern = re.compile(r'\(pirate\)', re.IGNORECASE) if opt_dict['P'] else None
    prototype_pattern = re.compile(r'\((?:prototype|proto)\)', re.IGNORECASE) if opt_dict['p'] else None
    country_pattern = re.compile(rf'{opt_dict["country"]}', re.IGNORECASE) if opt_dict['country'] else None

    console_id = parsing_RA_console_ids(opt_dict['cheevos'])
    if console_id:
        game_hashes = get_RA_game_info(console_id)
        print("Game hashes loaded")
        print(game_hashes)

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

        if console_id:
            should_process = True if has_cheevos(game_hashes, get_md5(file_path)) else False

        if md5_set:
            should_process = True if get_md5(file_path) in md5_set else False

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

    if source_dir == destination_dir:
        print("Error: Source and destination directories must be different.")
        sys.exit(1)
    
    if not os.path.exists(source_dir):
        print("Error: Source directory does not exist.")
        sys.exit(1)

    opt_dict = {
        "d": False,
        "u": False,
        "p": False,
        "P": False,
        "country": None,
        "dat": None,
        "cheevos": None
    }

    verbose = False
    move_files = False
    cheevos = False

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
        elif arg.startswith('--cheevos'):
            opt_dict['cheevos'] = arg.split('=')[1] if '=' in arg else None

    # If a .dat file was provided, get the MD5 hashes
    md5_set = set()
    if opt_dict["dat"]:
        md5_set = get_md5_from_dat(opt_dict["dat"])

    process_roms(source_dir, destination_dir, opt_dict, md5_set, move_files,  verbose)
