#!/usr/bin/env python3

import os
import mimetypes
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

BASE_PATH = os.path.expanduser('~')

# Define a dictionary to map file extensions to folder names
file_type_mapping = {
    '.mp3': 'music',
	'.mp4': 'videos',
	'.pdf': 'documents',
	'.jpg': 'images',
	'.jpeg': 'images',
	'.png': 'images',
    # Add more file extensions and corresponding folder names as needed
}

# Initialize the mimetypes database
mimetypes.init()

# Create logs folder if not exists
logs_folder = 'logs'
if not os.path.exists(logs_folder):
	os.makedirs(logs_folder)

# Configure logging to write to a file
log_file_path = os.path.join(os.getcwd(), logs_folder, 'file_organizer.log')
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Function to move a file to the appropriate folder based on its type
def organize_file(file_path):
    file_extension = os.path.splitext(file_path)[1]
    folder_name = file_type_mapping.get(file_extension.lower(), 'other')
    destination_folder = os.path.join(BASE_PATH, 'Desktop', folder_name)
    
    if not os.path.exists(destination_folder):
        logging.info(f"{destination_folder} folder is creating...")
        os.makedirs(destination_folder)
    
    destination_path = os.path.join(destination_folder, os.path.basename(file_path))
    
    try:
        os.rename(file_path, destination_path)
        logging.info(f"Moved '{file_path}' to the '{folder_name}' folder.")
    except FileNotFoundError:
        logging.warning(f"File '{file_path}' not found. It may have been moved or deleted.")

# A custom event handler for file creations
class CustomHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            mime_type, _ = mimetypes.guess_type(file_path)
            logging.debug(f"MIME type: {mime_type}")
            # Check if it's a recognized file type
            if mime_type:
                organize_file(file_path)
            else:
                logging.warning(f"Skipping '{file_path}' (unknown file type).")

if __name__ == "__main__":
    # Set the folder to monitor for new downloads
    folder_to_watch = os.path.join(BASE_PATH, 'Downloads')  # Replace with your desired folder path
    
    # Create an observer that watches the specified folder
    event_handler = CustomHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_to_watch, recursive=False)
    
    # Start monitoring
    observer.start()
    logging.info(f"Watching folder: {folder_to_watch}")
    
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()

