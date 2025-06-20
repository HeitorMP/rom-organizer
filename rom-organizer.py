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

# SUA API KEY DO RETROACHIEVEMENTS
RETRO_ACHIEVEMENTS_API_KEY = os.getenv("RETRO_ACHIEVEMENTS_API_KEY")
RETRO_ACHIEVEMENTS_BASE_URL_GAMES = "https://retroachievements.org/API/API_GetGameList.php"
RETRO_ACHIEVEMENTS_BASE_URL_SYSTEM = "https://retroachievements.org/API/API_GetConsoleIDs.php"
HOME = os.getenv("HOME")
CONFIG_FILES_PATH = HOME + "/.config/rom-organizer/"
CONSOLE_ID_FILE = CONFIG_FILES_PATH + "consoles.json"

def display_help():
    """Displays usage instructions and details about each parameter."""
    help_text = """
ROM Organizer Script
=====================

This script helps you organize ROM files by copying or moving them to a destination directory based on filters like "demo", "unl", "prototype", "pirate", or a specific word.

Usage:
    python script.py <source_directory> <destination_directory> [-d] [-u] [-p] [-P] [--grep=<key word>] [--dat=<dat_file>] [--move] [--verbose] [--help]

Options:
    <source_directory>       Directory where the ROM files are located.
    <destination_directory>  Directory where the filtered ROM files will be copied or moved.

    -d                       Process ROMs containing "(demo)" in their filenames.
    -u                       Process ROMs containing "(unl)" or "(pirate)" in their filenames.
    -p                       Process ROMs containing "(prototype)" or "(proto)" in their filenames.
    -b                       Process ROMs containing "(beta)" in their filenames.
    -P                       Process ROMs containing "(pirate)" in their filenames (alternative to -u).
    --grep=<key word>        Add extra filters. All --grep terms must be present in the filename (logical AND). This refines the matches from -d, -u, -p, or -P.
    --dat=<dat_file>         Filter ROMs by MD5 using the provided .dat file.
                             If the file is a .zip, it will be temporarily extracted for MD5 checking.
    --cheevos=<console_id>   Filter ROMs by checking if they have achievements on RetroAchievements.
                             export RETRO_ACHIEVEMENTS_API_KEY=<your_api_key> needed.
    --move                   Move files instead of copying them. If this flag is omitted, files will be copied.
    --verbose                Print detailed logs of the operations being performed.
    --help                   Display this help message and exit.
"""
    print(help_text)
    if RETRO_ACHIEVEMENTS_API_KEY:
        print_console_ids()

