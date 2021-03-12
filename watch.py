from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import time
import subprocess

target_dir = "static/cwlimg"


class FileChangeHandler(FileSystemEventHandler):
    def on_created(self, event):
        filepath = event.src_path

        if ".json" in filepath:
            print("{} created".format(filepath))
            subprocess.call(["bash", "cwl_convert.sh", filepath])


if __name__ == "__main__":
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, target_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
