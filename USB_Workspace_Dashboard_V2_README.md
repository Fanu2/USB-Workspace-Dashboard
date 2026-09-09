# USB Workspace Dashboard V2

**A beautiful, clickable PySide6 dashboard for a USB drive or portable workspace.**

USB Workspace Dashboard turns a large collection of files, applications, documents, projects and utilities into a simple visual workspace.

Instead of manually browsing the USB with Windows Explorer, the dashboard scans the workspace and groups useful content into clickable categories.

---

## 1. What It Does

The dashboard automatically discovers useful content on the selected USB drive or workspace folder.

It provides:

- Automatic USB/removable-drive detection
- Safe local-folder fallback for testing
- Automatic content discovery
- Clickable category cards
- Workspace-wide search
- Double-click launching/opening
- USB storage information
- Project detection
- Portable configuration
- Offline operation

The application does **not require an internet connection**.

---

## 2. Main Dashboard

The dashboard provides eight main categories:

| Category | What it discovers |
|---|---|
| 📁 Documents | PDF, DOCX, TXT, Markdown and office files |
| 🛠 Applications | EXE, MSI, BAT, CMD and AppImage |
| 🧠 AI & Projects | Git, Python, Node/JavaScript and Docker projects |
| 📚 Books | EPUB and other ebook formats |
| 🐍 Python | Python scripts and Jupyter notebooks |
| 💻 Linux | ISO, IMG, AppImage, DEB, RPM and shell scripts |
| 📊 Data | CSV, Excel, JSON and database files |
| 📦 Archives | ZIP, 7z, RAR, TAR, GZ and related archives |

The numbers displayed on the cards represent the number of discovered items.

---

## 3. Requirements

### Windows

Python 3.10 or newer is recommended.

PySide6 is required.

Install the dependency with:

```powershell
python -m pip install -r requirements.txt
```

If PySide6 is already installed, no additional installation is normally required.

---

## 4. Running the Dashboard

Open PowerShell in the application directory.

Example:

```powershell
cd C:\Users\singh\Downloads\USB_Workspace_Dashboard_V2
```

Then run:

```powershell
python usb_workspace_dashboard.py
```

The dashboard window should open.

---

## 5. Selecting a USB Drive

When the application starts, it looks for available removable drives.

For example:

```text
H:\  • USB / removable
```

If a USB drive is detected, it is automatically selected.

The status indicator shows:

```text
USB READY
```

If no USB drive is connected, the dashboard uses its own folder as a safe testing workspace.

The status indicator then shows:

```text
LOCAL WORKSPACE
```

You can also manually select a location using:

**Choose USB / Folder**

---

## 6. Automatic Discovery

V2 is different from the earlier dashboard versions.

You do **not** need to create folders such as:

```text
Documents
Books
Applications
Python
Linux
Data
Archives
```

The application examines the actual contents of the workspace.

For example, if your USB contains:

```text
H:\
├── Camera
├── Camera.tar.gz
├── MyBook.epub
├── Report.pdf
├── Project-Athena
├── notebook.ipynb
└── utility.exe
```

the dashboard can classify those items automatically.

---

## 7. Project Detection

The dashboard also looks for common project indicators.

It can recognize projects containing files such as:

```text
.git
pyproject.toml
requirements.txt
package.json
Dockerfile
compose.yaml
docker-compose.yml
```

Examples include:

### Python project

```text
project/
├── pyproject.toml
├── src/
└── tests/
```

### Git project

```text
project/
├── .git/
├── README.md
└── src/
```

### Node / JavaScript project

```text
project/
├── package.json
└── src/
```

### Docker project

```text
project/
├── Dockerfile
└── compose.yaml
```

These are presented under **AI & Projects**.

---

## 8. Category Cards

Clicking a category card displays the discovered items in the lower results panel.

For example:

```text
Click: 📚 Books

        ↓

Books • 24 discovered item(s)

MyBook.epub
Reference.pdf
History.epub
...
```

This gives the dashboard a launcher-like workflow.

---

## 9. Opening Files

Double-click an item in the results panel.

The application asks Windows or the current operating system to open the item using the normal associated application.

Examples:

```text
PDF       → PDF reader
EPUB      → ebook application
XLSX      → spreadsheet application
EXE       → Windows application
Folder    → File Explorer
```

The dashboard does not attempt to replace the applications already installed on the computer.

---

## 10. Search

Use the **Search** box near the top of the dashboard.

You can search by:

- Filename
- Folder name
- Relative path
- Category

For example:

```text
athena
```

may find:

```text
Projects\Project-Athena
AI\Athena-Notes
...
```

Another example:

```text
pdf
```

can find filenames or paths containing `pdf`.

