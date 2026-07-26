<div align="center">

# WinOptimizer

**Advanced Windows System Optimization Suite**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white)](https://microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-00FF00?style=for-the-badge)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-FCD936?style=for-the-badge)](https://github.com/IVCS-R/WinOptimizer)
[![PRs](https://img.shields.io/badge/PRs-Welcome-00FF00?style=for-the-badge)](CONTRIBUTING.md)

Clean. Optimize. Perform.

</div>

---

## What is WinOptimizer?

A comprehensive, terminal-based Windows optimization tool built in Python. One-click system cleanup, gaming mode, startup management, and more — all with animated progress indicators and a clean interface.

```
+========================================================+
|                      MAIN MENU                          |
+========================================================+
|  [1] Optimize           - Full system optimization      |
|  [2] Gaming Mode        - Optimize for gaming           |
|  [3] Startup            - Manage startup programs       |
|  [4] System Info        - View system details           |
|  [5] Backup             - Restore point / registry      |
|  [6] Settings           - Individual tweaks             |
|  [0] Exit                                               |
+========================================================+
```

---

## Features

<details>
<summary><b>System Optimization</b></summary>

- Clean temporary files from multiple locations
- Clear browser cache (Chrome, Edge, Firefox, Brave)
- Remove Windows log files and crash dumps
- Empty Recycle Bin
- Calculate space savings before cleanup
- Set High Performance power plan
- Disable unnecessary visual effects
- Optimize virtual memory (pagefile)
- Disable Windows Search indexing

</details>

<details>
<summary><b>Gaming Mode</b></summary>

- Enable Game Mode
- Optimize GPU scheduling
- Set high performance power plan
- Disable unnecessary background processes
- Maximize system resources for gaming

</details>

<details>
<summary><b>Startup Manager</b></summary>

- View all startup programs
- Disable/enable startup items
- Handle registry-based startup entries
- Manage Startup folder items

</details>

<details>
<summary><b>System Information</b></summary>

- CPU details and real-time usage
- Memory usage and availability
- Disk space information
- Running processes monitor
- Network adapter details

</details>

<details>
<summary><b>Backup & Restore</b></summary>

- Create Windows restore points
- Export/Import registry backups
- Timestamped for easy identification
- Stored in `~/WinOptimizer_Backups/`

</details>

<details>
<summary><b>Individual Settings</b></summary>

- Disable Windows telemetry
- Disable Cortana
- Disable advertising ID
- Disable activity history
- Flush DNS cache
- Optimize TCP/IP settings
- Reset Winsock catalog

</details>

---

## Installation

### Option 1: Portable (recommended)

```bash
git clone https://github.com/IVCS-R/WinOptimizer.git
cd WinOptimizer
pip install -r requirements.txt
python optimizer.py
```

### Option 2: NSIS Installer

Download `WinOptimizer_Setup.exe` from [Releases](https://github.com/IVCS-R/WinOptimizer/releases) and run the installer.

### Option 3: PyInstaller Build

Download `WinOptimizer_Installer.exe` from [Releases](https://github.com/IVCS-R/WinOptimizer/releases) — no Python required.

### Quick Run

```bash
pip install rich psutil
python optimizer.py
```

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| Windows | 10 / 11 |
| rich | Latest |
| psutil | Latest |

> Some features require Administrator privileges. The tool will warn you if not running as admin.

---

## Safety

- **Admin check**: Warns when not running as administrator
- **Backup creation**: Always backs up before changes
- **Confirmation prompts**: Asks before destructive operations
- **Error handling**: Graceful handling of failures
- **Logging**: All operations are logged to `~/WinOptimizer_Logs/`

---

## Project Structure

```
WinOptimizer/
├── optimizer.py            # Main application
├── install_verbose.py      # Verbose installer (terminal output)
├── uninstall_verbose.py    # Verbose uninstaller
├── installer.nsi           # NSIS installer script
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
├── README.md               # This file
└── dist/                   # Built executables
    ├── WinOptimizer_Installer.exe
    └── WinOptimizer_Uninstaller.exe
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Disclaimer

This tool modifies system settings. While it creates backups and uses safe methods, use it at your own risk. Always create a system restore point before making significant changes.

---

<div align="center">

**Made with Python and Rich**

[![Rich](https://img.shields.io/badge/Rich-Terminal_UI-0D1117?style=for-the-badge&logo=python&logoColor=white)](https://github.com/Textualize/rich)
[![psutil](https://img.shields.io/badge/psutil-System-0D1117?style=for-the-badge&logo=python&logoColor=white)](https://github.com/giampaolo/psutil)

</div>
