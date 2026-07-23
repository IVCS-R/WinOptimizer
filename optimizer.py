#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════╗
║                    WINOPTIMIZER v1.0.0                                    ║
║              Advanced Windows System Optimization Suite                  ║
║                                                                          ║
║  Features:                                                               ║
║  - System cleanup (temp files, cache, logs)                              ║
║  - Startup management                                                    ║
║  - Performance optimization                                              ║
║  - Network optimization                                                  ║
║  - Privacy settings                                                      ║
║  - System information                                                    ║
║  - Gaming optimization                                                   ║
║  - Backup & restore                                                      ║
║                                                                          ║
║  Author: IVCS                                                            ║
║  License: MIT                                                            ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import json
import shutil
import subprocess
import ctypes
import winreg
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import hashlib

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich import box
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.text import Text
    from rich.layout import Layout
    from rich import box

# ── Constants ──────────────────────────────────────────────────────────────────
VERSION = "1.0.0"
APP_NAME = "WinOptimizer"
BACKUP_DIR = Path.home() / "WinOptimizer_Backups"
LOG_DIR = Path.home() / "WinOptimizer_Logs"

# ── Console setup ──────────────────────────────────────────────────────────────
console = Console()

# ── Utility Functions ──────────────────────────────────────────────────────────
def is_admin() -> bool:
    """Check if running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    """Restart the script with administrator privileges."""
    if not is_admin():
        console.print("[yellow]Requesting administrator privileges...[/yellow]")
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except:
            console.print("[red]Failed to get administrator privileges.[/red]")
            console.print("[yellow]Please run as administrator for full functionality.[/yellow]")

def create_backup(items: List[str], backup_name: str) -> bool:
    """Create a backup of specified items."""
    try:
        backup_path = BACKUP_DIR / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        for item in items:
            item_path = Path(item)
            if item_path.exists():
                if item_path.is_file():
                    shutil.copy2(item_path, backup_path)
                elif item_path.is_dir():
                    shutil.copytree(item_path, backup_path / item_path.name, dirs_exist_ok=True)
        
        console.print(f"[green]✓ Backup created: {backup_path}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Backup failed: {e}[/red]")
        return False

def log_operation(operation: str, details: str):
    """Log an operation to file."""
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"optimizer_{datetime.now().strftime('%Y%m%d')}.log"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {operation}: {details}\n")

def get_size_format(size_bytes: int) -> str:
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def get_directory_size(path: Path) -> int:
    """Calculate total size of a directory."""
    total_size = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
    except:
        pass
    return total_size

# ── System Cleanup Module ──────────────────────────────────────────────────────
class SystemCleanup:
    """System cleanup and maintenance operations."""
    
    TEMP_DIRS = [
        Path(os.environ.get('TEMP', '')),
        Path(os.environ.get('TMP', '')),
        Path(os.environ.get('LOCALAPPDATA', '')) / 'Temp',
        Path('C:\\Windows\\Temp'),
        Path('C:\\Windows\\Prefetch'),
        Path('C:\\Windows\\SoftwareDistribution\\Download'),
    ]
    
    BROWSER_CACHE_DIRS = [
        Path.home() / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Cache',
        Path.home() / 'AppData' / 'Local' / 'Google' / 'Chrome' / 'User Data' / 'Default' / 'Code Cache',
        Path.home() / 'AppData' / 'Local' / 'Microsoft' / 'Edge' / 'User Data' / 'Default' / 'Cache',
        Path.home() / 'AppData' / 'Local' / 'Mozilla' / 'Firefox' / 'Profiles',
        Path.home() / 'AppData' / 'Local' / 'BraveSoftware' / 'Brave-Browser' / 'User Data' / 'Default' / 'Cache',
    ]
    
    @staticmethod
    def calculate_cleanup_size() -> Dict[str, int]:
        """Calculate total size of files that can be cleaned."""
        sizes = {
            'temp': 0,
            'browser_cache': 0,
            'windows_logs': 0,
            'recycle_bin': 0,
        }
        
        # Temp files
        for temp_dir in SystemCleanup.TEMP_DIRS:
            if temp_dir.exists():
                sizes['temp'] += get_directory_size(temp_dir)
        
        # Browser cache
        for cache_dir in SystemCleanup.BROWSER_CACHE_DIRS:
            if cache_dir.exists():
                sizes['browser_cache'] += get_directory_size(cache_dir)
        
        # Windows logs
        log_dirs = [
            Path('C:\\Windows\\Logs'),
            Path.home() / 'AppData' / 'Local' / 'CrashDumps',
        ]
        for log_dir in log_dirs:
            if log_dir.exists():
                sizes['windows_logs'] += get_directory_size(log_dir)
        
        # Recycle Bin
        try:
            sizes['recycle_bin'] = get_directory_size(Path('C:\\$Recycle.Bin'))
        except:
            pass
        
        return sizes
    
    @staticmethod
    def clean_temp_files() -> Tuple[int, List[str]]:
        """Clean temporary files."""
        cleaned = []
        total_size = 0
        
        for temp_dir in SystemCleanup.TEMP_DIRS:
            if temp_dir.exists():
                try:
                    for item in temp_dir.rglob('*'):
                        try:
                            if item.is_file():
                                size = item.stat().st_size
                                item.unlink()
                                total_size += size
                                cleaned.append(str(item))
                        except:
                            pass
                except:
                    pass
        
        return total_size, cleaned
    
    @staticmethod
    def clean_browser_cache() -> Tuple[int, List[str]]:
        """Clean browser cache."""
        cleaned = []
        total_size = 0
        
        for cache_dir in SystemCleanup.BROWSER_CACHE_DIRS:
            if cache_dir.exists():
                try:
                    size = get_directory_size(cache_dir)
                    shutil.rmtree(cache_dir)
                    total_size += size
                    cleaned.append(str(cache_dir))
                except:
                    pass
        
        return total_size, cleaned
    
    @staticmethod
    def clean_windows_logs() -> Tuple[int, List[str]]:
        """Clean Windows log files."""
        cleaned = []
        total_size = 0
        
        log_dirs = [
            Path('C:\\Windows\\Logs'),
            Path.home() / 'AppData' / 'Local' / 'CrashDumps',
        ]
        
        for log_dir in log_dirs:
            if log_dir.exists():
                try:
                    for item in log_dir.rglob('*.log'):
                        try:
                            size = item.stat().st_size
                            item.unlink()
                            total_size += size
                            cleaned.append(str(item))
                        except:
                            pass
                except:
                    pass
        
        return total_size, cleaned
    
    @staticmethod
    def empty_recycle_bin() -> Tuple[int, bool]:
        """Empty the Recycle Bin."""
        try:
            size = get_directory_size(Path('C:\\$Recycle.Bin'))
            subprocess.run(['rd', '/s', '/q', 'C:\\$Recycle.Bin'], 
                         shell=True, capture_output=True)
            return size, True
        except:
            return 0, False
    
    @staticmethod
    def run_full_cleanup(callback=None) -> Dict:
        """Run a complete system cleanup."""
        results = {
            'temp': {'size': 0, 'files': 0},
            'browser': {'size': 0, 'dirs': 0},
            'logs': {'size': 0, 'files': 0},
            'recycle': {'size': 0, 'success': False},
        }
        
        if callback:
            callback("Cleaning temp files...")
        size, files = SystemCleanup.clean_temp_files()
        results['temp'] = {'size': size, 'files': len(files)}
        
        if callback:
            callback("Cleaning browser cache...")
        size, dirs = SystemCleanup.clean_browser_cache()
        results['browser'] = {'size': size, 'dirs': len(dirs)}
        
        if callback:
            callback("Cleaning Windows logs...")
        size, files = SystemCleanup.clean_windows_logs()
        results['logs'] = {'size': size, 'files': len(files)}
        
        if callback:
            callback("Emptying Recycle Bin...")
        size, success = SystemCleanup.empty_recycle_bin()
        results['recycle'] = {'size': size, 'success': success}
        
        return results

# ── Startup Manager Module ─────────────────────────────────────────────────────
class StartupManager:
    """Manage startup programs and services."""
    
    REGISTRY_PATHS = {
        'user_run': r'Software\Microsoft\Windows\CurrentVersion\Run',
        'user_runonce': r'Software\Microsoft\Windows\CurrentVersion\RunOnce',
        'machine_run': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
        'machine_runonce': r'SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',
        'startup_folder': str(Path.home() / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'),
    }
    
    @staticmethod
    def get_startup_items() -> List[Dict]:
        """Get list of startup items."""
        items = []
        
        # Registry items
        for location, reg_path in StartupManager.REGISTRY_PATHS.items():
            if location == 'startup_folder':
                continue
            try:
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER if 'user' in location else winreg.HKEY_LOCAL_MACHINE,
                    reg_path,
                    0,
                    winreg.KEY_READ
                )
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        items.append({
                            'name': name,
                            'command': value,
                            'location': location,
                            'enabled': True
                        })
                        i += 1
                    except WindowsError:
                        break
                winreg.CloseKey(key)
            except:
                pass
        
        # Startup folder items
        startup_folder = Path(StartupManager.REGISTRY_PATHS['startup_folder'])
        if startup_folder.exists():
            for item in startup_folder.iterdir():
                if item.is_file():
                    items.append({
                        'name': item.stem,
                        'command': str(item),
                        'location': 'startup_folder',
                        'enabled': True
                    })
        
        return items
    
    @staticmethod
    def disable_startup_item(item: Dict) -> bool:
        """Disable a startup item."""
        try:
            if item['location'] == 'startup_folder':
                # Move to backup location
                backup_dir = BACKUP_DIR / 'startup_items'
                backup_dir.mkdir(parents=True, exist_ok=True)
                source = Path(item['command'])
                if source.exists():
                    shutil.move(str(source), str(backup_dir / source.name))
                    return True
            else:
                # Remove from registry
                location = item['location']
                reg_path = StartupManager.REGISTRY_PATHS[location]
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER if 'user' in location else winreg.HKEY_LOCAL_MACHINE,
                    reg_path,
                    0,
                    winreg.KEY_SET_VALUE
                )
                winreg.DeleteValue(key, item['name'])
                winreg.CloseKey(key)
                return True
        except Exception as e:
            console.print(f"[red]Error disabling {item['name']}: {e}[/red]")
            return False
    
    @staticmethod
    def enable_startup_item(item: Dict) -> bool:
        """Enable a startup item."""
        try:
            if item['location'] == 'startup_folder':
                # Move back from backup
                backup_dir = BACKUP_DIR / 'startup_items'
                source = backup_dir / Path(item['command']).name
                if source.exists():
                    shutil.move(str(source), item['command'])
                    return True
            else:
                # Add to registry
                location = item['location']
                reg_path = StartupManager.REGISTRY_PATHS[location]
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER if 'user' in location else winreg.HKEY_LOCAL_MACHINE,
                    reg_path,
                    0,
                    winreg.KEY_SET_VALUE
                )
                winreg.SetValueEx(key, item['name'], 0, winreg.REG_SZ, item['command'])
                winreg.CloseKey(key)
                return True
        except Exception as e:
            console.print(f"[red]Error enabling {item['name']}: {e}[/red]")
            return False

# ── Performance Optimizer Module ───────────────────────────────────────────────
class PerformanceOptimizer:
    """Optimize system performance settings."""
    
    @staticmethod
    def set_high_performance_power_plan() -> bool:
        """Set power plan to High Performance."""
        try:
            subprocess.run(['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'],
                         capture_output=True, shell=True)
            return True
        except:
            return False
    
    @staticmethod
    def disable_visual_effects() -> bool:
        """Disable unnecessary visual effects for better performance."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects',
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, 'VisualFXSetting', 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(key)
            
            # Disable transparency
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize',
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, 'EnableTransparency', 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            return True
        except:
            return False
    
    @staticmethod
    def optimize_virtual_memory() -> bool:
        """Optimize virtual memory settings."""
        try:
            # Get system drive
            system_drive = os.environ.get('SystemDrive', 'C:')
            
            # Set optimal pagefile size (1.5x RAM)
            import psutil
            ram_gb = psutil.virtual_memory().total / (1024**3)
            pagefile_size = int(ram_gb * 1.5 * 1024)  # In MB
            
            subprocess.run([
                'wmic', 'computersystem', 'where', 'name="%computername%"',
                'set', f'AutomaticManagedPagefile=False'
            ], capture_output=True, shell=True)
            
            subprocess.run([
                'wmic', 'pagefileset', 'where', f"name='{system_drive}\\\\pagefile.sys'",
                'set', f'InitialSize={pagefile_size}', f'MaximumSize={pagefile_size}'
            ], capture_output=True, shell=True)
            
            return True
        except:
            return False
    
    @staticmethod
    def disable_search_indexing() -> bool:
        """Disable Windows Search indexing service."""
        try:
            subprocess.run(['sc', 'config', 'WSearch', 'start=', 'disabled'],
                         capture_output=True, shell=True)
            subprocess.run(['net', 'stop', 'WSearch'],
                         capture_output=True, shell=True)
            return True
        except:
            return False
    
    @staticmethod
    def optimize_system_for_gaming() -> bool:
        """Optimize system settings for gaming."""
        try:
            # Enable Game Mode
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\GameBar',
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, 'AllowAutoGameMode', 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, 'AutoGameModeEnabled', 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
            
            # Optimize GPU scheduling
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SYSTEM\CurrentControlSet\Control\GraphicsDrivers',
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, 'HwSchMode', 0, winreg.REG_DWORD, 2)
            winreg.CloseKey(key)
            
            return True
        except:
            return False