Up to 250 matching results are displayed.

---

## 11. Rescan

Click:

**↻ Rescan**

or press:

```text
F5
```

The dashboard scans the workspace again.

Use this after:

- Copying new files to the USB
- Removing files
- Creating a project
- Adding documents
- Connecting a different USB drive

---

## 12. Storage Information

The dashboard displays the storage information for the selected workspace.

Example:

```text
Storage: 36.9 GB / 200.0 GB • 18% used
```

This is useful when the dashboard is being used as a portable USB control center.

---

## 13. Quick Actions

### Open Workspace Root

Opens the selected USB/workspace in the operating system's file manager.

### Dashboard Configuration

Opens:

```text
dashboard.json
```

The configuration file travels with the dashboard.

---

## 14. dashboard.json

The dashboard includes a portable configuration file:

```text
dashboard.json
```

This allows the dashboard layout to be customized without changing the Python program.

The default configuration contains the standard categories.

Example:

```json
{
    "categories": [
        {
            "icon": "📁",
            "name": "Documents",
            "path": "Documents",
            "description": "PDF, DOCX, TXT, MD and office files"
        }
    ]
}
```

The discovery engine remains automatic; the configuration primarily controls dashboard presentation.

---

## 15. Files Skipped During Scanning

To reduce noise and avoid unnecessarily scanning large development directories, the dashboard skips common folders such as:

```text
.git
.svn
.hg
__pycache__
node_modules
$Recycle.Bin
System Volume Information
```

This is especially useful for development-heavy USB drives.

---

## 16. Recommended Portable USB Layout

The dashboard does not require a fixed layout, but a clean USB can be organized approximately like this:

```text
USB\
│
├── Applications\
├── Documents\
├── Books\
├── AI\
├── Python\
├── Linux\
├── Data\
├── Archives\
├── Projects\
│
├── USB_Workspace_Dashboard\
│   ├── usb_workspace_dashboard.py
│   ├── dashboard.json
│   └── README.md
│
└── ...
```

The important point is that **V2 can discover existing content even when the folders are not organized this way**.

---

## 17. Portable Use

The intended long-term use is:

```text
USB Drive
    ↓
USB Workspace Dashboard
    ↓
Discover USB contents
    ↓
Present useful categories
    ↓
Click
    ↓
Open / launch the selected item
```

The dashboard itself can be stored on the USB.

For example:

```text
H:\USB_Workspace_Dashboard\
```

When moved to another computer, choose the USB drive and the dashboard can work with that computer's available applications and file associations.

---

## 18. Current V2 Scope

V2 is intentionally a foundation for a more capable portable workspace.

Current capabilities:

- USB detection
- Workspace selection
- Automatic scanning
- Content classification
- Project detection
- Search
- Category browsing
- File/folder opening
- Storage information
- Portable configuration

---

## 19. Planned Direction

Possible future versions can add:

### V3 — Portable Application Launcher

Automatically recognize launchable applications and provide dedicated application tiles.

Possible examples:

```text
🧠 Project Athena
🐍 Python Utility
📓 Jupyter Notebook
🛠 Portable Tool
💻 Linux Utility
```

### V4 — Smart Project Workspace

Recognize project types and provide actions such as:

```text
Open Project
Open Folder
Open Terminal
Run Python
Open Jupyter
Open Git Repository
```

### V5 — Personal USB Control Center

The eventual dashboard could become a complete portable workspace containing:

- Applications
- Projects
- Documents
- Books
- AI tools
- Development tools
- Utilities
- Search
- Favorites
- Recent items
- Storage monitoring
- Custom launchers

The goal is to make the USB behave less like a collection of folders and more like a **portable personal computing workspace**.

---

## 20. Troubleshooting

### PySide6 is missing

Run:

```powershell
python -m pip install PySide6
```

### The application opens but no USB is selected

Use:

**Choose USB / Folder**

and select the USB drive.

### A category shows zero items

This means the scanner did not find supported files for that category.

Press:

```text
F5
```

to rescan.

### A file does not open

The dashboard uses the operating system's normal file associations. Make sure an appropriate application is installed for that file type.

### USB was disconnected

Reconnect it and use **Refresh/Rescan** or select the USB again.

---

## 21. Project Philosophy

USB Workspace Dashboard is designed around a simple idea:

> **The USB should be a workspace, not just a storage device.**

The dashboard provides a visual layer over the files already present on the drive while keeping the underlying files completely ordinary and accessible.

It is:

- Portable
- Offline-first
- Simple
- Non-destructive
- File-system friendly
- Built with PySide6
- Designed to grow incrementally

---

## 22. License / Personal Use

This project is currently intended as a personal utility and development project.

No cloud service or external account is required.
