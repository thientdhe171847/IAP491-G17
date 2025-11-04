from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QFileDialog
import os
import shutil
from pathlib import Path
from datetime import datetime
import re


class FileClassifier:
    """Phân loại file theo cấu trúc mới
    - System: Config, Action (Log/Db/Xml/Other)
    - App: <app_name> (Log/Db/Json/Xml/Other)
    - Connect: Network (Config + Log/Db/Json/Xml/Other), BT (Config + Log/Db/Json/Xml/Other)
    """

    # ==================== SYSTEM ====================
    SYSTEM_CONFIG_PATHS = [
        'default.prop',
        'dpolicy',
        'etc/',
        'vendor/',
        'oem/',
        'product/',
        'odm/',
        'metadata/',
        'efs/',
        'sepolicy_version',
        'spu/',
        'init',
        'data/etc',
        'data/property'
    ]

    SYSTEM_ACTION_PATHS = [
        'bugreports',
        'cache',
        'data/adb',
        'data/anr',
        'data/tombstones',
        'data/rdx_dump',
        'data/log',
        'data/system',
        'data/system_ce',
        'data/system_de'
    ]

    # ==================== CONNECT NETWORK ====================
    CONNECT_NETWORK_CONFIG_PATHS = [
        'data/misc/net',
        'data/misc/dhcp',
        'data/misc/ethernet',
        'data/misc/vpn',
        'data/misc/apns',
        'data/misc/carrierid',
        'data/misc/network_watchlist',
        'data/misc/pageboost'
    ]

    CONNECT_NETWORK_ACTION_PATHS = [
        'data/misc/bootstat',
        'data/misc/boottrace',
        'data/misc/snapshotctl_log',
        'data/misc/update_engine_log',
        'data/misc/wmtrace',
        'data/misc/trace',
        'data/misc/profman',
        'data/misc/user',
        'data/misc/sms',
        'data/misc/credstore',
        'data/misc/stats-data',
        'data/misc/stats-metadata',
        'data/misc/stats-active-metric',
        'data/misc/stats-service',
        'data/misc/perfetto-traces',
        'data/misc/textclassifier',
        'data/misc/update_engine',
        'data/misc/vold',
        'data/misc/recovery',
        'data/misc/shared_relro'
    ]

    # ==================== CONNECT BT ====================
    CONNECT_BT_CONFIG_PATHS = [
        'data/misc/bluedroid',
        'data/misc/bluetooth'
    ]

    CONNECT_BT_ACTION_PATHS = [
        'data/misc/profiles',
        'data/misc/keychain',
        'data/misc/audioserver'
    ]

    # ==================== APP ====================
    APP_PATHS = [
        'data/app',
        'data/data',
        'data/user'
    ]

    APP_KNOWN_SUBFOLDERS = {'databases', 'shared_prefs', 'files', 'cache', 'code_cache', 'no_backup', 'app_webview'}

    @staticmethod
    def extract_package_name(path_parts):
        """Extract Android package name from path"""
        low_parts = [p.lower() for p in path_parts]

        # Pattern 1: /data/data/<package>/
        for i, part in enumerate(low_parts):
            if part == 'data' and i + 1 < len(low_parts) and low_parts[i + 1] == 'data' and i + 2 < len(low_parts):
                potential_package = path_parts[i + 2]
                if potential_package.lower() in FileClassifier.APP_KNOWN_SUBFOLDERS and i + 3 < len(low_parts):
                    potential_package = path_parts[i + 3]
                if '.' in potential_package and re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$', potential_package, re.IGNORECASE):
                    return potential_package
                if potential_package and potential_package.lower() not in FileClassifier.APP_KNOWN_SUBFOLDERS:
                    return potential_package

        # Pattern 2: /data/app/<folder>/
        for i, part in enumerate(low_parts):
            if part == 'data' and i + 1 < len(low_parts) and low_parts[i + 1] == 'app' and i + 2 < len(low_parts):
                next_part = path_parts[i + 2]
                package = re.split(r'[-=]', next_part)[0]
                if '.' in package and re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$', package, re.IGNORECASE):
                    return package
                if package and package.lower() not in FileClassifier.APP_KNOWN_SUBFOLDERS:
                    return package

        # Pattern 3: /data/user/<id>/<package>/
        for i, part in enumerate(low_parts):
            if part == 'data' and i + 1 < len(low_parts) and low_parts[i + 1] == 'user':
                if i + 2 < len(low_parts) and low_parts[i + 2].isdigit():
                    if i + 3 < len(low_parts):
                        potential_package = path_parts[i + 3]
                        if '.' in potential_package and re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$', potential_package, re.IGNORECASE):
                            return potential_package
                        if potential_package and potential_package.lower() not in FileClassifier.APP_KNOWN_SUBFOLDERS:
                            return potential_package

        # Pattern 4: find any part that looks like a package name
        for part in path_parts:
            if '.' in part and not part.startswith('.'):
                if re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){2,}$', part, re.IGNORECASE):
                    return part

        return None

    @staticmethod
    def get_file_type_from_extension(file_ext):
        """Xác định file type từ extension"""
        file_ext = file_ext.lower()

        if file_ext in ['.log', '.txt']:
            return 'Log'
        elif file_ext in ['.db', '.sqlite', '.sqlite3', '.db-wal', '.db-shm', '.sqlite-wal', '.sqlite-shm',
                          '.db-journal', '.sqlite-journal', '.journal', '.wal', '.shm', '.sql']:
            return 'Db'
        elif file_ext == '.json':
            return 'Json'
        elif file_ext == '.xml':
            return 'Xml'
        else:
            return 'Other'

    @staticmethod
    def path_matches_any(path_str, path_list):
        """Kiểm tra path có khớp với bất kỳ pattern nào không"""
        path_lower = path_str.lower().replace('\\', '/')
        for pattern in path_list:
            pattern_lower = pattern.lower().replace('\\', '/')
            if pattern_lower in path_lower:
                return True
        return False

    @staticmethod
    def classify(file_path: Path, input_root: Path):
        """
        Phân loại file theo cấu trúc mới
        Returns: {
            'main_category': 'System' | 'App' | 'Connect',
            'sub_category': str,
            'sub_type': str (Config/Action for System, Log/Db/Json/Xml/Other),
            'app_name': str | None,
        }
        """
        try:
            relative_path = file_path.relative_to(input_root)
        except ValueError:
            relative_path = file_path

        path_parts = list(relative_path.parts)
        path_str = str(relative_path).replace('\\', '/')
        file_ext = file_path.suffix.lower()

        result = {
            'main_category': None,
            'sub_category': None,
            'sub_type': None,
            'app_name': None,
        }

        # ==================== CONNECT - NETWORK ====================
        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_NETWORK_CONFIG_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'Network'
            result['sub_type'] = 'Config'
            return result

        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_NETWORK_ACTION_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'Network'
            result['sub_type'] = FileClassifier.get_file_type_from_extension(file_ext)
            return result

        # ==================== CONNECT - BT ====================
        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_BT_CONFIG_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'BT'
            result['sub_type'] = 'Config'
            return result

        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_BT_ACTION_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'BT'
            result['sub_type'] = FileClassifier.get_file_type_from_extension(file_ext)
            return result

        # ==================== SYSTEM ====================
        if FileClassifier.path_matches_any(path_str, FileClassifier.SYSTEM_CONFIG_PATHS):
            result['main_category'] = 'System'
            result['sub_category'] = 'Config'
            result['sub_type'] = 'Config'
            return result

        if FileClassifier.path_matches_any(path_str, FileClassifier.SYSTEM_ACTION_PATHS):
            result['main_category'] = 'System'
            result['sub_category'] = 'Action'
            result['sub_type'] = FileClassifier.get_file_type_from_extension(file_ext)
            return result

        # ==================== APP ====================
        package_name = FileClassifier.extract_package_name(path_parts)

        if package_name or FileClassifier.path_matches_any(path_str, FileClassifier.APP_PATHS):
            app_name = package_name if package_name else 'Unknown'

            # Fallback: scan for data/data or data/user pattern
            if not package_name:
                low_parts = [p.lower() for p in path_parts]
                for i, p in enumerate(low_parts):
                    if p == 'data' and i + 1 < len(low_parts) and low_parts[i + 1] == 'data' and i + 2 < len(low_parts):
                        candidate = path_parts[i + 2]
                        if candidate.lower() not in FileClassifier.APP_KNOWN_SUBFOLDERS:
                            app_name = candidate
                            break
                if not package_name:
                    for i, p in enumerate(low_parts):
                        if p == 'data' and i + 1 < len(low_parts) and low_parts[i + 1] == 'app' and i + 2 < len(low_parts):
                            candidate = re.split(r'[-=]', path_parts[i + 2])[0]
                            if candidate and candidate.lower() not in FileClassifier.APP_KNOWN_SUBFOLDERS:
                                app_name = candidate
                                break

            result['main_category'] = 'App'
            result['sub_category'] = app_name
            result['app_name'] = app_name
            result['sub_type'] = FileClassifier.get_file_type_from_extension(file_ext)
            return result

        # ==================== DEFAULT ====================
        result['main_category'] = 'System'
        result['sub_category'] = 'Action'
        result['sub_type'] = FileClassifier.get_file_type_from_extension(file_ext)
        return result


