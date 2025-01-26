import os
import shutil
import sys
import re

def move_roms(source_dir, destination_dir, opt_dict):
    # Check if the destination directory exists, if not, create it
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    # Compile regular expressions for demo, unl, prototype, and country filter
    demo_pattern = re.compile(r'\(demo\)', re.IGNORECASE) if opt_dict['d'] else None
    unl_pattern = re.compile(r'\(unl\)', re.IGNORECASE) if opt_dict['u'] else None
    prototype_pattern = re.compile(r'\(prototype\)', re.IGNORECASE) if opt_dict['p'] else None
    country_pattern = re.compile(rf'{opt_dict["country"]}', re.IGNORECASE) if opt_dict['country'] else None

    # Use a set to track filenames and avoid duplicates
    seen = set()

    # Traverse through all files in the source directory and subdirectories
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            file_name = os.path.splitext(file)[0]  # Get the file name without extension

            # Skip duplicate files
            if file_name in seen:
                continue
            seen.add(file_name)

            # Check if the file matches the demo, unl, prototype, or country criteria
            should_move = True

            # Filter by demo
            if demo_pattern and not demo_pattern.search(file_name):
                should_move = False

            # Filter by unl
            if unl_pattern and not unl_pattern.search(file_name):
                should_move = False

            # Filter by prototype
            if prototype_pattern and not prototype_pattern.search(file_name):
                should_move = False

            # Filter by country
            if country_pattern and not country_pattern.search(file_name):
                should_move = False

            # If the file matches the criteria, move it
            if should_move:
                print(f"Moving file: {file} to {destination_dir}")
                shutil.move(os.path.join(root, file), destination_dir)

    print("Organization completed!")

# Main entry point of the script
if __name__ == '__main__':
    # Check if we have the correct number of arguments
    if len(sys.argv) < 4:
        print("Usage: python script.py <source_directory> <destination_directory> [-d] [-u] [-p] [--country <country>]")
        sys.exit(1)

    # Source and destination directories
    source_dir = sys.argv[1]
    destination_dir = sys.argv[2]

    # Define the options dictionary with default values
    opt_dict = {
        "d": False,
        "u": False,
        "p": False,
        "country": None
    }

    # Process the arguments
    args = sys.argv[3:]
    for arg in args:
        if arg.startswith('-'):
            # Start of a filter argument, check each letter after the "-"
            for char in arg[1:]:  # Skip the leading "-"
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

    # Call the move_roms function with the appropriate parameters
    move_roms(source_dir, destination_dir, opt_dict)
