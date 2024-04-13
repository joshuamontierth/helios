import os

def rename_files(directory_path):
    # Get the list of files in the directory
    files = os.listdir(directory_path)
    
    # Iterate through the files and rename them
    for i, filename in enumerate(files):
        # Construct the new filename with the desired format (e.g., 0.jpg, 1.jpg, etc.)
        new_filename = f"{i}.png"
        
        # Build the full paths for the old and new filenames
        old_filepath = os.path.join(directory_path, filename)
        new_filepath = os.path.join(directory_path, new_filename)
        
        # Rename the file
        os.rename(old_filepath, new_filepath)
        
        print(f"Renamed: {filename} -> {new_filename}")

# Replace 'your_directory_path' with the path to your directory containing the pictures
directory_path = '/home/joshua/weather/static/pics/Storm'

# Call the function to rename files in the specified directory
rename_files(directory_path)