class ExtractionWorker(QThread):
    """Worker thread để thực hiện extraction không block UI"""
    progress = Signal(int, str)
    finished = Signal(bool, str)

    def __init__(self, input_path, case_id, mode):
        super().__init__()
        self.input_path = input_path
        self.case_id = case_id
        self.mode = mode
        self.is_cancelled = False

    def run(self):
        try:
            self.progress.emit(5, "Validating input...")
            input_path = Path(self.input_path)

            if not input_path.exists():
                self.finished.emit(False, "Error: Selected path does not exist")
                return

            if self.mode == "file":
                if input_path.is_file():
                    if input_path.stat().st_size == 0:
                        self.finished.emit(False, "Error: Selected file is empty (0 bytes)")
                        return
                else:
                    self.finished.emit(False, "Error: Selected path is not a valid file")
                    return
            elif self.mode == "folder":
                if not input_path.is_dir():
                    self.finished.emit(False, "Error: Selected path is not a valid folder")
                    return
                all_files = [f for f in input_path.rglob('*') if f.is_file()]
                if len(all_files) == 0:
                    self.finished.emit(False, "Error: Selected folder is empty (no files found)")
                    return
                self.progress.emit(10, f"Found {len(all_files)} files in folder")

            self.progress.emit(15, "Creating directory structure...")
            # Tạo Root ở thư mục làm việc hiện tại
            current_dir = Path.cwd()
            case_dir = current_dir / self.case_id
            root_dir = case_dir / "Root"
            self.create_work_structure(root_dir)

            log_file = root_dir / "conversion_manifest.txt"
            with open(log_file, 'w', encoding='utf-8') as log:
                log.write("=" * 80 + "\n")
                log.write(f"CASE ID: {self.case_id}\n")
                log.write(f"GENERATED (UTC): {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}Z\n")
                log.write(f"INPUT PATH: {self.input_path}\n")
                log.write(f"INPUT MODE: {self.mode.upper()}\n")
                log.write("=" * 80 + "\n\n")

                if self.mode == "file":
                    all_files = [input_path]
                else:
                    all_files = [f for f in input_path.rglob('*') if f.is_file()]

                total_files = len(all_files)
                if total_files == 0:
                    self.progress.emit(100, "No files found to process")
                    self.finished.emit(False, "No files found in input")
                    return

                self.progress.emit(25, f"Found {total_files} files to process...")

                processed = 0
                stats = {
                    'System': {'Config': 0, 'Action': {'Log': 0, 'Db': 0, 'Xml': 0, 'Other': 0}},
                    'App': {},
                    'Connect': {
                        'Network': {'Config': 0, 'Log': 0, 'Db': 0, 'Json': 0, 'Xml': 0, 'Other': 0},
                        'BT': {'Config': 0, 'Log': 0, 'Db': 0, 'Json': 0, 'Xml': 0, 'Other': 0}
                    }
                }

                for file_path in all_files:
                    if self.is_cancelled:
                        self.finished.emit(False, "Cancelled by user")
                        return

                    try:
                        classification = FileClassifier.classify(file_path, input_path)
                        target_dir = self.build_target_path(root_dir, classification)
                        target_dir.mkdir(parents=True, exist_ok=True)
                        success = self.process_file(file_path, target_dir, classification, log)
                        if success:
                            self.update_stats(stats, classification)
                    except Exception as e:
                        log.write(f"[ERROR] Failed to process {file_path}: {str(e)}\n")

                    processed += 1
                    progress_percent = 25 + int((processed / total_files) * 70)
                    self.progress.emit(progress_percent, f"Processing: {file_path.name} ({processed}/{total_files})")

                self.write_statistics(log, stats, processed)

            self.progress.emit(100, "Extraction completed!")
            summary = f"Processed {processed} files\nOutput: {root_dir}"
            self.finished.emit(True, summary)

        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

    def create_work_structure(self, root_dir):
        """Tạo cấu trúc thư mục Root theo cấu trúc mới"""
        # System
        (root_dir / "System" / "Config").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Action" / "Log").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Action" / "Db").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Action" / "Xml").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Action" / "Other").mkdir(parents=True, exist_ok=True)

        # Connect - Network
        (root_dir / "Connect" / "Network" / "Config").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Log").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Db").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Json").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Xml").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Other").mkdir(parents=True, exist_ok=True)

        # Connect - BT
        (root_dir / "Connect" / "BT" / "Config").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Log").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Db").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Json").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Xml").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Other").mkdir(parents=True, exist_ok=True)

    def build_target_path(self, root_dir, classification):
        """Xây dựng đường dẫn thư mục đích theo cấu trúc mới"""
        main_cat = classification['main_category']
        sub_cat = classification['sub_category']
        sub_type = classification['sub_type']

        if main_cat == 'System':
            if sub_cat == 'Config':
                return root_dir / main_cat / sub_cat
            else:  # Action
                return root_dir / main_cat / sub_cat / sub_type
        elif main_cat == 'App':
            return root_dir / main_cat / sub_cat / sub_type
        elif main_cat == 'Connect':
            return root_dir / main_cat / sub_cat / sub_type
        else:
            return root_dir / "System" / "Action" / "Other"

    def process_file(self, source_path, target_dir, classification, log):
        """Xử lý và copy file"""
        try:
            target_file = target_dir / source_path.name
            shutil.copy2(source_path, target_file)
            log.write(f"[{classification['main_category']}/{classification['sub_category']}/{classification['sub_type']}] {source_path.name}\n")
            return True
        except Exception as e:
            log.write(f"[ERROR] {source_path.name}: {str(e)}\n")
            return False

    def update_stats(self, stats, classification):
        """Update statistics theo cấu trúc mới"""
        main_cat = classification['main_category']
        sub_cat = classification.get('sub_category', 'Unknown')
        sub_type = classification.get('sub_type', 'Other')

        if main_cat == 'System':
            if sub_cat == 'Config':
                stats['System']['Config'] += 1
            else:  # Action
                if sub_type not in stats['System']['Action']:
                    stats['System']['Action'][sub_type] = 0
                stats['System']['Action'][sub_type] += 1
        elif main_cat == 'Connect':
            if sub_type not in stats['Connect'][sub_cat]:
                stats['Connect'][sub_cat][sub_type] = 0
            stats['Connect'][sub_cat][sub_type] += 1
        elif main_cat == 'App':
            app_name = classification.get('app_name', 'Unknown')
            if app_name not in stats['App']:
                stats['App'][app_name] = {'Log': 0, 'Db': 0, 'Json': 0, 'Xml': 0, 'Other': 0}
            if sub_type not in stats['App'][app_name]:
                stats['App'][app_name][sub_type] = 0
            stats['App'][app_name][sub_type] += 1

    def write_statistics(self, log, stats, total_processed):
        """Ghi thống kê ra file log"""
        log.write("\n" + "=" * 80 + "\n")
        log.write("STATISTICS:\n")
        log.write("=" * 80 + "\n\n")

        # System
        log.write("SYSTEM:\n")
        log.write(f"  Config: {stats['System']['Config']}\n")
        log.write("  Action:\n")
        for ftype, count in sorted(stats['System']['Action'].items()):
            log.write(f"    {ftype}: {count}\n")

        # App
        log.write("\nAPP:\n")
        for app_name in sorted(stats['App'].keys()):
            types = stats['App'][app_name]
            total = sum(types.values())
            log.write(f"  {app_name} (Total: {total}):\n")
            for ftype, count in sorted(types.items()):
                if count > 0:
                    log.write(f"    {ftype}: {count}\n")

        # Connect
        log.write("\nCONNECT:\n")
        for sub in ['Network', 'BT']:
            log.write(f"  {sub}:\n")
            for ftype, count in sorted(stats['Connect'][sub].items()):
                log.write(f"    {ftype}: {count}\n")

        log.write("\n" + "=" * 80 + "\n")
        log.write(f"TOTAL PROCESSED: {total_processed}\n")
        log.write("=" * 80 + "\n")
        log.write("[DONE] Stage 1 completed successfully.\n")

    def cancel(self):
        """Cancel the operation"""
        self.is_cancelled = True


class Backend(QObject):
    fileOrFolderSelected = Signal(str)
    extractionProgress = Signal(int, str)
    extractionFinished = Signal(bool, str)

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
