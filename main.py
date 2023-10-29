import os
import time
import logging
import argparse
import platform
import subprocess
from pathlib import Path
from typing import Optional
from utils.source_ext import MapExt
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path: str = os.path.normpath(file_path)
        self.process: Optional[subprocess.Popen] = None

    def on_created(self, event):
        if event.is_directory:
            return
        evt_parts = os.path.basename(event.src_path).split(" ")
        evt_extension = evt_parts[-1].split(".")[-1]
        evt_filename = f"{evt_parts[0]}.{evt_extension}"
        f_path = os.path.basename(self.file_path)
        if f_path == evt_filename:
            logging.info("Replacement file created. Relaunching...")
            self._restart_process()

    def on_deleted(self, event):
        """Handle file deletion event"""
        if event.src_path.endswith(os.path.basename(self.file_path)):
            logging.info("File deleted. Exiting...")
            os._exit(0)

    def on_modified(self, event):
        """Handle file modification event"""
        if event.is_directory:
            return
        if event.src_path == self.file_path:
            logging.info("File modified. Relaunching...")
            self._restart_process()

    def _terminate_process(self, process: subprocess.Popen):
        _timeout = 5
        _, ext = os.path.splitext(self.file_path)
        if platform.system() == "Windows":
            if ext == ".exe":
                try:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)])
                    process.wait(timeout=_timeout)
                except Exception as e:
                    logging.error(f"Error while terminating process: {e}")
            else:
                try:
                    process.terminate()
                    process.wait(timeout=_timeout)
                except Exception as e:
                    logging.error(f"Error while terminating process: {e}")
        else:
            try:
                process.kill()
                process.wait(timeout=_timeout)
            except Exception as e:
                logging.error(f"Error while terminating process: {e}")

    def _create_subprocess(self, file_path: str) -> subprocess.Popen:
        interpreter = MapExt.resolve(file_path)
        if platform.system() == "Windows":
            if interpreter:
                return subprocess.Popen(
                    [interpreter, file_path],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                )
            elif os.path.isfile(file_path) and file_path.lower().endswith(".exe"):
                return subprocess.Popen(
                    [file_path], creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                logging.error(f"Unsupported file type for Windows: {file_path}")
        else:
            if interpreter:
                return subprocess.Popen([interpreter, file_path])
            elif os.path.isfile(file_path) and file_path.lower().endswith(".exe"):
                return subprocess.Popen([file_path])
            else:
                logging.error(f"Unsupported file type: {file_path}")

    def _restart_process(self):
        if self.process:
            try:
                self._terminate_process(self.process)
            except subprocess.TimeoutExpired:
                logging.warning("Old process did not terminate. Forcing termination...")
                self.process.kill()
        self.process = self._create_subprocess(self.file_path)


def init_file_monitoring(file_path: str, monitored_directory: str):
    """
    Monitor directory for changes and automatically relaunch executable (.exe) or script files.

    Args:
        file_path (str): Executable or Script file.
        monitored_directory (str): Directory to be monitored.

    Example:
        init_file_monitoring("binary_or_script_file ex: test.exe test.py", "/path/to/directory")
    """
    event_handler = FileChangeHandler(file_path)
    observer = Observer()

    try:
        observer.schedule(event_handler, str(monitored_directory), recursive=False)
        observer.start()

        file = os.path.basename(file_path)
        file_count = sum(1 for _ in monitored_directory.iterdir() if _.is_file())
        logging.info(f"Number of files in the directory: {file_count}")
        logging.info(f"Monitoring directory: {monitored_directory}")
        logging.info(f"File: {file}")
        logging.info("Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping file monitoring...")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        observer.stop()
        observer.join()


def main():
    parser = argparse.ArgumentParser(
        description="Monitor directory and automatically relaunch binary or script file."
    )
    parser.add_argument(
        "--bin",
        type=Path,
        required=False,
        help="Binary or Script file Ex. test.py, test.exe.",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        required=False,
        default=Path.cwd(),
        help="Path to the Directory to be monitored. Defaults to the current working directory.",
    )
    parser.add_argument("-v", "--version", action="store_true", help="Package version.")
    args = parser.parse_args()
    if args.version:
        package_version = "0.3.3"
        print(f"binswap {package_version}")
        return

    if not args.bin:
        logging.error("File path is required.")
        return

    bin_path = args.dir / args.bin
    if not bin_path.exists():
        logging.error("Binary file does not exist. Please provide a valid path.")
        return

    init_file_monitoring(bin_path, args.dir)


if __name__ == "__main__":
    main()
