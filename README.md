# ROM Organizer Script - Usage Documentation

This script helps you organize ROM files by moving them into a destination directory based on specific filters like "demo", "unl", "prototype", and "country". You can use it to quickly sort and manage your ROM collection.
Requirements
```bash
    Python 3.x
```

### Usage

To use the script, run it from the command line with the following syntax:
```bash
python rom-organizer.py --help
python rom-organizer.py <source_directory> <destination_directory> [-d] [-u] [-p] [-P] [--country=<country>]
```

### Parameters

- <source_directory>: The directory where your ROM files are currently located.
- <destination_directory>: The directory where you want to move the filtered ROM files.
- -d: Move ROMs containing "(demo)" in their names.
- -u: Move ROMs containing "(unl)" in their names.
- -p: Move ROMs containing "(prototype)" in their names.
- -P: Move ROMs containing "(pirate)" in their names.
- --country=<country>: Move ROMs that contain the specified country name in their filenames. (Example: --country=Brazil)
- --verbose= Show files copy/move messages
- --help: Usage

### Examples
Example 1: Move ROMs with "demo" and "unl" to the destination directory
```bash
python rom-organizer.py /path/to/roms /path/to/destination -d -u
```
Example 2: Move ROMs with "demo", "unl", and "prototype", and filter by country "Brazil"
```bash
python rom-organizer.py /path/to/roms /path/to/destination -d -u -p --country=Brazil
```
Example 3: Move ROMs with "prototype" and "unl"
```bash
python rom-organizer.py /path/to/roms /path/to/destination -up
```

### Notes

    The script can handle multiple filters at once. For example, -d -u will move ROMs that contain both "demo" and "unl".
    If the --country parameter is specified, only ROMs containing that country name in their filename will be moved.

