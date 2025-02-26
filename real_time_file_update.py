import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from vector_indexing import build_index
from config import WATCH_DIRECTORY

class FileUpdateHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"File created: {event.src_path}. Rebuilding index...")
            build_index(WATCH_DIRECTORY)
    
    def on_modified(self, event):
        if not event.is_directory:
            logging.info(f"File modified: {event.src_path}. Rebuilding index...")
            build_index(WATCH_DIRECTORY)
    
    def on_deleted(self, event):
        if not event.is_directory:
            logging.info(f"File deleted: {event.src_path}. Rebuilding index...")
            build_index(WATCH_DIRECTORY)
    
    def on_moved(self, event):
        if not event.is_directory:
            logging.info(f"File moved from {event.src_path} to {event.dest_path}. Rebuilding index...")
            build_index(WATCH_DIRECTORY)

def start_file_watcher(directory):
    event_handler = FileUpdateHandler()
    observer = Observer()
    observer.schedule(event_handler, path=directory, recursive=True)
    observer.start()
    logging.info(f"Started file watcher on {directory}")
    return observer