def recriate_file_if_expired(path, console_id = None):
    """Checks if the file is expired (24 hours)."""
    """ If the file is expired, it will be recreated. """

    if not RETRO_ACHIEVEMENTS_API_KEY:
        print("export RETRO_ACHIEVEMENTS_API_KEY=<your_api_key> needed.")
        exit(1)

    url = None
    if not console_id:
        url = f"{RETRO_ACHIEVEMENTS_BASE_URL_SYSTEM}?y={RETRO_ACHIEVEMENTS_API_KEY}"
    else:
        url = f"{RETRO_ACHIEVEMENTS_BASE_URL_GAMES}?y={RETRO_ACHIEVEMENTS_API_KEY}&i={console_id}&h=1&f=1"
    if not os.path.exists(CONFIG_FILES_PATH):
        os.makedirs(CONFIG_FILES_PATH)

    if os.path.exists(path):
        file_time = os.path.getmtime(path)
        current_time = time.time()
        if current_time - file_time > 86400:
            print(f"File {path} is expired. Recreating...")
            try:
                response = requests.get(url)
                response.raise_for_status()
                consoles = response.json()

                with open(path, "w") as file:
                    json.dump(consoles, file)
            except requests.RequestException as e:
                print(f"Error to get information from API RetroAchievements: {e}")
    else:
        print(f"File {path} do not exist. Recreating...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            consoles = response.json()
            with open(path, "w") as file:
                json.dump(consoles, file)
        except requests.RequestException as e:
            print(f"Error to get information from API RetroAchievements: {e}")

def print_console_ids():
    """ Get and print a list of IDS and console names. """
    consoles = None
    recriate_file_if_expired(CONSOLE_ID_FILE)
    with open(CONSOLE_ID_FILE, "r") as file:
        consoles = json.load(file)
    
    print("Valids consoles ID:")
    for console in consoles:
        print(f"ID: {console['ID']} --- {console['Name']}")

def is_id_valid(id):
    """ Get the console ID from the user. """
    """ Validates the console ID provided by the user. """
    if not id.isdigit():
        print("Error: Console ID must be a number.")
        sys.exit(1)
    recriate_file_if_expired(CONSOLE_ID_FILE)
    with open(CONSOLE_ID_FILE, "r") as file:
        consoles = json.load(file)
        for console in consoles:
            if console['ID'] == int(id):
                return True
    return False


def get_RA_game_info(console_id):
    """ Generates a list of games for a specific console ID.
        Creates a file with the list of games if it doesn't exist or is expired.
    """
    games = None

    recriate_file_if_expired(f"{CONFIG_FILES_PATH}{console_id}.json", console_id)
    with open(f"{CONFIG_FILES_PATH}/{console_id}.json", "r") as file:
        games = json.load(file)
    return games
    
def has_cheevos(games, game_hash):
    """ Checks if a game has achievements based on its hash. """
    if not game_hash:
        return False
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

def get_arcade_md5(file_path):
    """ Returns the MD5 hash of a arcade file. """
    print("arcade")
    if not os.path.isfile(file_path):
        print("Error: File does not exist.")
        return None
    return calculate_md5(file_path)

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

    console_id = opt_dict.get('cheevos')
    game_hashes = None

    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Compila regex apenas se filtros ativados
    demo_pattern = re.compile(r'\(demo\)', re.IGNORECASE) if opt_dict.get('d') else None
    unl_pattern = re.compile(r'\(unl\)', re.IGNORECASE) if opt_dict.get('u') else None
    pirate_pattern = re.compile(r'\(pirate\)', re.IGNORECASE) if opt_dict.get('P') else None
    beta_pattern = re.compile(r'\(beta\)', re.IGNORECASE) if opt_dict.get('b') else None
    prototype_pattern = re.compile(r'\((?:prototype|proto)\)', re.IGNORECASE) if opt_dict.get('p') else None
    grep_patterns = [re.compile(re.escape(word), re.IGNORECASE) for word in opt_dict.get("grep", [])]

    # Configuração cheevos
    if console_id:
        if not RETRO_ACHIEVEMENTS_API_KEY:
            print("Error: RETRO_ACHIEVEMENTS_API_KEY environment variable is not set.")
            sys.exit(1)
        if not is_id_valid(console_id):
            print_console_ids()
            sys.exit(1)
        game_hashes = get_RA_game_info(console_id)

    seen = set()
    processed_count = 0

    for file in os.listdir(source_dir):
        file_path = os.path.join(source_dir, file)

        if not os.path.isfile(file_path):
            continue

        if file in seen:
            continue
        seen.add(file)

        lower_name = file.lower()

        # Decide se deve processar o arquivo
        should_process = True

        # Verifica filtros base (d, u, p, P, b)
        base_filters = []
        if demo_pattern:
            base_filters.append(bool(demo_pattern.search(lower_name)))
        if unl_pattern:
            base_filters.append(bool(unl_pattern.search(lower_name)))
        if prototype_pattern:
            base_filters.append(bool(prototype_pattern.search(lower_name)))
        if pirate_pattern:
            base_filters.append(bool(pirate_pattern.search(lower_name)))
        if beta_pattern:
            base_filters.append(bool(beta_pattern.search(lower_name)))

        if base_filters:
            # Se algum filtro base não for satisfeito, não processa
            if not any(base_filters):
                should_process = False

        # Aplica filtros grep: todos devem estar presentes no nome
        if grep_patterns:
            if not all(pattern.search(lower_name) for pattern in grep_patterns):
                should_process = False

        # Verifica se tem achievements se cheevos ativado
        if should_process and console_id:
            hash_func = get_arcade_md5 if console_id == "27" else get_md5
            game_hash = hash_func(file_path)
            if not has_cheevos(game_hashes, game_hash):
                should_process = False

        # Verifica MD5 se filtro md5_set ativo
        if should_process and md5_set:
            if get_md5(file_path) not in md5_set:
                should_process = False

        # Se passar nos filtros, copia ou move o arquivo
        if should_process:
            dest_file_path = os.path.join(destination_dir, file)

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
        "b": False,
        "P": False,
        "grep": [],
        "dat": None,
        "cheevos": None
    }

    verbose = False
    move_files = False
    cheevos = False

    args = sys.argv[3:]
    for arg in args:




        # Process command line arguments
        if arg.startswith('-') and not arg.startswith('--'):
            for char in arg[1:]:
                if char in opt_dict:
                    opt_dict[char] = True
                else:
                    print(f"Invalid filter option: -{char}")
                    sys.exit(1)
        elif arg.startswith('--grep'):
            grep = arg.split('=')[1] if '=' in arg else None
            if not grep:
                print("Error: Missing key word after --grep=")
                sys.exit(1)
            opt_dict["grep"].append(grep)
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

        # Check for exclusive options
        if opt_dict.get('dat'):  # Se dat tem valor (string)
            forbidden = [k for k, v in opt_dict.items() if k != 'dat' and v and k != 'grep']
            if forbidden or (opt_dict.get('grep') and len(opt_dict['grep']) > 0) or opt_dict.get('cheevos'):
                print("Error: When using --dat, no other filters (e.g. -p, -d, --grep, --cheevos) are allowed.")
                sys.exit(1)

        if opt_dict.get('cheevos'):
            forbidden = [k for k, v in opt_dict.items() if k != 'cheevos' and v and k != 'grep']
            if forbidden or (opt_dict.get('grep') and len(opt_dict['grep']) > 0) or opt_dict.get('dat'):
                print("Error: When using --cheevos, no other filters (e.g. -p, -d, --grep, --dat) are allowed.")
                sys.exit(1)

    # If a .dat file was provided, get the MD5 hashes
    md5_set = set()
    if opt_dict["dat"]:
        md5_set = get_md5_from_dat(opt_dict["dat"])

    process_roms(source_dir, destination_dir, opt_dict, md5_set, move_files,  verbose)
