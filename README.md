# WinOptimizer

A comprehensive Windows system optimization suite with a modern terminal interface.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-10%2F11-0078D4?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## Features

### System Cleanup
- Clean temporary files from multiple locations
- Clear browser cache (Chrome, Edge, Firefox, Brave)
- Remove Windows log files
- Empty Recycle Bin
- Calculate space savings before cleanup

### Startup Manager
- View all startup programs
- Disable/enable startup items
- Manage registry-based startup entries
- Handle Startup folder items

### Performance Optimization
- Set High Performance power plan
- Disable unnecessary visual effects
- Optimize virtual memory (pagefile)
- Disable Windows Search indexing
- Gaming mode optimization

### Network Optimization
- Flush DNS cache
- Optimize TCP/IP settings
- Reset Winsock catalog
- Configure network adapter settings

### Privacy Settings
- Disable Windows telemetry
- Disable Cortana
- Disable advertising ID
- Disable activity history

### System Information
- CPU details and usage
- Memory usage and availability
- Disk space information
- Running processes monitor

### Gaming Optimization
- Enable Game Mode
- Optimize GPU scheduling
- Set high performance power plan
- Disable unnecessary background processes

## Installation

### Prerequisites
- Python 3.8 or higher
- Windows 10 or 11
- Administrator privileges (for some features)

### Install from source
```bash
git clone https://github.com/IVCS-R/WinOptimizer.git
cd WinOptimizer
pip install -r requirements.txt
python optimizer.py
```

### Quick install
```bash
pip install rich psutil
python optimizer.py
```

## Usage

Run the optimizer:
```bash
python optimizer.py
```

The application will display a menu with the following options:

```
╔══════════════════════════════════════════════════════════════╗
║                        MAIN MENU                            ║
╠══════════════════════════════════════════════════════════════╣
║  [1] System Cleanup        - Clean temp files & cache       ║
║  [2] Startup Manager       - Manage startup programs        ║
║  [3] Performance Optimization - Optimize system speed       ║
║  [4] Network Optimization  - Optimize network settings      ║
║  [5] Privacy Settings      - Configure privacy options      ║
║  [6] Gaming Optimization   - Optimize for gaming            ║
║  [7] System Information    - View system details            ║
║  [8] Backup & Restore      - Backup/restore settings        ║
║  [9] Full Optimization     - Run all optimizations          ║
║  [0] Exit                                                          ║
╚══════════════════════════════════════════════════════════════╝
```

## Features in Detail

### System Cleanup

The cleanup module scans multiple locations for files that can be safely removed:

- **Temp Files**: Windows temp folders, user temp folders
- **Browser Cache**: Cache directories for major browsers
- **Windows Logs**: System logs and crash dumps
- **Recycle Bin**: Already deleted files

Before cleaning, it shows you exactly how much space will be freed and creates a backup.

### Startup Manager

Manages programs that run automatically when Windows starts:

- **Registry-based**: Items in `HKCU\...\Run` and `HKLM\...\Run`
- **Startup Folder**: Programs in the Startup folder
- **Safe disabling**: Items are backed up before disabling

### Performance Optimization

Optimizes Windows settings for better performance:

- **Power Plan**: Sets High Performance mode
- **Visual Effects**: Disables animations and transparency
- **Virtual Memory**: Optimizes pagefile size
- **Search Indexing**: Disables background indexing

### Network Optimization

Improves network performance:

- **DNS Cache**: Clears stale DNS entries
- **TCP/IP**: Optimizes network stack settings
- **Winsock**: Resets network catalog

### Privacy Settings

Reduces Windows telemetry and tracking:

- **Telemetry**: Disables diagnostic data collection
- **Cortana**: Disables voice assistant
- **Advertising ID**: Stops personalized ads

## Backup & Restore

All optimizations create backups before making changes:

- Backups stored in `~/WinOptimizer_Backups/`
- Timestamped for easy identification
- Can be restored manually if needed

## Logs

Operations are logged to `~/WinOptimizer_Logs/`:

- Daily log files
- Timestamped entries
- Operation details

## Safety Features

- **Admin check**: Warns when not running as administrator
- **Backup creation**: Always backs up before changes
- **Confirmation prompts**: Asks before destructive operations
- **Error handling**: Graceful handling of failures
- **Logging**: All operations are logged

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool modifies system settings. While it creates backups and uses safe methods, use it at your own risk. Always create a system restore point before making significant changes.

## Acknowledgments

- [Rich](https://github.com/Textualize/rich) - For the beautiful terminal interface
- [psutil](https://github.com/giampaolo/psutil) - For system information
