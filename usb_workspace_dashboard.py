
import json
import os
import platform
import shutil
import string
import subprocess
import sys
from collections import Counter
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QUrl, Signal
from PySide6.QtGui import QAction, QDesktopServices, QFont
from PySide6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMessageBox,
    QPushButton, QScrollArea, QVBoxLayout, QWidget
)

APP_NAME = "USB Workspace Dashboard"
CONFIG_NAME = "dashboard.json"

CATEGORIES = [
    ("📁", "Documents", "PDF, DOCX, TXT, MD and office files"),
    ("🛠", "Applications", "Portable applications and launchable programs"),
    ("🧠", "AI & Projects", "AI workspaces, source repositories and projects"),
    ("📚", "Books", "PDF and EPUB reading material"),
    ("🐍", "Python", "Python scripts and Jupyter notebooks"),
    ("💻", "Linux", "ISO images, AppImages and Linux resources"),
    ("📊", "Data", "CSV, Excel, JSON and database files"),
    ("📦", "Archives", "ZIP, TAR, GZ and other archives"),
]

EXTENSION_GROUPS = {
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt", ".ppt", ".pptx"},
    "Books": {".epub", ".mobi", ".azw", ".azw3"},
    "Python": {".py", ".pyw", ".ipynb"},
    "Linux": {".iso", ".img", ".appimage", ".deb", ".rpm", ".sh"},
    "Data": {".csv", ".xlsx", ".xls", ".json", ".sqlite", ".sqlite3", ".db", ".parquet"},
    "Archives": {".zip", ".7z", ".rar", ".tar", ".gz", ".bz2", ".xz", ".tgz"},
    "Applications": {".exe", ".msi", ".bat", ".cmd", ".appimage"},
}

IGNORED_DIRS = {
    ".git", ".svn", ".hg", "__pycache__", "node_modules",
    "$recycle.bin", "system volume information"
}


def human_size(value):
    size = float(max(value, 0))
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} TB"


def open_path(path):
    path = Path(path)
    if not path.exists():
        return False
    try:
        if platform.system() == "Windows":
            os.startfile(str(path))
            return True
        if platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
            return True
        return bool(QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))))
    except OSError:
        return False


def discover_usb_roots():
    if platform.system() == "Windows":
        try:
            import ctypes
            mask = ctypes.windll.kernel32.GetLogicalDrives()
            get_type = ctypes.windll.kernel32.GetDriveTypeW
            roots = []
            for i in range(26):
                if mask & (1 << i):
                    drive = f"{string.ascii_uppercase[i]}:\\"
                    if get_type(drive) == 2 and Path(drive).is_dir():
                        roots.append(Path(drive))
            return roots
        except Exception:
            return []

    roots = []
    for base in (Path("/media"), Path("/run/media")):
        if base.exists():
            try:
                for user_dir in base.iterdir():
                    if user_dir.is_dir():
                        roots.extend(p for p in user_dir.iterdir() if p.is_dir() and p.exists())
            except OSError:
                pass
    return roots


def classify_file(path):
    suffix = path.suffix.lower()
    if suffix in EXTENSION_GROUPS["Applications"]:
        return "Applications"
    for category, extensions in EXTENSION_GROUPS.items():
        if suffix in extensions:
            return category
    return None


def project_type(directory):
    names = set()
    try:
        names = {p.name.lower() for p in directory.iterdir()}
    except OSError:
        return None

    if ".git" in names:
        if "pyproject.toml" in names or "requirements.txt" in names:
            return "Python / Git project"
        if "package.json" in names:
            return "Node / JavaScript project"
        return "Git project"
    if "pyproject.toml" in names or "requirements.txt" in names:
        return "Python project"
    if "package.json" in names:
        return "Node / JavaScript project"
    if "dockerfile" in names or "compose.yaml" in names or "docker-compose.yml" in names:
        return "Docker project"
    return None