# ── Network Optimizer Module ───────────────────────────────────────────────────
class NetworkOptimizer:
    """Optimize network settings."""
    
    @staticmethod
    def flush_dns() -> bool:
        """Flush DNS cache."""
        try:
            subprocess.run(['ipconfig', '/flushdns'], capture_output=True, shell=True)
            return True
        except:
            return False
    
    @staticmethod
    def optimize_tcp_ip() -> bool:
        """Optimize TCP/IP settings."""
        try:
            # Reset TCP/IP stack
            subprocess.run(['netsh', 'int', 'ip', 'reset'], capture_output=True, shell=True)
            
            # Optimize network adapter settings
            commands = [
                'netsh int tcp set global autotuninglevel=normal',
                'netsh int tcp set global chimney=enabled',
                'netsh int tcp set global dca=enabled',
                'netsh int tcp set global netdma=enabled',
                'netsh int tcp set global ecncapability=disabled',
                'netsh int tcp set global timestamps=disabled',
            ]
            
            for cmd in commands:
                subprocess.run(cmd.split(), capture_output=True, shell=True)
            
            return True
        except:
            return False
    
    @staticmethod
    def reset_winsock() -> bool:
        """Reset Winsock catalog."""
        try:
            subprocess.run(['netsh', 'winsock', 'reset'], capture_output=True, shell=True)
            return True
        except:
            return False

