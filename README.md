# ROM Organizer Script - Usage Documentation

This script helps you organize ROM files by moving them into a destination directory based on specific filters like "demo", "unl", "prototype", and "country". You can use it to quickly sort and manage your ROM collection.
Requirements
```bash
    Python 3.x
```

### Usage

To use the script, run it from the command line with the following syntax:
```bash
./rom-organizer.py --help
./rom-organizer.py <source_directory> <destination_directory> [-d] [-u] [-p] [-P] [--country=<country>]
```

### Parameters

- **<source_directory>**       Directory where the ROM files are located.
- **<destination_directory>**  Directory where the filtered ROM files will be copied or moved.
- **-d**                       Process ROMs containing "(demo)" in their filenames.
- **-u**                       Process ROMs containing "(unl)" or "(pirate)" in their filenames.
- **-p**                       Process ROMs containing "(prototype)" or "(proto)" in their filenames.
- **-P**                       Process ROMs containing "(pirate)" in their filenames (alternative to -u).
- **--country=<country>**      Process ROMs containing the specified country name in their filenames.
- **--dat=<dat_file>**         Filter ROMs by MD5 using the provided .dat file. If the file is a .zip, it will be temporarily extracted for MD5 checking.
- **--move**                   Move files instead of copying them. If this flag is omitted, files will be copied.
- **--verbose**                Print detailed logs of the operations being performed.
- **--help**                   Display this help message and exit.

### Examples
Example 1: Move ROMs with "demo" and "unl" to the destination directory
```bash
./rom-organizer.py /path/to/roms /path/to/destination -d -u
```
Example 2: Move ROMs with "demo", "unl", and "prototype", and filter by country "Brazil"
```bash
./rom-organizer.py /path/to/roms /path/to/destination -d -u -p --country=Brazil
```
Example 3: Move ROMs with "prototype" and "unl"
```bash
./rom-organizer.py /path/to/roms /path/to/destination -up
```

### DAT files download:

[libretro dat files](https://github.com/libretro/libretro-database/tree/master/metadat/no-intro)

### Notes

    The script can handle multiple filters at once. For example, -d -u will move ROMs that contain both "demo" and "unl".
    If the --country parameter is specified, only ROMs containing that country name in their filename will be moved.

