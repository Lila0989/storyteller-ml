#!/bin/bash

cd ComfyUI

# Check if the input file exists
if [ ! -f ../gitkeeps.txt ]; then
    echo "File 'gitkeeps.txt' not found!"
    exit 1
fi

# Read each line from the file
while IFS= read -r directory; do
    # Check if the line is not empty and the directory exists
    if [[ -n "$directory" && -d "$directory" ]]; then
        # Add a .gitkeep file to the directory
        touch "${directory}/.gitkeep"
        echo "Added .gitkeep to $directory"
    else
        echo "Directory '$directory' not found or line is empty."
    fi
done < ../gitkeeps.txt

