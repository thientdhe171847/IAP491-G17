from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QFileDialog
import os
import shutil
import sqlite3
import csv
from pathlib import Path
from datetime import datetime
import re


class FileClassifier:
    """Phân loại file theo cấu trúc mới từ đặc tả Word"""

    # ==================== CONNECT ====================
    CONNECT_WIFI_PATHS = [
        'vendor/etc/wifi',
        'system/etc/wifi',
        'data/misc/wifi',
        'vendor/firmware/wlan',
        'vendor/firmware/wifi',
        'efs/wifi'
    ]

    CONNECT_WIFI_EXTS = {
        'conf': ['.conf', '.ini', '.cnf', '.cfg'],
        'xml': ['.xml'],
        'db': ['.db', '.sqlite', '.db-wal', '.db-shm'],
        'json': ['.json'],
        'log': ['.log'],
        'other': ['.txt', '.bin', '.dat', '.nvram', '.nvm', '.cal', '.clm_blob',
                  '.clmb', '.hcf', '.sdb', '.info', '.t', '.csv', '.properties',
                  '.bak', '.old', '.rc', '.sh', '.pem', '.der', '.dump', '.img',
                  '.elf', '.hdr', '.mbn', '.crc', '.mac', '.addr']
    }

    CONNECT_BLUETOOTH_PATHS = [
        'vendor/etc/bluetooth',
        'system/etc/bluetooth',
        'data/misc/bluetooth',
        'data/misc/bluedroid',
        'vendor/firmware/bt',
        'vendor/firmware/bluetooth',
        'efs/bluetooth'
    ]

    CONNECT_BLUETOOTH_EXTS = {
        'conf': ['.conf', '.ini', '.cfg'],
        'xml': ['.xml'],
        'db': ['.db', '.sqlite', '.db-wal', '.db-shm'],
        'json': ['.json'],
        'log': ['.log'],
        'other': ['.txt', '.dat', '.bin', '.hcd', '.mbn', '.btfw', '.patch', '.prop',
                  '.rc', '.sh', '.pem', '.der', '.mac', '.addr', '.bak', '.old',
                  '.btsnoop', '.hci', '.key', '.csr', '.dump', '.bdaddr', '.nvram',
                  '.nvm', '.cal', '.crc', '.img', '.elf', '.hdr']
    }

    CONNECT_TELEPHONY_PATHS = [
        'vendor/etc/radio',
        'carrier',
        'vendor/etc/audio',
        'vendor/firmware/modem',
        'vendor/firmware/mcfg',
        'vendor/firmware/mbn',
        'vendor/firmware/qcril',
        'efs/imei',
        'efs/FactoryApp'
    ]

    CONNECT_TELEPHONY_EXTS = {
        'conf': ['.conf', '.cfg', '.ini'],
        'xml': ['.xml'],
        'db': ['.db', '.sqlite', '.db-wal', '.db-shm'],
        'json': ['.json'],
        'log': ['.log'],
        'other': ['.mbn', '.mcfg', '.mdt', '.dat', '.bin', '.img', '.txt', '.prop',
                  '.pem', '.der', '.cer', '.png', '.jpg', '.zip', '.tar', '.gz',
                  '.bak', '.old', '.acdb', '.csv', '.pcm', '.wav', '.elf', '.sig',
                  '.md5', '.sha1', '.sha256', '.nv', '.nvram', '.nvm', '.key',
                  '.cert', '.mac', '.addr', '.cal', '.crc']
    }

    # ==================== APP ====================
    APP_PATHS = [
        'data/app',
        'data/data'
    ]

    APP_DATABASE_PATHS = ['databases']
    APP_SHARED_PREFS_PATHS = ['shared_prefs']
    APP_FILES_PATHS = ['files']
    APP_CACHE_PATHS = ['cache']

    APP_EXTS = {
        'db': ['.db', '.sqlite', '.sqlite3', '.db-wal', '.db-shm', '.sqlite-wal',
               '.sqlite-shm', '.db-journal', '.sqlite-journal', '.journal', '.wal',
               '.shm', '.realm', '.realm.lock', '.realm.management'],
        'xml': ['.xml'],
        'apk': ['.apk'],
        'json': ['.json'],
        'log': ['.log', '.txt'],
        'other': ['.bak', '.old', '.tmp', '.sql', '.enc', '.aes', '.gz', '.zip',
                  '.csv', '.cfg', '.conf', '.ini', '.properties', '.dat', '.bin',
                  '.proto', '.pb', '.obb', '.dex', '.jar', '.so', '.pdf', '.doc',
                  '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.html', '.htm', '.js',
                  '.css', '.7z', '.rar', '.tar', '.bz2', '.xz', '.lz4', '.temp',
                  '.partial', '.download', '.cache', '.thumb', '.nomedia', '.jpg',
                  '.jpeg', '.png', '.webp', '.gif', '.heic', '.mp3', '.m4a', '.aac',
                  '.wav', '.flac', '.ogg', '.opus', '.amr', '.3gp', '.mp4', '.mkv',
                  '.webm', '.mov', '.m4v', '.pem', '.der', '.crt', '.cer', '.key',
                  '.keystore', '.p12', '.pfx', '.sig', '.md5', '.sha1', '.sha256',
                  '.idx', '.index', '.lru', '.br']
    }

    # ==================== STORAGE ====================
    STORAGE_GALLERY_PATHS = [
        'storage/emulated',
        'storage/',
        'DCIM',
        'Pictures',
        'Screenshots',
        'ScreenShot',
        'ScreenCapture'
    ]

    STORAGE_GALLERY_EXTS = {
        'jpg': ['.jpg', '.jpeg'],
        'png': ['.png'],
        'webp': ['.webp'],
        'gif': ['.gif'],
        'heic': ['.heic', '.heif'],
        'other': ['.bmp', '.dng', '.raw']
    }

    STORAGE_AUDIO_PATHS = [
        'Music',
        'Podcasts',
        'Audiobooks',
        'Ringtones',
        'Alarms',
        'Notifications',
        'Recordings',
        'Voice Recorder',
        'SoundRecorder',
        'CallRecordings',
        'Call'
    ]

    STORAGE_AUDIO_EXTS = {
        'mp3': ['.mp3'],
        'm4a': ['.m4a'],
        'wav': ['.wav'],
        'other': ['.aac', '.flac', '.ogg', '.opus', '.amr', '.3gp']
    }

    STORAGE_VIDEO_PATHS = [
        'Movies',
        'DCIM/Camera',
        'DCIM/ScreenRecorder',
        'Movies/ScreenRecords',
        'ScreenRecords'
    ]

    STORAGE_VIDEO_EXTS = {
        'mp4': ['.mp4'],
        'mkv': ['.mkv'],
        'mov': ['.mov'],
        'other': ['.webm', '.3gp', '.m4v']
    }

    STORAGE_DOWNLOAD_PATHS = [
        'Download',
        'Documents'
    ]

    STORAGE_DOWNLOAD_EXTS = {
        'apk': ['.apk', '.xapk'],
        'pdf': ['.pdf'],
        'doc': ['.doc', '.docx'],
        'xls': ['.xls', '.xlsx'],
        'other': ['.ppt', '.pptx', '.zip', '.rar', '.7z', '.txt', '.csv',
                  '.json', '.xml', '.tar', '.gz']
    }

    # ==================== SYSTEM ====================
    SYSTEM_CONFIG_PATHS = [
        'system/etc',
        'system/app',
        'system/priv-app',
        'system/framework',
        'system/lib',
        'system/lib64',
        'system/media',
        'system/fonts',
        'system/usr',
        'product',
        'vendor',
        'odm',
        'oem',
        'apex',
        'linkerconfig',
        'data/system'
    ]

    SYSTEM_CONFIG_EXTS = {
        'prop': ['.prop'],
        'xml': ['.xml'],
        'conf': ['.conf', '.cfg', '.ini'],
        'json': ['.json'],
        'log': ['.log'],
        'other': ['.rc', '.txt', '.pem', '.der', '.crt', '.cer', '.bc', '.cil',
                  '.policy', '.sh', '.apk', '.jar', '.so', '.ogg', '.wav', '.mp3',
                  '.mp4', '.m4a', '.png', '.jpg', '.webp', '.ttf', '.otf', '.ttc',
                  '.kl', '.kcm', '.idc', '.dat', '.arsc', '.te', '.mapping', '.bin',
                  '.mbn', '.img', '.elf', '.hdr', '.nvm', '.nvram', '.cal',
                  '.clm_blob', '.clmb', '.hcf', '.sdb', '.info', '.t', '.ucode',
                  '.bak', '.old', '.list']
    }

    SYSTEM_DIAGNOSTIC_PATHS = [
        'cache/recovery',
        'cache/ota',
        'metadata/ota',
        'data/user_de/0/com.android.shell/files/bugreports'
    ]

    SYSTEM_DIAGNOSTIC_EXTS = {
        'log': ['.log', '.txt'],
        'other': ['.zip', '.img', '.bin', '.json', '.xml', '.sig', '.dat', '.tmp', '.partial']
    }

    @staticmethod
    def extract_package_name(path_parts):
        """Extract Android package name from path"""
        # Pattern 1: /data/data/com.xxx.yyy/
        for i, part in enumerate(path_parts):
            if part.lower() in ['data'] and i + 1 < len(path_parts):
                if path_parts[i + 1].lower() == 'data' and i + 2 < len(path_parts):
                    potential_package = path_parts[i + 2]
                    if '.' in potential_package and re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$', potential_package, re.IGNORECASE):
                        return potential_package

        # Pattern 2: /data/app/com.xxx.yyy-...=/
        for i, part in enumerate(path_parts):
            if 'data' in part.lower() and i + 1 < len(path_parts):
                if 'app' in path_parts[i + 1].lower() and i + 2 < len(path_parts):
                    next_part = path_parts[i + 2]
                    # Remove trailing identifiers
                    if '-' in next_part or '=' in next_part:
                        package = re.split(r'[-=]', next_part)[0]
                        if '.' in package and re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$', package, re.IGNORECASE):
                            return package

        # Pattern 3: Simple package name in path
        for part in path_parts:
            if '.' in part and not part.startswith('.'):
                if re.match(r'^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*){2,}$', part, re.IGNORECASE):
                    return part

        return None

    @staticmethod
    def get_file_type_from_extension(file_ext, ext_dict):
        """Tìm file_type từ extension trong dictionary"""
        for file_type, extensions in ext_dict.items():
            if file_ext.lower() in extensions:
                return file_type
        return 'other'

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
        Phân loại file và trả về thông tin
        Returns: {
            'main_category': 'System' | 'App' | 'Connect' | 'Storage',
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
        path_str_lower = path_str.lower()
        file_ext = file_path.suffix.lower()
        file_name = file_path.stem.lower()

        result = {
            'main_category': None,
            'sub_category': None,
            'app_name': None,
            'file_type': 'other',
        }

        # ==================== CONNECT ====================
        # Connect/Network (Wi-Fi)
        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_WIFI_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'Network'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.CONNECT_WIFI_EXTS
            )
            return result

        # Connect/Bluetooth
        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_BLUETOOTH_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'Bluetooth'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.CONNECT_BLUETOOTH_EXTS
            )
            return result

        # Connect/Telephony
        if FileClassifier.path_matches_any(path_str, FileClassifier.CONNECT_TELEPHONY_PATHS):
            result['main_category'] = 'Connect'
            result['sub_category'] = 'Telephony'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.CONNECT_TELEPHONY_EXTS
            )
            return result

        # ==================== SYSTEM ====================
        # System/Diagnostic
        if FileClassifier.path_matches_any(path_str, FileClassifier.SYSTEM_DIAGNOSTIC_PATHS):
            result['main_category'] = 'System'
            result['sub_category'] = 'Diagnostic'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.SYSTEM_DIAGNOSTIC_EXTS
            )
            return result

        # System/Config
        if FileClassifier.path_matches_any(path_str, FileClassifier.SYSTEM_CONFIG_PATHS):
            result['main_category'] = 'System'
            result['sub_category'] = 'Config'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.SYSTEM_CONFIG_EXTS
            )
            return result

        # ==================== APP ====================
        # Kiểm tra xem có phải app path không
        package_name = FileClassifier.extract_package_name(path_parts)

        if package_name or FileClassifier.path_matches_any(path_str, FileClassifier.APP_PATHS):
            result['main_category'] = 'App'
            result['app_name'] = package_name if package_name else 'Diagnostic'
            result['sub_category'] = package_name if package_name else 'Diagnostic'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.APP_EXTS
            )
            return result

        # ==================== STORAGE ====================
        # Storage/Gallery
        if FileClassifier.path_matches_any(path_str, FileClassifier.STORAGE_GALLERY_PATHS):
            if file_ext in [ext for exts in FileClassifier.STORAGE_GALLERY_EXTS.values() for ext in exts]:
                result['main_category'] = 'Storage'
                result['sub_category'] = 'Gallery'
                result['file_type'] = FileClassifier.get_file_type_from_extension(
                    file_ext, FileClassifier.STORAGE_GALLERY_EXTS
                )
                return result

        # Storage/Audio
        if FileClassifier.path_matches_any(path_str, FileClassifier.STORAGE_AUDIO_PATHS):
            if file_ext in [ext for exts in FileClassifier.STORAGE_AUDIO_EXTS.values() for ext in exts]:
                result['main_category'] = 'Storage'
                result['sub_category'] = 'Audio'
                result['file_type'] = FileClassifier.get_file_type_from_extension(
                    file_ext, FileClassifier.STORAGE_AUDIO_EXTS
                )
                return result

        # Storage/Video
        if FileClassifier.path_matches_any(path_str, FileClassifier.STORAGE_VIDEO_PATHS):
            if file_ext in [ext for exts in FileClassifier.STORAGE_VIDEO_EXTS.values() for ext in exts]:
                result['main_category'] = 'Storage'
                result['sub_category'] = 'Video'
                result['file_type'] = FileClassifier.get_file_type_from_extension(
                    file_ext, FileClassifier.STORAGE_VIDEO_EXTS
                )
                return result

        # Storage/Download
        if FileClassifier.path_matches_any(path_str, FileClassifier.STORAGE_DOWNLOAD_PATHS):
            result['main_category'] = 'Storage'
            result['sub_category'] = 'Download'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.STORAGE_DOWNLOAD_EXTS
            )
            return result

        # ==================== DEFAULT BY EXTENSION ====================
        # Nếu không match path, phân loại theo extension
        # Gallery
        all_gallery_exts = [ext for exts in FileClassifier.STORAGE_GALLERY_EXTS.values() for ext in exts]
        if file_ext in all_gallery_exts:
            result['main_category'] = 'Storage'
            result['sub_category'] = 'Gallery'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.STORAGE_GALLERY_EXTS
            )
            return result

        # Audio
        all_audio_exts = [ext for exts in FileClassifier.STORAGE_AUDIO_EXTS.values() for ext in exts]
        if file_ext in all_audio_exts:
            result['main_category'] = 'Storage'
            result['sub_category'] = 'Audio'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.STORAGE_AUDIO_EXTS
            )
            return result

        # Video
        all_video_exts = [ext for exts in FileClassifier.STORAGE_VIDEO_EXTS.values() for ext in exts]
        if file_ext in all_video_exts:
            result['main_category'] = 'Storage'
            result['sub_category'] = 'Video'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.STORAGE_VIDEO_EXTS
            )
            return result

        # Download
        all_download_exts = [ext for exts in FileClassifier.STORAGE_DOWNLOAD_EXTS.values() for ext in exts]
        if file_ext in all_download_exts:
            result['main_category'] = 'Storage'
            result['sub_category'] = 'Download'
            result['file_type'] = FileClassifier.get_file_type_from_extension(
                file_ext, FileClassifier.STORAGE_DOWNLOAD_EXTS
            )
            return result

        # ==================== FINAL DEFAULT ====================
        # Không phân loại được -> App/Diagnostic/other
        result['main_category'] = 'App'
        result['sub_category'] = 'Diagnostic'
        result['file_type'] = 'other'
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
            case_dir = input_path.parent / self.case_id
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
                    'System': {'Config': {}, 'Diagnostic': {}},
                    'App': {},
                    'Connect': {'Network': {}, 'Bluetooth': {}, 'Telephony': {}},
                    'Storage': {'Gallery': {}, 'Audio': {}, 'Video': {}, 'Download': {}}
                }

                # Track which source directories we've already copied for App/Diagnostic
                copied_dirs = set()

                for file_path in all_files:
                    if self.is_cancelled:
                        self.finished.emit(False, "Cancelled by user")
                        return

                    try:
                        classification = FileClassifier.classify(file_path, input_path)

                        # Special handling: For App/Diagnostic when input is a folder, copy entire source folder
                        if self.mode == "folder" and classification['main_category'] == 'App' and classification['sub_category'] == 'Diagnostic':
                            source_dir = file_path.parent
                            # Use resolved path string as set key to avoid duplicates
                            source_key = str(source_dir.resolve())
                            try:
                                rel_dir = source_dir.relative_to(input_path)
                            except Exception:
                                # Fallback to using the final part of the directory
                                rel_dir = Path(source_dir.name)
                            dest_dir = root_dir / 'App' / 'Diagnostic' / rel_dir
                            if source_key not in copied_dirs:
                                try:
                                    # Copy the whole directory (merge into dest if exists)
                                    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
                                    log.write(f"[COPYDIR] App/Diagnostic: {source_dir} → {dest_dir}\n")
                                    copied_dirs.add(source_key)
                                    success = True
                                except Exception as e:
                                    log.write(f"[ERROR] Failed to copy directory {source_dir}: {str(e)}\n")
                                    success = False
                            else:
                                # Already copied this directory; treat as success for stats/progress
                                success = True

                            if success:
                                # Update stats per-file so counts reflect processed files
                                self.update_stats(stats, classification)
                            # Continue processing next file (we don't copy individual files here)
                            # processed increment happens below
                        else:
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
        """Tạo cấu trúc thư mục Root"""
        (root_dir / "System" / "Config").mkdir(parents=True, exist_ok=True)
        (root_dir / "System" / "Diagnostic").mkdir(parents=True, exist_ok=True)
        (root_dir / "App" / "Diagnostic").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Network").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Bluetooth").mkdir(parents=True, exist_ok=True)
        (root_dir / "Connect" / "Telephony").mkdir(parents=True, exist_ok=True)
        (root_dir / "Storage" / "Gallery").mkdir(parents=True, exist_ok=True)
        (root_dir / "Storage" / "Audio").mkdir(parents=True, exist_ok=True)
        (root_dir / "Storage" / "Video").mkdir(parents=True, exist_ok=True)
        (root_dir / "Storage" / "Download").mkdir(parents=True, exist_ok=True)

    def build_target_path(self, root_dir, classification):
        """Xây dựng đường dẫn thư mục đích"""
        main_cat = classification['main_category']
        sub_cat = classification['sub_category']
        file_type = classification['file_type']

        if main_cat == 'App' and classification['app_name']:
            return root_dir / main_cat / sub_cat / file_type
        else:
            return root_dir / main_cat / sub_cat / file_type

    def process_file(self, source_path, target_dir, classification, log):
        """Xử lý và copy file"""
        try:
            file_type = classification['file_type']
            target_file = target_dir / source_path.name

            if file_type == 'db':
                csv_target = target_dir / f"{source_path.stem}.csv"
                if self.convert_sqlite_to_csv(str(source_path), str(csv_target)):
                    log.write(f"[DB→CSV] {classification['main_category']}/{classification['sub_category']}: {source_path.name} → {csv_target.name}\n")
                    return True
                else:
                    shutil.copy2(source_path, target_file)
                    log.write(f"[COPY] {classification['main_category']}/{classification['sub_category']}: {source_path.name} (not a valid SQLite DB)\n")
                    return True
            else:
                shutil.copy2(source_path, target_file)
                log.write(f"[{classification['main_category']}/{classification['sub_category']}/{file_type}] {source_path.name}\n")
                return True
        except Exception as e:
            log.write(f"[ERROR] {source_path.name}: {str(e)}\n")
            return False

    def convert_sqlite_to_csv(self, db_path, csv_path):
        """Convert SQLite database to CSV"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                conn.close()
                return False
            table_name = tables[0][0]
            cursor.execute(f"SELECT * FROM {table_name}")
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([description[0] for description in cursor.description])
                csv_writer.writerows(cursor.fetchall())
            conn.close()
            return True
        except Exception:
            return False

    def update_stats(self, stats, classification):
        """Update statistics"""
        main_cat = classification['main_category']
        sub_cat = classification['sub_category']
        file_type = classification['file_type']

        if main_cat == 'System':
            if file_type not in stats['System'][sub_cat]:
                stats['System'][sub_cat][file_type] = 0
            stats['System'][sub_cat][file_type] += 1
        elif main_cat == 'Connect':
            if file_type not in stats['Connect'][sub_cat]:
                stats['Connect'][sub_cat][file_type] = 0
            stats['Connect'][sub_cat][file_type] += 1
        elif main_cat == 'Storage':
            if file_type not in stats['Storage'][sub_cat]:
                stats['Storage'][sub_cat][file_type] = 0
            stats['Storage'][sub_cat][file_type] += 1
        elif main_cat == 'App':
            # Ensure app entry exists
            app_name = classification.get('app_name') or 'Diagnostic'
            if app_name not in stats['App']:
                stats['App'][app_name] = {}
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
        for sub in ['Config', 'Diagnostic']:
            if stats['System'][sub]:
                log.write(f"  {sub}:\n")
                for ftype, count in sorted(stats['System'][sub].items()):
                    log.write(f"    {ftype}: {count}\n")

        # App
        log.write("\nAPP:\n")
        for app_name in sorted(stats['App'].keys()):
            types = stats['App'][app_name]
            log.write(f"  {app_name}:\n")
            for ftype, count in sorted(types.items()):
                log.write(f"    {ftype}: {count}\n")

        # Connect
        log.write("\nCONNECT:\n")
        for sub in ['Network', 'Bluetooth', 'Telephony']:
            if stats['Connect'][sub]:
                log.write(f"  {sub}:\n")
                for ftype, count in sorted(stats['Connect'][sub].items()):
                    log.write(f"    {ftype}: {count}\n")

        # Storage
        log.write("\nSTORAGE:\n")
        for sub in ['Gallery', 'Audio', 'Video', 'Download']:
            if stats['Storage'][sub]:
                log.write(f"  {sub}:\n")
                for ftype, count in sorted(stats['Storage'][sub].items()):
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