# ── Privacy Optimizer Module ───────────────────────────────────────────────────
class PrivacyOptimizer:
    """Optimize privacy settings."""
    
    @staticmethod
    def disable_telemetry() -> bool:
        """Disable Windows telemetry."""
        try:
            # Disable telemetry service
            subprocess.run(['sc', 'config', 'DiagTrack', 'start=', 'disabled'],
                         capture_output=True, shell=True)
            subprocess.run(['net', 'stop', 'DiagTrack'],
                         capture_output=True, shell=True)
            
            # Disable activity history
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'Policies\Microsoft\Windows\System',
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, 'EnableActivityFeed', 0, winreg.REG_DWORD, 0)
            winreg.SetValueEx(key, 'PublishUserActivities', 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            
            return True
        except:
            return False
    
    @staticmethod
    def disable_cortana() -> bool:
        """Disable Cortana."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r'SOFTWARE\Policies\Microsoft\Windows\Windows Search',
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, 'AllowCortana', 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            return True
        except:
            return False
    
    @staticmethod
    def disable_advertising_id() -> bool:
        """Disable advertising ID."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo',
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, 'Enabled', 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
            return True
        except:
            return False

# ── System Information Module ──────────────────────────────────────────────────
class SystemInfo:
    """Get system information."""
    
    @staticmethod
    def get_system_info() -> Dict:
        """Get comprehensive system information."""
        import psutil
        
        info = {
            'os': {
                'name': os.environ.get('OS', 'Unknown'),
                'version': os.environ.get('OS_VERSION', 'Unknown'),
                'architecture': os.environ.get('PROCESSOR_ARCHITECTURE', 'Unknown'),
            },
            'cpu': {
                'name': os.environ.get('PROCESSOR_IDENTIFIER', 'Unknown'),
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'usage': psutil.cpu_percent(interval=1),
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'used': psutil.virtual_memory().used,
                'percent': psutil.virtual_memory().percent,
            },
            'disk': {},
        }
        
        # Disk information
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                info['disk'][partition.device] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': usage.percent,
                }
            except:
                pass
        
        return info
    
    @staticmethod
    def get_running_processes() -> List[Dict]:
        """Get list of running processes."""
        import psutil
        
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append(proc.info)
            except:
                pass
        
        return sorted(processes, key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)

