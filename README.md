# ROM Organizer Script - Usage Documentation

This script helps you organize ROM files by moving them into a destination directory based on specific filters like "demo", "unl", "prototype", and "country". You can use it to quickly sort and manage your ROM collection.
Requirements
```bash
Python 3.x
```

### Usage

To get help and console ID list.
```bash
./rom-organizer.py --help
```

To use the script, run it from the command line with the following syntax:
```bash
./rom-organizer.py <source_directory> <destination_directory> [-d] [-u] [-p] [-P] [--grep=<word>]
```

To use to check if game has achievements on retroachievements.org
Check your api key in: retroachevements.org/settings
```bash
export RETRO_ACHIEVEMENTS_API_KEY=<your_api_key> && ./rom-organizer.py <source_directory> <destination_directory> [--cheevos=<ID>]
```

### Parameters

- **<source_directory>**       Directory where the ROM files are located.
- **<destination_directory>**  Directory where the filtered ROM files will be copied or moved.
- **-d**                       Process ROMs containing "(demo)" in their filenames.
- **-u**                       Process ROMs containing "(unl)" in their filenames.
- **-p**                       Process ROMs containing "(prototype)" or "(proto)" in their filenames.
- **-P**                       Process ROMs containing "(pirate)" in their filenames.
- **--grep=<'word'>**          Process ROMs containing the specified key word in their filenames.
- **--dat=<dat_file>**         Filter ROMs by MD5 using the provided .dat file. If the file is a .zip, it will be temporarily extracted for MD5 checking.
- **--cheevos=<ID>**           Filter ROMs by checking if they have achievements on RetroAchievements.   
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
./rom-organizer.py /path/to/roms /path/to/destination -d -u -p --grep=Brazil
```
Example 3: Move ROMs with "prototype" and "unl"
```bash
./rom-organizer.py /path/to/roms /path/to/destination -up
```

### DAT files download:

[libretro dat files](https://github.com/libretro/libretro-database/tree/master/metadat/no-intro)

### Notes

    The script can handle multiple filters at once. For example, -d -u will copy ROMs that contain both "demo" and "unl".

