# This Python file uses the following encoding: utf-8
import sys

from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine

# === Thêm dòng này để import backend ===
from backend import Backend

if __name__ == "__main__":
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Lấy đường dẫn thư mục hiện tại chứa main.py
    current_dir = Path(__file__).resolve().parent

    # Thêm đường dẫn QML vào import path để tìm module Constants
    engine.addImportPath(str(current_dir))

    # === Đăng ký backend vào QML context ===
    backend = Backend()
    engine.rootContext().setContextProperty("backend", backend)

    # Load main.qml
    qml_file = current_dir / "main.qml"
    engine.load(qml_file)

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
