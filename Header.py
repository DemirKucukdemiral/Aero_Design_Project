import os
from datetime import datetime

def add_header_to_script():
    # Ask for the script path (absolute or relative)
    script_path = input("Enter the full or relative path to the script (with .py): ").strip()

    # Expand `~` if used (for macOS/Linux home directories)
    script_path = os.path.expanduser(script_path)

    # Convert to absolute path
    script_path = os.path.abspath(script_path)

    # Check if the file exists
    if not os.path.exists(script_path):
        print(f"Error: {script_path} does not exist!")
        return

    # Read existing content
    with open(script_path, "r") as f:
        existing_content = f.readlines()

    # Define header content
    current_date = datetime.now().strftime("%Y-%m-%d")
    header = f'''
###===--------------------------------------------===###
# Script:       {os.path.basename(script_path)}
# Authors:       Demir Kucukdemiral 2883935K, Charikleia Nikou 2881802N, Cameron Norrington 2873038N, Ben Maconnachie 2911209M, Jeremi Rozanski 2881882R
# Created on:   {current_date}
# Last Modified: {current_date}
# Description:  [Short description of the script]
# Version:      1.0
###===--------------------------------------------===###    


'''

    # Check if the file already contains a header
    if any("===" in line for line in existing_content[:10]):  # Look in the first 10 lines
        print(f"⚠️ Header already exists in {script_path}. No changes made.")
        return

    # Insert the header at the top, keeping old content
    with open(script_path, "w") as f:
        f.write(header + "".join(existing_content))

    print(f"Header successfully added to {script_path}")

if __name__ == "__main__":
    add_header_to_script()