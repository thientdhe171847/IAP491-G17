from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QFileDialog
import os
import shutil
import sqlite3
import csv
from pathlib import Path
from datetime import datetime


class ExtractionWorker(QThread):
    """Worker thread để thực hiện extraction không block UI"""
    progress = Signal(int, str)  # progress_percent, message
    finished = Signal(bool, str)  # success, message

    def __init__(self, input_path, case_id, mode):
        super().__init__()
        self.input_path = input_path
        self.case_id = case_id
        self.mode = mode  # "file" or "folder"
        self.is_cancelled = False

    def run(self):
        try:
            # Tạo cấu trúc thư mục
            root_dir = Path(self.input_path).parent / self.case_id
            raw_dir = root_dir / "RAW"
            work_dir = root_dir / "WORK"

            # Tạo các thư mục
            self.progress.emit(5, "Creating directory structure...")
            work_dir.mkdir(parents=True, exist_ok=True)
            (work_dir / "logs").mkdir(exist_ok=True)
            (work_dir / "xml").mkdir(exist_ok=True)
            (work_dir / "db").mkdir(exist_ok=True)
            (work_dir / "json").mkdir(exist_ok=True)
            (work_dir / "others").mkdir(exist_ok=True)

            # Copy input vào RAW
            self.progress.emit(10, "Copying input to RAW directory...")
            raw_dir.mkdir(parents=True, exist_ok=True)

            if self.mode == "file":
                shutil.copy2(self.input_path, raw_dir / Path(self.input_path).name)
            else:
                shutil.copytree(self.input_path, raw_dir, dirs_exist_ok=True)

            # Tạo log file
            log_file = work_dir / "conversion_manifest.txt"

            with open(log_file, 'w', encoding='utf-8') as log:
                log.write("=" * 61 + "\n")
                log.write(f"CASE ID: {self.case_id}\n")
                log.write(f"GENERATED (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}Z\n")
                log.write("=" * 61 + "\n\n")

                # Lấy danh sách tất cả files trong RAW
                all_files = list(raw_dir.rglob('*'))
                all_files = [f for f in all_files if f.is_file()]
                total_files = len(all_files)

                if total_files == 0:
                    self.progress.emit(100, "No files found to process")
                    self.finished.emit(False, "No files found in the selected input")
                    return

                self.progress.emit(15, f"Found {total_files} files to process...")

                # Xử lý từng file
                processed = 0
                stats = {
                    'txt': 0, 'log': 0, 'xml': 0, 'json': 0,
                    'db': 0, 'db_converted': 0, 'others': 0
                }

                for file_path in all_files:
                    if self.is_cancelled:
                        self.finished.emit(False, "Cancelled by user")
                        return

                    ext = file_path.suffix.lower()
                    name = file_path.name

                    try:
                        if ext == '.txt':
                            shutil.copy2(file_path, work_dir / "logs" / name)
                            log.write(f"[TXT] Copied: {file_path}\n")
                            stats['txt'] += 1

                        elif ext == '.log':
                            shutil.copy2(file_path, work_dir / "logs" / name)
                            log.write(f"[LOG] Copied: {file_path}\n")
                            stats['log'] += 1

                        elif ext == '.xml':
                            shutil.copy2(file_path, work_dir / "xml" / name)
                            log.write(f"[XML] Copied: {file_path}\n")
                            stats['xml'] += 1

                        elif ext == '.json':
                            shutil.copy2(file_path, work_dir / "json" / name)
                            log.write(f"[JSON] Copied: {file_path}\n")
                            stats['json'] += 1

                        elif ext == '.db':
                            log.write(f"[DB] Detected: {file_path}\n")
                            stats['db'] += 1

                            # Convert SQLite to CSV
                            csv_path = work_dir / "db" / f"{file_path.stem}.csv"
                            if self.convert_sqlite_to_csv(str(file_path), str(csv_path)):
                                log.write(f"[OK] Converted to CSV: {csv_path.name}\n")
                                stats['db_converted'] += 1
                            else:
                                log.write(f"[WARN] Not a valid SQLite DB: {file_path}\n")
                                # Copy as others
                                shutil.copy2(file_path, work_dir / "others" / name)

                        else:
                            shutil.copy2(file_path, work_dir / "others" / name)
                            log.write(f"[OTHER] Copied: {file_path}\n")
                            stats['others'] += 1

                    except Exception as e:
                        log.write(f"[ERROR] Failed to process {file_path}: {str(e)}\n")

                    processed += 1
                    progress_percent = 15 + int((processed / total_files) * 80)
                    self.progress.emit(progress_percent, f"Processing: {name} ({processed}/{total_files})")

                # Ghi thống kê
                log.write("\n" + "=" * 61 + "\n")
                log.write("STATISTICS:\n")
                log.write(f"  TXT files: {stats['txt']}\n")
                log.write(f"  LOG files: {stats['log']}\n")
                log.write(f"  XML files: {stats['xml']}\n")
                log.write(f"  JSON files: {stats['json']}\n")
                log.write(f"  DB files: {stats['db']} (Converted: {stats['db_converted']})\n")
                log.write(f"  Other files: {stats['others']}\n")
                log.write(f"  Total processed: {processed}\n")
                log.write("=" * 61 + "\n")
                log.write("[DONE] Stage 1 completed successfully.\n")

            self.progress.emit(100, "Extraction completed!")
            summary = f"Processed {processed} files\n"
            summary += f"Output: {work_dir}"
            self.finished.emit(True, summary)

        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

    def convert_sqlite_to_csv(self, db_path, csv_path):
        """Convert SQLite database to CSV"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Lấy danh sách tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            if not tables:
                conn.close()
                return False

            # Xuất table đầu tiên (hoặc có thể xuất tất cả tables)
            table_name = tables[0][0]
            cursor.execute(f"SELECT * FROM {table_name}")

            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                # Write headers
                csv_writer.writerow([description[0] for description in cursor.description])
                # Write data
                csv_writer.writerows(cursor.fetchall())

            conn.close()
            return True

        except Exception as e:
            return False

    def cancel(self):
        """Cancel the operation"""
        self.is_cancelled = True


class Backend(QObject):
    fileOrFolderSelected = Signal(str)
    extractionProgress = Signal(int, str)  # progress, message
    extractionFinished = Signal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        self.worker = None

    @Slot(str)
    def openFileOrFolderDialog(self, mode):
        if mode == "file":
            dialog = QFileDialog()
            dialog.setFileMode(QFileDialog.ExistingFiles)
            dialog.setOption(QFileDialog.DontUseNativeDialog, False)
            dialog.setNameFilters(["All Files (*)"])
            if dialog.exec():
                files = dialog.selectedFiles()
                if files:
                    self.fileOrFolderSelected.emit(files[0])
        elif mode == "folder":
            folder = QFileDialog.getExistingDirectory(None, "Chọn folder")
            if folder:
                self.fileOrFolderSelected.emit(folder)

    @Slot(str, str, str)
    def startExtraction(self, input_path, case_id, mode):
        """Bắt đầu quá trình extraction"""
        if self.worker and self.worker.isRunning():
            return

        self.worker = ExtractionWorker(input_path, case_id, mode)
        self.worker.progress.connect(self.extractionProgress.emit)
        self.worker.finished.connect(self.extractionFinished.emit)
        self.worker.start()

    @Slot()
    def cancelExtraction(self):
        """Hủy quá trình extraction"""
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
