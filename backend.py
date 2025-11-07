from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QFileDialog
import os
import shutil
from pathlib import Path
from datetime import datetime
import re


class FileClassifier:
    """Phân loại file theo cấu trúc mới"""

    # ==================== SYSTEM ====================
    SYSTEM_CONFIG_PATHS = [
        'default.prop',
        'dpolicy',
        'etc',
        'vendor',
        'oem',
        'product',
        'odm',
        'metadata',
        'efs',
        'sepolicy_version',
        'spu',
        'data/etc',
        'data/property',
        'data/vendor',
        'externaldump/cmd',
        'externaldump/proc'
    ]

    SYSTEM_CONFIG_PATTERNS = [
        r'^init.*'  # init*
    ]

    # PRIORITY: Các đường dẫn CỤ THỂ hơn phải được kiểm tra TRƯỚC
    SYSTEM_ACTION_LOG_PATHS = [
        'data/vendor/log',
        'data/log',
        'bugreports',
        'cache',
        'data/adb',
        'data/anr',
        'data/tombstones',
        'data/rdx_dump',
        'externaldump/bugreport',
        'externaldump/logs',
        'externaldump/perf'
    ]

    SYSTEM_ACTION_DB_PATHS = [
        'data/system',
        'data/system_ce',
        'data/system_de',
        # 'externaldump/dump'
    ]

    # ==================== APP ====================
    APP_PATHS = [
        'data/data',
        'data/user'
    ]

    # ==================== CONNECT ====================
    CONNECT_NETWORK_CONFIG_PATHS = [
        'data/misc/net',
        'data/misc/dhcp',
        'data/misc/ethernet',
        'data/misc/vpn',
        'data/misc/apns',
        'data/misc/carrierid',
        'data/misc/network_watchlist',
        'data/misc/pageboost',
        'externaldump/net'
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
        'data/misc/shared_relro',
        'externaldump/radio'
    ]

    CONNECT_BT_CONFIG_PATHS = [
        'data/misc/bluedroid',
        'data/misc/bluetooth'
    ]

    CONNECT_BT_ACTION_PATHS = [
        'data/misc/profiles',
        'data/misc/keychain',
        'data/misc/audioserver'
    ]

    # ======================================================
    # ================ CLASS METHODS =======================
    # ======================================================

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
    def path_matches_pattern(path_str, patterns):
        """Kiểm tra path có khớp với regex pattern không"""
        path_lower = path_str.lower()
        for pattern in patterns:
            if re.search(pattern, path_lower):
                return True
        return False

    @staticmethod
    def extract_app_name(path_parts):
        """
        Trích xuất tên app, CHỈ TÌM TỪ THƯ MỤC GỐC TƯƠNG ĐỐI
        (Chỉ lấy data/data và data/user/* ở thư mục ngoài)
        """
        low_parts = [p.lower() for p in path_parts]
        num_parts = len(low_parts)

        if num_parts > 3 and low_parts[0] == 'data' and low_parts[1] == 'data':
            # path_parts[2] là <app_name>
            return path_parts[2]

        elif num_parts > 4 and low_parts[0] == 'data' and low_parts[1] == 'user':
            if low_parts[2].isdigit():
                # path_parts[3] là <app_name>
                return path_parts[3]

        return None

    # =========== HÀM ĐÃ CHỈNH MỚI (CÓ KIỂM TRA NỘI DUNG) =
    @staticmethod
    def get_file_extension_category(file_ext, file_path=None):
        """
        Xác định category của file dựa vào extension hoặc nội dung (nếu là .txt)
        """
        file_ext = file_ext.lower()

        #  Ưu tiên .log
        if file_ext == '.log':
            return 'Log'

        #  Kiểm tra .txt
        elif file_ext == '.txt' and file_path:

            # === [THÊM MỚI] 2.1: Kiểm tra tên file dump phổ biến (Nhanh và chính xác) ===
            file_name_lower = file_path.name.lower()
            if file_name_lower in [
                'statsd_dump.txt',
                'telephony_registry.txt',
                'interrupts.txt'
            ]:
                return 'Log'

            # === 2.2: Kiểm tra nội dung file (Nếu tên không khớp) ===
            try:
                head_lines = []
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for _ in range(200): # Đọc 200 dòng
                        line = f.readline()
                        if not line:
                            break
                        head_lines.append(line)
                head = ''.join(head_lines)

                head_lower = head.lower()
                if (
                    # Các cấp độ log thông thường
                    re.search(r'\b(INFO|ERROR|WARN|DEBUG|TRACE|FATAL)\b', head_lower, re.IGNORECASE)

                    # === [THÊM MỚI] Các từ khóa lỗi/dump phổ biến ===
                    or re.search(r'\b(FAIL|FAILURE|FAILED|EXCEPTION|CRASH)\b', head_lower, re.IGNORECASE)

                    # Ngày định dạng đầy đủ
                    or re.search(r'\d{4}-\d{2}-\d{2}', head_lower)

                    # Định dạng logcat: MM-DD HH:MM:SS.mmm
                    or re.search(r'\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3}', head_lower)

                    # Dòng mở đầu bằng dấu [
                    or re.search(r'^\[', head_lower, re.MULTILINE)

                    # Dấu hiệu file telephony
                    or 'local logs:' in head_lower or 'listen logs:' in head_lower
                ):
                    return 'Log'

            except Exception:
                pass

            # Nếu cả tên và nội dung đều không khớp, trả về 'Other'
            return 'Other'

        # Các định dạng khác
        elif file_ext in ['.db', '.sql', '.sqlite', '.sqlite3', '.db-wal', '.db-shm']:
            return 'Db'
        elif file_ext == '.json':
            return 'Json'
        elif file_ext == '.xml':
            return 'Xml'
        else:
            return 'Other'



    # ======================================================
    # =============== CLASSIFY FUNCTION ====================
    # ======================================================
    @staticmethod
    def classify(file_path: Path, input_root: Path):
        """
        Phân loại file và trả về thông tin
        Returns: {
            'main_category': 'System' | 'App' | 'Connect',
            'sub_category': str,
            'app_name': str | None,
            'file_type': str,
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
            'app_name': None,
            'file_type': 'Other',
        }

        # ==================== SYSTEM ====================
        if FileClassifier.path_matches_any(path_str, FileClassifier.SYSTEM_ACTION_LOG_PATHS):
            result['main_category'] = 'System'
            result['sub_category'] = 'Action'
            result['file_type'] = FileClassifier.get_file_extension_category(file_ext, file_path)
            return result

        if FileClassifier.path_matches_any(path_str, FileClassifier.SYSTEM_ACTION_DB_PATHS):
            result['main_category'] = 'System'
            result['sub_category'] = 'Action'
            result['file_type'] = FileClassifier.get_file_extension_category(file_ext, file_path)
            return result

        if FileClassifier.path_matches_any(path_str, FileClassifier.SYSTEM_CONFIG_PATHS) or \
           FileClassifier.path_matches_pattern(path_str, FileClassifier.SYSTEM_CONFIG_PATTERNS):
            result['main_category'] = 'System'
            result['sub_category'] = 'Config'
            result['file_type'] = 'Config'
            return result

        # ==================== CONNECT ====================
        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_NETWORK_CONFIG_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'Network'
            result['file_type'] = 'Config'
            return result

        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_NETWORK_ACTION_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'Network'
            result['file_type'] = FileClassifier.get_file_extension_category(file_ext, file_path)
            return result

        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_BT_CONFIG_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'BT'
            result['file_type'] = 'Config'
            return result

        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_BT_ACTION_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'BT'
            result['file_type'] = FileClassifier.get_file_extension_category(file_ext, file_path)
            return result

        # ==================== APP ====================
        app_name = FileClassifier.extract_app_name(path_parts)

        if app_name:
            result['main_category'] = 'App'
            result['sub_category'] = app_name
            result['app_name'] = app_name
            result['file_type'] = FileClassifier.get_file_extension_category(file_ext, file_path)
            return result

        # ==================== DEFAULT ====================
        result['main_category'] = 'System'
        result['sub_category'] = 'Action'
        result['file_type'] = 'Other'
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
                    'System': {
                        'Config': {'Config': 0},
                        'Action': {'Log': 0, 'Db': 0, 'Xml': 0, 'Other': 0}
                    },
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
        """Tạo cấu trúc thư mục Root (hard-coded)"""
        # System
        (root_dir / "System" / "Config").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Action" / "Log").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Action" / "Db").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Action" / "Xml").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Action" / "Other").mkdir(parents=True, exist_ok=True)

        # Connect/Network
        (root_dir / "Connect" / "Network" / "Config").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Log").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Db").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Json").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Xml").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network" / "Other").mkdir(parents=True, exist_ok=True)

        # Connect/BT
        (root_dir / "Connect" / "BT" / "Config").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Log").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Db").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Json").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Xml").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "BT" / "Other").mkdir(parents=True, exist_ok=True)

    def build_target_path(self, root_dir, classification):
        """Xây dựng đường dẫn thư mục đích"""
        main_cat = classification['main_category']
        sub_cat = classification['sub_category']
        file_type = classification['file_type']

        if main_cat == 'System':
            if sub_cat == 'Config':
                return root_dir / main_cat / sub_cat
            else:  # Action
                return root_dir / main_cat / sub_cat / file_type

        elif main_cat == 'Connect':
            if file_type == 'Config':
                return root_dir / main_cat / sub_cat / 'Config'
            else:
                return root_dir / main_cat / sub_cat / file_type

        elif main_cat == 'App':
            app_name = classification.get('app_name', 'Unknown')
            return root_dir / main_cat / app_name / file_type

        else:
            return root_dir / main_cat / sub_cat / file_type

    def process_file(self, source_path, target_dir, classification, log):
        """Xử lý và copy file"""
        try:
            target_file = target_dir / source_path.name
            shutil.copy2(source_path, target_file)
            log.write(f"[{classification['main_category']}/{classification['sub_category']}/{classification['file_type']}] {source_path.name}\n")
            return True
        except Exception as e:
            log.write(f"[ERROR] {source_path.name}: {str(e)}\n")
            return False

    def update_stats(self, stats, classification):
        """Update statistics"""
        main_cat = classification['main_category']
        sub_cat = classification.get('sub_category', 'Unknown')
        file_type = classification.get('file_type', 'Other')

        if main_cat == 'System':
            if sub_cat == 'Config':
                stats['System']['Config']['Config'] += 1
            else:  # Action
                if file_type not in stats['System']['Action']:
                    stats['System']['Action'][file_type] = 0
                stats['System']['Action'][file_type] += 1

        elif main_cat == 'Connect':
            if file_type not in stats['Connect'][sub_cat]:
                stats['Connect'][sub_cat][file_type] = 0
            stats['Connect'][sub_cat][file_type] += 1

        elif main_cat == 'App':
            app_name = classification.get('app_name', 'Unknown')
            if app_name not in stats['App']:
                stats['App'][app_name] = {'Log': 0, 'Db': 0, 'Json': 0, 'Xml': 0, 'Other': 0}
            if file_type not in stats['App'][app_name]:
                stats['App'][app_name][file_type] = 0
            stats['App'][app_name][file_type] += 1

    def write_statistics(self, log, stats, total_processed):
        """Ghi thống kê ra file log"""
        log.write("\n" + "=" * 80 + "\n")
        log.write("STATISTICS:\n")
        log.write("=" * 80 + "\n\n")

        # System
        log.write("SYSTEM:\n")
        log.write("  Config:\n")
        log.write(f"    Files: {stats['System']['Config']['Config']}\n")
        log.write("  Action:\n")
        for ftype in ['Log', 'Db', 'Xml', 'Other']:
            count = stats['System']['Action'].get(ftype, 0)
            log.write(f"    {ftype}: {count}\n")

        # App
        log.write("\nAPP:\n")
        for app_name in sorted(stats['App'].keys()):
            log.write(f"  {app_name}:\n")
            for ftype in ['Log', 'Db', 'Json', 'Xml', 'Other']:
                count = stats['App'][app_name].get(ftype, 0)
                log.write(f"    {ftype}: {count}\n")

        # Connect
        log.write("\nCONNECT:\n")
        for sub in ['Network', 'BT']:
            log.write(f"  {sub}:\n")
            for ftype in ['Config', 'Log', 'Db', 'Json', 'Xml', 'Other']:
                count = stats['Connect'][sub].get(ftype, 0)
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