# ── Main Optimizer Class ───────────────────────────────────────────────────────
class WinOptimizer:
    """Main optimizer class."""
    
    def __init__(self):
        self.cleanup = SystemCleanup()
        self.startup = StartupManager()
        self.performance = PerformanceOptimizer()
        self.network = NetworkOptimizer()
        self.privacy = PrivacyOptimizer()
        self.system = SystemInfo()
    
    def display_banner(self):
        """Display application banner."""
        banner = """
[bold green]
╔══════════════════════════════════════════════════════════════════════════╗
║                                                                          ║
║   ███╗   ██╗██╗███╗   ██╗██╗     ██╗ ██████╗ ██████╗  ██████╗ ██╗   ██╗███╗   ██╗███████╗  ║
║   ████╗  ██║██║████╗  ██║██║     ██║██╔═══██╗██╔══██╗██╔═══██╗██║   ██║████╗  ██║██╔════╝  ║
║   ██╔██╗ ██║██║██╔██╗ ██║██║     ██║██║   ██║██║  ██║██║   ██║██║   ██║██╔██╗ ██║█████╗    ║
║   ██║╚██╗██║██║██║╚██╗██║██║     ██║██║   ██║██║  ██║██║   ██║██║   ██║██║╚██╗██║██╔══╝    ║
║   ██║ ╚████║██║██║ ╚████║███████╗██║╚██████╔╝██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║███████╗  ║
║   ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝╚═╝  ╚═══╝╚══════╝  ║
║                                                                          ║
║                    Advanced Windows Optimization Suite                   ║
║                              Version {version}                            ║
╚══════════════════════════════════════════════════════════════════════════╝
[/bold green]"""
        console.print(banner.format(version=VERSION))
    
    def display_menu(self):
        """Display main menu."""
        menu = """
[bold cyan]╔══════════════════════════════════════════════════════════════╗
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
║  [0] Exit                                                            ║
╚══════════════════════════════════════════════════════════════╝[/bold cyan]"""
        console.print(menu)
    
    def run_cleanup(self):
        """Run system cleanup."""
        console.print("\n[bold yellow]═══ System Cleanup ═══[/bold yellow]")
        
        # Calculate size
        with console.status("[bold green]Calculating cleanup size...[/bold green]"):
            sizes = self.cleanup.calculate_cleanup_size()
        
        total = sum(sizes.values())
        
        # Display sizes
        table = Table(title="Cleanup Preview", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Size", style="green")
        
        table.add_row("Temp Files", get_size_format(sizes['temp']))
        table.add_row("Browser Cache", get_size_format(sizes['browser_cache']))
        table.add_row("Windows Logs", get_size_format(sizes['windows_logs']))
        table.add_row("Recycle Bin", get_size_format(sizes['recycle_bin']))
        table.add_row("[bold]Total[/bold]", f"[bold]{get_size_format(total)}[/bold]")
        
        console.print(table)
        
        if Confirm.ask(f"\nClean {get_size_format(total)} of files?"):
            # Create backup
            create_backup([
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
            ], f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Run cleanup
            with console.status("[bold green]Cleaning...[/bold green]") as status:
                results = self.cleanup.run_full_cleanup(lambda msg: status.update(f"[bold green]{msg}[/bold green]"))
            
            # Display results
            total_cleaned = sum(r['size'] for r in results.values())
            console.print(f"\n[bold green]✓ Cleaned {get_size_format(total_cleaned)}[/bold green]")
            
            log_operation("CLEANUP", f"Cleaned {get_size_format(total_cleaned)}")
    
    def run_startup_manager(self):
        """Run startup manager."""
        console.print("\n[bold yellow]═══ Startup Manager ═══[/bold yellow]")
        
        items = self.startup.get_startup_items()
        
        if not items:
            console.print("[yellow]No startup items found.[/yellow]")
            return
        
        table = Table(title="Startup Items", box=box.ROUNDED)
        table.add_column("#", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Location", style="green")
        table.add_column("Status", style="yellow")
        
        for i, item in enumerate(items, 1):
            status = "[green]✓ Enabled[/green]" if item['enabled'] else "[red]✗ Disabled[/red]"
            table.add_row(str(i), item['name'], item['location'], status)
        
        console.print(table)
        
        action = Prompt.ask(
            "\nAction",
            choices=["disable", "enable", "back"],
            default="back"
        )
        
        if action in ["disable", "enable"]:
            num = int(Prompt.ask("Enter item number")) - 1
            if 0 <= num < len(items):
                if action == "disable":
                    if self.startup.disable_startup_item(items[num]):
                        console.print(f"[green]✓ Disabled {items[num]['name']}[/green]")
                else:
                    if self.startup.enable_startup_item(items[num]):
                        console.print(f"[green]✓ Enabled {items[num]['name']}[/green]")
    
    def run_performance_optimization(self):
        """Run performance optimization."""
        console.print("\n[bold yellow]═══ Performance Optimization ═══[/bold yellow]")
        
        options = [
            ("1", "Set High Performance Power Plan"),
            ("2", "Disable Visual Effects"),
            ("3", "Optimize Virtual Memory"),
            ("4", "Disable Search Indexing"),
            ("5", "Apply All Performance Optimizations"),
            ("0", "Back"),
        ]
        
        for num, desc in options:
            console.print(f"  [{num}] {desc}")
        
        choice = Prompt.ask("\nSelect option", choices=["0", "1", "2", "3", "4", "5"])
        
        if choice == "1":
            if self.performance.set_high_performance_power_plan():
                console.print("[green]✓ High Performance power plan enabled[/green]")
        elif choice == "2":
            if self.performance.disable_visual_effects():
                console.print("[green]✓ Visual effects disabled[/green]")
        elif choice == "3":
            if self.performance.optimize_virtual_memory():
                console.print("[green]✓ Virtual memory optimized[/green]")
        elif choice == "4":
            if self.performance.disable_search_indexing():
                console.print("[green]✓ Search indexing disabled[/green]")
        elif choice == "5":
            with console.status("[bold green]Applying optimizations...[/bold green]"):
                self.performance.set_high_performance_power_plan()
                self.performance.disable_visual_effects()
                self.performance.optimize_virtual_memory()
                self.performance.disable_search_indexing()
            console.print("[green]✓ All performance optimizations applied[/green]")
    
    def run_network_optimization(self):
        """Run network optimization."""
        console.print("\n[bold yellow]═══ Network Optimization ═══[/bold yellow]")
        
        options = [
            ("1", "Flush DNS Cache"),
            ("2", "Optimize TCP/IP Settings"),
            ("3", "Reset Winsock"),
            ("4", "Apply All Network Optimizations"),
            ("0", "Back"),
        ]
        
        for num, desc in options:
            console.print(f"  [{num}] {desc}")
        
        choice = Prompt.ask("\nSelect option", choices=["0", "1", "2", "3", "4"])
        
        if choice == "1":
            if self.network.flush_dns():
                console.print("[green]✓ DNS cache flushed[/green]")
        elif choice == "2":
            if self.network.optimize_tcp_ip():
                console.print("[green]✓ TCP/IP optimized[/green]")
        elif choice == "3":
            if self.network.reset_winsock():
                console.print("[green]✓ Winsock reset[/green]")
        elif choice == "4":
            with console.status("[bold green]Applying network optimizations...[/bold green]"):
                self.network.flush_dns()
                self.network.optimize_tcp_ip()
                self.network.reset_winsock()
            console.print("[green]✓ All network optimizations applied[/green]")
    
    def run_privacy_optimization(self):
        """Run privacy optimization."""
        console.print("\n[bold yellow]═══ Privacy Settings ═══[/bold yellow]")
        
        options = [
            ("1", "Disable Telemetry"),
            ("2", "Disable Cortana"),
            ("3", "Disable Advertising ID"),
            ("4", "Apply All Privacy Settings"),
            ("0", "Back"),
        ]
        
        for num, desc in options:
            console.print(f"  [{num}] {desc}")
        
        choice = Prompt.ask("\nSelect option", choices=["0", "1", "2", "3", "4"])
        
        if choice == "1":
            if self.privacy.disable_telemetry():
                console.print("[green]✓ Telemetry disabled[/green]")
        elif choice == "2":
            if self.privacy.disable_cortana():
                console.print("[green]✓ Cortana disabled[/green]")
        elif choice == "3":
            if self.privacy.disable_advertising_id():
                console.print("[green]✓ Advertising ID disabled[/green]")
        elif choice == "4":
            with console.status("[bold green]Applying privacy settings...[/bold green]"):
                self.privacy.disable_telemetry()
                self.privacy.disable_cortana()
                self.privacy.disable_advertising_id()
            console.print("[green]✓ All privacy settings applied[/green]")
    
    def run_gaming_optimization(self):
        """Run gaming optimization."""
        console.print("\n[bold yellow]═══ Gaming Optimization ═══[/bold yellow]")
        
        if Confirm.ask("Apply gaming optimizations?"):
            with console.status("[bold green]Optimizing for gaming...[/bold green]"):
                self.performance.optimize_system_for_gaming()
                self.performance.set_high_performance_power_plan()
            console.print("[green]✓ Gaming optimizations applied[/green]")
    
    def show_system_info(self):
        """Show system information."""
        console.print("\n[bold yellow]═══ System Information ═══[/bold yellow]")
        
        with console.status("[bold green]Gathering system info...[/bold green]"):
            info = self.system.get_system_info()
        
        # OS Info
        os_table = Table(title="Operating System", box=box.ROUNDED)
        os_table.add_column("Property", style="cyan")
        os_table.add_column("Value", style="green")
        os_table.add_row("Name", info['os']['name'])
        os_table.add_row("Architecture", info['os']['architecture'])
        console.print(os_table)
        
        # CPU Info
        cpu_table = Table(title="CPU", box=box.ROUNDED)
        cpu_table.add_column("Property", style="cyan")
        cpu_table.add_column("Value", style="green")
        cpu_table.add_row("Name", info['cpu']['name'])
        cpu_table.add_row("Cores", str(info['cpu']['cores']))
        cpu_table.add_row("Threads", str(info['cpu']['threads']))
        cpu_table.add_row("Usage", f"{info['cpu']['usage']}%")
        console.print(cpu_table)
        
        # Memory Info
        mem = info['memory']
        mem_table = Table(title="Memory", box=box.ROUNDED)
        mem_table.add_column("Property", style="cyan")
        mem_table.add_column("Value", style="green")
        mem_table.add_row("Total", get_size_format(mem['total']))
        mem_table.add_row("Used", get_size_format(mem['used']))
        mem_table.add_row("Available", get_size_format(mem['available']))
        mem_table.add_row("Usage", f"{mem['percent']}%")
        console.print(mem_table)
        
        # Disk Info
        disk_table = Table(title="Disks", box=box.ROUNDED)
        disk_table.add_column("Drive", style="cyan")
        disk_table.add_column("Total", style="green")
        disk_table.add_column("Used", style="yellow")
        disk_table.add_column("Free", style="green")
        disk_table.add_column("Usage", style="yellow")
        
        for drive, usage in info['disk'].items():
            disk_table.add_row(
                drive,
                get_size_format(usage['total']),
                get_size_format(usage['used']),
                get_size_format(usage['free']),
                f"{usage['percent']}%"
            )
        console.print(disk_table)
    
    def run_full_optimization(self):
        """Run full system optimization."""
        console.print("\n[bold yellow]═══ Full System Optimization ═══[/bold yellow]")
        
        if not Confirm.ask("This will apply all optimizations. Continue?"):
            return
        
        console.print("\n[bold cyan]Creating system backup...[/bold cyan]")
        create_backup([
            os.environ.get('TEMP', ''),
            str(Path.home() / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'),
        ], f"full_optimization_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            # Cleanup
            task = progress.add_task("[cyan]Cleaning system...", total=5)
            self.cleanup.run_full_cleanup(lambda msg: progress.update(task, description=f"[cyan]{msg}"))
            progress.advance(task)
            
            # Performance
            progress.update(task, description="[cyan]Optimizing performance...")
            self.performance.set_high_performance_power_plan()
            self.performance.disable_visual_effects()
            progress.advance(task)
            
            # Network
            progress.update(task, description="[cyan]Optimizing network...")
            self.network.flush_dns()
            self.network.optimize_tcp_ip()
            progress.advance(task)
            
            # Privacy
            progress.update(task, description="[cyan]Applying privacy settings...")
            self.privacy.disable_telemetry()
            self.privacy.disable_advertising_id()
            progress.advance(task)
            
            # Gaming
            progress.update(task, description="[cyan]Optimizing for gaming...")
            self.performance.optimize_system_for_gaming()
            progress.advance(task)
        
        console.print("\n[bold green]✓ Full optimization complete![/bold green]")
        console.print("[yellow]Some changes may require a restart to take effect.[/yellow]")
        
        log_operation("FULL_OPTIMIZATION", "All optimizations applied")
    
    def run(self):
        """Main application loop."""
        # Check for admin rights
        if not is_admin():
            console.print("[yellow]Warning: Some features require administrator privileges.[/yellow]")
            if Confirm.ask("Run as administrator?"):
                run_as_admin()
        
        self.display_banner()
        
        while True:
            self.display_menu()
            choice = Prompt.ask("\nSelect option", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
            
            if choice == "0":
                console.print("[bold green]Thank you for using WinOptimizer![/bold green]")
                break
            elif choice == "1":
                self.run_cleanup()
            elif choice == "2":
                self.run_startup_manager()
            elif choice == "3":
                self.run_performance_optimization()
            elif choice == "4":
                self.run_network_optimization()
            elif choice == "5":
                self.run_privacy_optimization()
            elif choice == "6":
                self.run_gaming_optimization()
            elif choice == "7":
                self.show_system_info()
            elif choice == "8":
                console.print("[yellow]Backup & Restore coming soon![/yellow]")
            elif choice == "9":
                self.run_full_optimization()
            
            console.print()

# ── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        optimizer = WinOptimizer()
        optimizer.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