class CategoryCard(QFrame):
    clicked = Signal(str)

    def __init__(self, icon, name, description):
        super().__init__()
        self.category = name
        self.setObjectName("CategoryCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(145)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)

        top = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setObjectName("CardIcon")
        top.addWidget(icon_label)
        top.addStretch()

        self.count = QLabel("0")
        self.count.setObjectName("CardCount")
        top.addWidget(self.count)
        layout.addLayout(top)

        title = QLabel(name)
        title.setObjectName("CardTitle")
        layout.addWidget(title)

        desc = QLabel(description)
        desc.setObjectName("CardDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        layout.addStretch()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.category)
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.root = None
        self.usb_mode = False
        self.cards = []
        self.search_results = []
        self.items = []
        self.category_items = {category[1]: [] for category in CATEGORIES}

        self.setWindowTitle(APP_NAME)
        self.resize(1500, 940)
        self.setMinimumSize(1100, 720)

        self.build_ui()
        self.detect_workspace()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_drive_state)
        self.timer.start(5000)

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main = QVBoxLayout(central)
        main.setContentsMargins(24, 22, 24, 20)
        main.setSpacing(14)

        hero = QFrame()
        hero.setObjectName("Hero")
        h = QHBoxLayout(hero)
        h.setContentsMargins(26, 22, 26, 22)

        text = QVBoxLayout()
        title = QLabel("USB Workspace")
        title.setObjectName("HeroTitle")
        subtitle = QLabel("Your portable files, applications and projects — discovered automatically")
        subtitle.setObjectName("HeroSubtitle")
        text.addWidget(title)
        text.addWidget(subtitle)
        h.addLayout(text)
        h.addStretch()

        self.drive_combo = QComboBox()
        self.drive_combo.setMinimumWidth(290)
        self.drive_combo.currentIndexChanged.connect(self.drive_changed)
        h.addWidget(self.drive_combo)

        choose = QPushButton("Choose USB / Folder")
        choose.clicked.connect(self.choose_root)
        h.addWidget(choose)

        self.status_badge = QLabel("STARTING")
        self.status_badge.setObjectName("StatusBadge")
        h.addWidget(self.status_badge)
        main.addWidget(hero)

        info = QFrame()
        info.setObjectName("InfoPanel")
        il = QHBoxLayout(info)
        self.root_label = QLabel("No workspace selected")
        self.root_label.setObjectName("RootLabel")
        il.addWidget(self.root_label)
        il.addStretch()
        self.scan_label = QLabel("Scan: —")
        il.addWidget(self.scan_label)
        self.storage_label = QLabel("Storage: —")
        il.addWidget(self.storage_label)
        main.addWidget(info)

        controls = QHBoxLayout()
        label = QLabel("Search")
        label.setObjectName("SectionLabel")
        controls.addWidget(label)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search files, folders, projects or extensions…")
        self.search.textChanged.connect(self.search_workspace)
        controls.addWidget(self.search, 1)

        refresh = QPushButton("↻ Rescan")
        refresh.clicked.connect(self.refresh_all)
        controls.addWidget(refresh)
        main.addLayout(controls)

        section = QLabel("Discovered Workspace")
        section.setObjectName("SectionTitle")
        main.addWidget(section)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.card_container = QWidget()
        self.card_grid = QGridLayout(self.card_container)
        self.card_grid.setContentsMargins(0, 0, 0, 0)
        self.card_grid.setSpacing(14)
        scroll.setWidget(self.card_container)
        main.addWidget(scroll, 1)

        bottom = QHBoxLayout()

        results_box = QFrame()
        results_box.setObjectName("ResultsBox")
        rl = QVBoxLayout(results_box)
        self.results_title = QLabel("Search / Category Results")
        self.results_title.setObjectName("ResultsTitle")
        rl.addWidget(self.results_title)
        self.result_list = QListWidget()
        self.result_list.setMinimumHeight(125)
        self.result_list.itemDoubleClicked.connect(self.open_result)
        rl.addWidget(self.result_list)
        bottom.addWidget(results_box, 1)

        quick = QFrame()
        quick.setObjectName("QuickPanel")
        ql = QVBoxLayout(quick)
        ql.addWidget(QLabel("Quick actions"))
        for text, callback in (
            ("📂 Open Workspace Root", self.open_root),
            ("⚙ Dashboard Configuration", self.open_config),
        ):
            button = QPushButton(text)
            button.clicked.connect(callback)
            ql.addWidget(button)
        bottom.addWidget(quick)
        main.addLayout(bottom)

        menu = self.menuBar().addMenu("&Workspace")

        action = QAction("Choose USB / Folder", self)
        action.triggered.connect(self.choose_root)
        menu.addAction(action)

        action = QAction("Rescan", self)
        action.setShortcut("F5")
        action.triggered.connect(self.refresh_all)
        menu.addAction(action)

        action = QAction("Open Workspace Root", self)
        action.triggered.connect(self.open_root)
        menu.addAction(action)

        action = QAction("Exit", self)
        action.setShortcut("Ctrl+Q")
        action.triggered.connect(self.close)
        menu.addAction(action)

        self.statusBar().showMessage("Starting dashboard…")

    def detect_workspace(self):
        roots = discover_usb_roots()
        self.drive_combo.blockSignals(True)
        self.drive_combo.clear()

        for root in roots:
            if root.exists():
                self.drive_combo.addItem(f"{root}  • USB / removable", str(root))

        self.drive_combo.blockSignals(False)

        if roots:
            self.set_root(roots[0], True)
        else:
            local_root = Path(__file__).resolve().parent
            self._add_workspace(local_root, "Local dashboard folder")
            self.set_root(local_root, False)

    def _add_workspace(self, root, label=None):
        root = Path(root)
        if not root.exists() or not root.is_dir():
            return

        for i in range(self.drive_combo.count()):
            if self.drive_combo.itemData(i) == str(root):
                self.drive_combo.setCurrentIndex(i)
                return

        self.drive_combo.addItem(label or str(root), str(root))
        self.drive_combo.setCurrentIndex(self.drive_combo.count() - 1)

    def choose_root(self):
        path = QFileDialog.getExistingDirectory(self, "Choose USB Drive or Workspace Folder")
        if path:
            root = Path(path)
            self._add_workspace(root)
            self.set_root(root, root in discover_usb_roots())

    def drive_changed(self, index):
        if index >= 0:
            value = self.drive_combo.itemData(index)
            if value:
                root = Path(value)
                if root.exists():
                    self.set_root(root, root in discover_usb_roots())

    def set_root(self, root, usb=False):
        root = Path(root)
        if not root.exists() or not root.is_dir():
            fallback = Path(__file__).resolve().parent
            if fallback.exists():
                root = fallback
                usb = False
            else:
                self.status_badge.setText("NO WORKSPACE")
                return

        self.root = root
        self.usb_mode = usb
        self.root_label.setText(f"Workspace:  {root}")
        self.status_badge.setText("USB READY" if usb else "LOCAL WORKSPACE")
        self.refresh_all()

    def config_path(self):
        return self.root / CONFIG_NAME if self.root else None

    def load_config(self):
        path = self.config_path()
        if not path or not path.exists():
            return
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
            loaded = []
            for item in config.get("categories", []):
                if item.get("name"):
                    loaded.append((
                        item.get("icon", "📁"),
                        item["name"],
                        item.get("description", "")
                    ))
            if loaded:
                # Config can customize descriptions/icons while discovery remains automatic.
                by_name = {x[1]: x for x in loaded}
                self.display_categories = [
                    by_name.get(x[1], x) for x in CATEGORIES
                ]
                return
        except Exception:
            pass
        self.display_categories = CATEGORIES

    def scan_workspace(self):
        self.items = []
        self.category_items = {category[1]: [] for category in CATEGORIES}

        if not self.root:
            return

        try:
            for path in self.root.rglob("*"):
                try:
                    if any(part.lower() in IGNORED_DIRS for part in path.parts):
                        continue

                    category = None
                    if path.is_dir():
                        ptype = project_type(path)
                        if ptype:
                            category = "AI & Projects"
                    elif path.is_file():
                        category = classify_file(path)

                    if category:
                        self.items.append((path, category))
                        self.category_items.setdefault(category, []).append(path)
                except (OSError, PermissionError):
                    continue
        except (OSError, PermissionError):
            pass

    def build_cards(self):
        while self.card_grid.count():
            item = self.card_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.cards.clear()

        for index, (icon, name, desc) in enumerate(self.display_categories):
            card = CategoryCard(icon, name, desc)
            count = len(self.category_items.get(name, []))
            card.count.setText(f"{count} item{'s' if count != 1 else ''}")
            card.clicked.connect(self.show_category)
            self.cards.append(card)
            self.card_grid.addWidget(card, index // 4, index % 4)

    def show_category(self, category):
        self.result_list.clear()
        self.search_results = list(self.category_items.get(category, []))
        self.results_title.setText(f"{category} • {len(self.search_results)} discovered item(s)")

        for path in self.search_results[:250]:
            relative = str(path.relative_to(self.root))
            self.result_list.addItem(relative)

        self.statusBar().showMessage(
            f"{category}: {len(self.search_results)} item(s)"
            + (" • first 250 shown" if len(self.search_results) > 250 else "")
        )

    def search_workspace(self, text):
        self.result_list.clear()
        self.search_results = []

        needle = text.strip().lower()
        if not needle or not self.root:
            self.results_title.setText("Search / Category Results")
            return

        for path, category in self.items:
            try:
                relative = str(path.relative_to(self.root))
                if needle in path.name.lower() or needle in relative.lower() or needle in category.lower():
                    self.search_results.append(path)
                    if len(self.search_results) >= 250:
                        break
            except ValueError:
                continue

        for path in self.search_results:
            self.result_list.addItem(str(path.relative_to(self.root)))

        self.results_title.setText(
            f"Search Results • {len(self.search_results)}"
            + ("+ • first 250 shown" if len(self.search_results) >= 250 else "")
        )
        self.statusBar().showMessage(
            f"Search: {len(self.search_results)} result(s)"
        )

    def open_result(self, item):
        index = self.result_list.row(item)
        if 0 <= index < len(self.search_results):
            path = self.search_results[index]
            if not open_path(path):
                QMessageBox.warning(self, "Open failed", f"Could not open:\n{path}")

    def open_root(self):
        if self.root and not open_path(self.root):
            QMessageBox.warning(self, "Open failed", f"Could not open:\n{self.root}")

    def open_config(self):
        if not self.root:
            return
        path = self.config_path()
        if not path.exists():
            config = {
                "categories": [
                    {"icon": icon, "name": name, "description": desc}
                    for icon, name, _, desc in CATEGORIES
                ]
            }
            path.write_text(
                json.dumps(config, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        open_path(path)

    def refresh_all(self):
        if not self.root or not self.root.exists():
            self.detect_workspace()
            return

        self.load_config()
        self.scan_workspace()
        self.build_cards()
        self.refresh_stats()

        self.result_list.clear()
        self.search_results = []
        self.results_title.setText("Search / Category Results")
        self.scan_label.setText(f"Scan: {len(self.items)} discovered item(s)")
        self.statusBar().showMessage("Workspace rescanned")

    def refresh_stats(self):
        if not self.root:
            return

        try:
            usage = shutil.disk_usage(self.root)
            used = usage.total - usage.free
            percent = used / usage.total * 100 if usage.total else 0
            self.storage_label.setText(
                f"Storage: {human_size(used)} / {human_size(usage.total)} • {percent:.0f}% used"
            )
        except OSError:
            self.storage_label.setText("Storage: unavailable")
            self.status_badge.setText("DRIVE OFFLINE")

    def refresh_drive_state(self):
        if not self.root:
            return
        if self.root.exists():
            self.refresh_stats()
        else:
            self.status_badge.setText("DRIVE OFFLINE")
            self.storage_label.setText("Storage: unavailable")


STYLE = r"""
QMainWindow, QWidget {
    background: #f4f7fb;
    color: #172033;
}
QMenuBar {
    background: white;
    padding: 6px;
    border-bottom: 1px solid #dbe2ec;
}
QFrame#Hero {
    background: #172033;
    border-radius: 18px;
}
QLabel#HeroTitle {
    color: white;
    font-size: 29px;
    font-weight: 800;
}
QLabel#HeroSubtitle {
    color: #cbd5e1;
    font-size: 13px;
}
QLabel#StatusBadge {
    background: #e7f7ee;
    color: #176b3a;
    border-radius: 14px;
    padding: 9px 14px;
    font-weight: 800;
}
QFrame#InfoPanel, QFrame#QuickPanel, QFrame#ResultsBox {
    background: white;
    border: 1px solid #dbe2ec;
    border-radius: 12px;
}
QLabel#RootLabel {
    font-weight: 750;
}
QLabel#SectionLabel {
    font-weight: 750;
}
QLabel#SectionTitle {
    font-size: 18px;
    font-weight: 800;
}
QLabel#ResultsTitle {
    font-size: 13px;
    font-weight: 800;
}
QLineEdit, QComboBox {
    background: white;
    border: 1px solid #cfd8e3;
    border-radius: 9px;
    padding: 9px 11px;
}
QPushButton {
    background: white;
    border: 1px solid #cfd8e3;
    border-radius: 9px;
    padding: 9px 14px;
    font-weight: 650;
}
QPushButton:hover {
    background: #edf3fb;
}
QFrame#CategoryCard {
    background: white;
    border: 1px solid #dbe2ec;
    border-radius: 16px;
}
QFrame#CategoryCard:hover {
    background: #f8fbff;
    border: 1px solid #9fb9d8;
}
QLabel#CardIcon {
    font-size: 30px;
}
QLabel#CardTitle {
    font-size: 18px;
    font-weight: 800;
}
QLabel#CardDesc {
    color: #697586;
    font-size: 12px;
}
QLabel#CardCount {
    color: #536174;
    font-size: 11px;
    font-weight: 700;
}
QListWidget {
    background: white;
    border: 1px solid #dbe2ec;
    border-radius: 10px;
    padding: 5px;
}
QListWidget::item {
    padding: 7px;
    border-radius: 7px;
}
QListWidget::item:selected {
    background: #dce8f7;
    color: #172033;
}
QStatusBar {
    background: white;
}
QScrollArea {
    background: transparent;
    border: none;
}
"""

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
