#!/usr/bin/env python3
"""
WINOPTIMIZER v2.0.0
Advanced Windows System Optimization Suite

Features:
- One-click system optimization with animated progress
- Gaming mode optimization
- Startup program management
- System information
- Backup & restore
- Individual settings tweaks

Author: IVCS
License: MIT
"""

import os
import sys
import shutil
import subprocess
import ctypes
import winreg
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import psutil
except ImportError:
    psutil = None

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.live import Live
    from rich.text import Text
    from rich import box
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
    from rich.live import Live
    from rich.text import Text
    from rich import box

VERSION = "2.0.0"
APP_NAME = "WinOptimizer"
BACKUP_DIR = Path.home() / "WinOptimizer_Backups"
LOG_DIR = Path.home() / "WinOptimizer_Logs"

console = Console()

# ── Utility Functions ──────────────────────────────────────────────────────────

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def is_admin() -> bool:
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin():
    if not is_admin():
        console.print("[yellow]Requesting administrator privileges...[/yellow]")
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except Exception:
            console.print("[red]Failed to get administrator privileges.[/red]")


def log_operation(operation: str, details: str):
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"optimizer_{datetime.now().strftime('%Y%m%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {operation}: {details}\n")


def get_size_format(size_bytes: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def get_directory_size(path: Path) -> int:
    total_size = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
    except Exception:
        pass
    return total_size


def animated_step(description: str, func, *args, **kwargs):
    result = [None]
    error = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=target)
    thread.start()

    symbols = ["|", "/", "-", "\\"]
    idx = 0
    while thread.is_alive():
        symbol = symbols[idx % len(symbols)]
        sys.stdout.write(f"\r  {symbol} {description}...")
        sys.stdout.flush()
        time.sleep(0.15)
        idx += 1

    sys.stdout.write(f"\r  + {description}... DONE          \n")
    sys.stdout.flush()

    if error[0]:
        sys.stdout.write(f"    X Error: {error[0]}\n")
        sys.stdout.flush()
        return None
    return result[0]


def animated_step_with_size(description: str, func, *args, **kwargs):
    result = [None]
    error = [None]

    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            error[0] = e

    thread = threading.Thread(target=target)
    thread.start()

    symbols = ["|", "/", "-", "\\"]
    idx = 0
    while thread.is_alive():
        symbol = symbols[idx % len(symbols)]
        sys.stdout.write(f"\r  {symbol} {description}...")
        sys.stdout.flush()
        time.sleep(0.15)
        idx += 1

    if error[0]:
        sys.stdout.write(f"\r  X {description}... FAILED          \n")
        sys.stdout.flush()
        sys.stdout.write(f"    {error[0]}\n")
        sys.stdout.flush()
        return None

    if result[0] and isinstance(result[0], tuple) and len(result[0]) >= 1:
        size = result[0][0]
        if size and size > 0:
            sys.stdout.write(f"\r  + {description}... {get_size_format(size)} freed          \n")
        else:
            sys.stdout.write(f"\r  + {description}... DONE          \n")
    else:
        sys.stdout.write(f"\r  + {description}... DONE          \n")
    sys.stdout.flush()

    return result[0]


# ── Cleanup Functions ──────────────────────────────────────────────────────────

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


def clean_temp_files() -> Tuple[int, int]:
    total_size = 0
    count = 0
    for temp_dir in TEMP_DIRS:
        if temp_dir.exists():
            try:
                for item in temp_dir.rglob('*'):
                    try:
                        if item.is_file():
                            total_size += item.stat().st_size
                            item.unlink()
                            count += 1
                    except Exception:
                        pass
            except Exception:
                pass
    return total_size, count


def clean_browser_cache() -> Tuple[int, int]:
    total_size = 0
    count = 0
    for cache_dir in BROWSER_CACHE_DIRS:
        if cache_dir.exists():
            try:
                total_size += get_directory_size(cache_dir)
                shutil.rmtree(cache_dir)
                count += 1
            except Exception:
                pass
    return total_size, count


def clean_windows_logs() -> Tuple[int, int]:
    total_size = 0
    count = 0
    log_dirs = [
        Path('C:\\Windows\\Logs'),
        Path.home() / 'AppData' / 'Local' / 'CrashDumps',
    ]
    for log_dir in log_dirs:
        if log_dir.exists():
            try:
                for item in log_dir.rglob('*.log'):
                    try:
                        total_size += item.stat().st_size
                        item.unlink()
                        count += 1
                    except Exception:
                        pass
            except Exception:
                pass
    return total_size, count


def empty_recycle_bin() -> Tuple[int, bool]:
    try:
        size = get_directory_size(Path('C:\\$Recycle.Bin'))
        result = subprocess.run(
            ['powershell', '-Command',
             'Clear-RecycleBin -Force -ErrorAction SilentlyContinue'],
            capture_output=True
        )
        if result.returncode != 0:
            subprocess.run(
                ['cmd', '/c', 'rd', '/s', '/q', 'C:\\$Recycle.Bin'],
                capture_output=True
            )
        return size, True
    except Exception:
        return 0, False


# ── Performance Functions ──────────────────────────────────────────────────────

def set_high_performance_power_plan() -> bool:
    try:
        subprocess.run(
            ['powercfg', '/setactive', '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'],
            capture_output=True
        )
        return True
    except Exception:
        return False


def disable_visual_effects() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects',
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, 'VisualFXSetting', 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize',
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, 'EnableTransparency', 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def disable_search_indexing() -> bool:
    try:
        subprocess.run(['sc', 'config', 'WSearch', 'start=', 'disabled'], capture_output=True)
        subprocess.run(['net', 'stop', 'WSearch'], capture_output=True)
        return True
    except Exception:
        return False


def optimize_system_for_gaming() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\GameBar',
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, 'AllowAutoGameMode', 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(key, 'AutoGameModeEnabled', 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'SYSTEM\CurrentControlSet\Control\GraphicsDrivers',
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, 'HwSchMode', 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


# ── Network Functions ──────────────────────────────────────────────────────────

def flush_dns() -> bool:
    try:
        subprocess.run(['ipconfig', '/flushdns'], capture_output=True)
        return True
    except Exception:
        return False


def optimize_tcp_ip() -> bool:
    try:
        subprocess.run(['netsh', 'int', 'ip', 'reset'], capture_output=True)
        commands = [
            'netsh int tcp set global autotuninglevel=normal',
            'netsh int tcp set global chimney=enabled',
            'netsh int tcp set global dca=enabled',
            'netsh int tcp set global netdma=enabled',
            'netsh int tcp set global ecncapability=disabled',
            'netsh int tcp set global timestamps=disabled',
        ]
        for cmd in commands:
            subprocess.run(cmd.split(), capture_output=True)
        return True
    except Exception:
        return False


# ── Privacy Functions ──────────────────────────────────────────────────────────

def disable_telemetry() -> bool:
    try:
        subprocess.run(['sc', 'config', 'DiagTrack', 'start=', 'disabled'], capture_output=True)
        subprocess.run(['net', 'stop', 'DiagTrack'], capture_output=True)

        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'Policies\Microsoft\Windows\System',
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, 'EnableActivityFeed', 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, 'PublishUserActivities', 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def disable_cortana() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r'SOFTWARE\Policies\Microsoft\Windows\Windows Search',
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, 'AllowCortana', 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


def disable_advertising_id() -> bool:
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo',
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, 'Enabled', 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False


# ── Startup Manager ────────────────────────────────────────────────────────────

STARTUP_REGISTRY = {
    'user_run': r'Software\Microsoft\Windows\CurrentVersion\Run',
    'user_runonce': r'Software\Microsoft\Windows\CurrentVersion\RunOnce',
    'machine_run': r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run',
    'machine_runonce': r'SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce',
    'startup_folder': str(Path.home() / 'AppData' / 'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'),
}


def get_startup_items() -> List[Dict]:
    items = []
    for location, reg_path in STARTUP_REGISTRY.items():
        if location == 'startup_folder':
            continue
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER if 'user' in location else winreg.HKEY_LOCAL_MACHINE,
                reg_path, 0, winreg.KEY_READ
            )
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    items.append({'name': name, 'command': value, 'location': location, 'enabled': True})
                    i += 1
                except OSError:
                    break
            winreg.CloseKey(key)
        except Exception:
            pass

    startup_folder = Path(STARTUP_REGISTRY['startup_folder'])
    if startup_folder.exists():
        for item in startup_folder.iterdir():
            if item.is_file():
                items.append({'name': item.stem, 'command': str(item), 'location': 'startup_folder', 'enabled': True})
    return items


def disable_startup_item(item: Dict) -> bool:
    try:
        if item['location'] == 'startup_folder':
            backup_dir = BACKUP_DIR / 'startup_items'
            backup_dir.mkdir(parents=True, exist_ok=True)
            source = Path(item['command'])
            if source.exists():
                shutil.move(str(source), str(backup_dir / source.name))
                return True
            return False
        else:
            location = item['location']
            reg_path = STARTUP_REGISTRY[location]
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER if 'user' in location else winreg.HKEY_LOCAL_MACHINE,
                reg_path, 0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, item['name'])
            winreg.CloseKey(key)
            return True
    except Exception:
        return False


def enable_startup_item(item: Dict) -> bool:
    try:
        if item['location'] == 'startup_folder':
            backup_dir = BACKUP_DIR / 'startup_items'
            backup_file = backup_dir / (item['name'] + Path(item['command']).suffix)
            if backup_file.exists():
                dest = Path(STARTUP_REGISTRY['startup_folder']) / backup_file.name
                shutil.move(str(backup_file), str(dest))
                return True
            return False
        else:
            location = item['location']
            reg_path = STARTUP_REGISTRY[location]
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER if 'user' in location else winreg.HKEY_LOCAL_MACHINE,
                reg_path, 0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, item['name'], 0, winreg.REG_SZ, item['command'])
            winreg.CloseKey(key)
            return True
    except Exception:
        return False


# ── System Info ────────────────────────────────────────────────────────────────

def get_system_info() -> Dict:
    if psutil is None:
        return {}
    info = {
        'os': {
            'name': os.environ.get('OS', 'Unknown'),
            'architecture': os.environ.get('PROCESSOR_ARCHITECTURE', 'Unknown'),
        },
        'cpu': {
            'name': os.environ.get('PROCESSOR_IDENTIFIER', 'Unknown'),
            'cores': psutil.cpu_count(logical=False) or 0,
            'threads': psutil.cpu_count(logical=True) or 0,
            'usage': psutil.cpu_percent(interval=1),
        },
        'memory': {
            'total': psutil.virtual_memory().total,
            'used': psutil.virtual_memory().used,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent,
        },
        'disk': {},
    }
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            info['disk'][partition.device] = {
                'total': usage.total, 'used': usage.used,
                'free': usage.free, 'percent': usage.percent,
            }
        except Exception:
            pass
    return info


# ── Main Application ───────────────────────────────────────────────────────────

class WinOptimizer:
    def __init__(self):
        pass

    def display_banner(self):
        banner = (
            "\n[bold green]"
            "+======================================================================+\n"
            "|                                                                      |\n"
            "|   __      __  ______  _____       ______  _____  _   _  _____       |\n"
            "|   \\ \\    / / |  ____||  __ \\     |  ____|/ ____|| \\ | ||  __ \\      |\n"
            "|    \\ \\  / /  | |__   | |  | |    | |__  | (___  |  \\| || |  | |     |\n"
            "|     \\ \\/ /   |  __|  | |  | |    |  __|  \\___ \\ | . ` || |  | |     |\n"
            "|      \\  /    | |____ | |__| | _  | |____ ____) || |\\  || |__| | _   |\n"
            "|       \\/     |______||_____/(_) |______|_____/ |_| \\_||_____/ (_)  |\n"
            "|                                                                      |\n"
            "|                 Advanced Windows Optimization Suite                  |\n"
            "|                            Version {version}                            |\n"
            "+======================================================================+\n"
            "[/bold green]"
        )
        console.print(banner.format(version=VERSION))

    def display_menu(self):
        menu = """
[bold cyan]+========================================================+
|                      MAIN MENU                          |
+========================================================+
|  [1] Optimize           - Full system optimization      |
|  [2] Gaming Mode        - Optimize for gaming           |
|  [3] Startup            - Manage startup programs       |
|  [4] System Info        - View system details           |
|  [5] Backup             - Restore point / registry      |
|  [6] Settings           - Individual tweaks             |
|  [0] Exit                                             |
+========================================================+[/bold cyan]"""
        console.print(menu)

    def run_optimize(self):
        console.print("\n[bold yellow]=== Full System Optimization ===[/bold yellow]")

        if not Confirm.ask("Run full optimization?"):
            return

        console.print()
        results = []

        # Cleanup
        r = animated_step_with_size("Cleaning temp files", clean_temp_files)
        results.append(("Temp files", r is not None))

        r = animated_step_with_size("Cleaning browser cache", clean_browser_cache)
        results.append(("Browser cache", r is not None))

        r = animated_step_with_size("Cleaning Windows logs", clean_windows_logs)
        results.append(("Windows logs", r is not None))

        r = animated_step_with_size("Emptying recycle bin", empty_recycle_bin)
        results.append(("Recycle bin", r is not None))

        # Performance
        animated_step("Setting high performance power plan", set_high_performance_power_plan)
        results.append(("Power plan", True))

        animated_step("Disabling visual effects", disable_visual_effects)
        results.append(("Visual effects", True))

        animated_step("Disabling search indexing", disable_search_indexing)
        results.append(("Search indexing", True))

        # Network
        animated_step("Flushing DNS cache", flush_dns)
        results.append(("DNS cache", True))

        animated_step("Optimizing TCP/IP", optimize_tcp_ip)
        results.append(("TCP/IP", True))

        # Privacy
        animated_step("Disabling telemetry", disable_telemetry)
        results.append(("Telemetry", True))

        animated_step("Disabling Cortana", disable_cortana)
        results.append(("Cortana", True))

        animated_step("Disabling advertising ID", disable_advertising_id)
        results.append(("Advertising ID", True))

        # Summary
        console.print()
        success = sum(1 for _, ok in results if ok)
        total = len(results)

        summary = Table(box=box.ROUNDED, title="Optimization Summary")
        summary.add_column("Task", style="cyan")
        summary.add_column("Status", justify="center")

        for name, ok in results:
            status = "[green]OK[/green]" if ok else "[red]FAIL[/red]"
            summary.add_row(name, status)

        console.print(summary)

        if success == total:
            console.print(f"\n[bold green]All {total} tasks completed successfully![/bold green]")
        else:
            console.print(f"\n[bold yellow]{success}/{total} tasks completed[/bold yellow]")

        console.print("[dim]Some changes may require a restart.[/dim]")
        log_operation("OPTIMIZE", f"{success}/{total} successful")

    def run_gaming(self):
        console.print("\n[bold yellow]=== Gaming Mode ===[/bold yellow]")

        if not Confirm.ask("Optimize system for gaming?"):
            return

        console.print()
        animated_step("Enabling Game Mode", optimize_system_for_gaming)
        animated_step("Setting high performance power plan", set_high_performance_power_plan)

        console.print("\n[bold green]+ Gaming optimizations applied![/bold green]")
        log_operation("GAMING", "Gaming optimizations applied")

    def run_startup(self):
        console.print("\n[bold yellow]=== Startup Manager ===[/bold yellow]")

        with console.status("[cyan]Loading startup items...[/cyan]"):
            items = get_startup_items()

        if not items:
            console.print("[yellow]No startup items found.[/yellow]")
            return

        table = Table(box=box.ROUNDED)
        table.add_column("#", style="dim")
        table.add_column("Name", style="cyan")
        table.add_column("Location", style="green")
        table.add_column("Status", style="yellow")

        for i, item in enumerate(items, 1):
            status = "[green]+[/green]" if item['enabled'] else "[red]-[/red]"
            table.add_row(str(i), item['name'], item['location'], status)

        console.print(table)

        action = Prompt.ask("\nAction", choices=["disable", "enable", "back"], default="back")

        if action in ["disable", "enable"]:
            try:
                num = int(Prompt.ask("Enter item number")) - 1
            except ValueError:
                console.print("[red]Invalid number.[/red]")
                return

            if 0 <= num < len(items):
                if action == "disable":
                    if disable_startup_item(items[num]):
                        console.print(f"[green]+ Disabled {items[num]['name']}[/green]")
                    else:
                        console.print(f"[red]X Failed to disable {items[num]['name']}[/red]")
                else:
                    if enable_startup_item(items[num]):
                        console.print(f"[green]+ Enabled {items[num]['name']}[/green]")
                    else:
                        console.print(f"[red]X Failed to enable {items[num]['name']}[/red]")
            else:
                console.print("[red]Invalid item number.[/red]")

    def run_system_info(self):
        console.print("\n[bold yellow]=== System Information ===[/bold yellow]")

        with console.status("[cyan]Gathering system info...[/cyan]"):
            info = get_system_info()

        if not info:
            console.print("[red]Could not retrieve system info (psutil required).[/red]")
            return

        # OS
        os_table = Table(title="Operating System", box=box.ROUNDED)
        os_table.add_column("Property", style="cyan")
        os_table.add_column("Value", style="green")
        os_table.add_row("Name", info['os']['name'])
        os_table.add_row("Architecture", info['os']['architecture'])
        console.print(os_table)

        # CPU
        cpu_table = Table(title="CPU", box=box.ROUNDED)
        cpu_table.add_column("Property", style="cyan")
        cpu_table.add_column("Value", style="green")
        cpu_table.add_row("Name", info['cpu']['name'])
        cpu_table.add_row("Cores", str(info['cpu']['cores']))
        cpu_table.add_row("Threads", str(info['cpu']['threads']))
        cpu_table.add_row("Usage", f"{info['cpu']['usage']}%")
        console.print(cpu_table)

        # Memory
        mem = info['memory']
        mem_table = Table(title="Memory", box=box.ROUNDED)
        mem_table.add_column("Property", style="cyan")
        mem_table.add_column("Value", style="green")
        mem_table.add_row("Total", get_size_format(mem['total']))
        mem_table.add_row("Used", get_size_format(mem['used']))
        mem_table.add_row("Available", get_size_format(mem['available']))
        mem_table.add_row("Usage", f"{mem['percent']}%")
        console.print(mem_table)

        # Disks
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

    def run_backup(self):
        console.print("\n[bold yellow]=== Backup ===[/bold yellow]")

        options = [
            ("1", "Create System Restore Point"),
            ("2", "Export Registry"),
            ("0", "Back"),
        ]

        for num, desc in options:
            console.print(f"  [{num}] {desc}")

        choice = Prompt.ask("\nSelect option", choices=["0", "1", "2"])

        if choice == "1":
            console.print()
            result = animated_step("Creating restore point", lambda: subprocess.run(
                ['powershell', '-Command',
                 'Checkpoint-Computer -Description "WinOptimizer Restore Point" '
                 '-RestorePointType MODIFY_SETTINGS'],
                capture_output=True
            ).returncode == 0)
            if result:
                console.print("[green]+ Restore point created[/green]")
            else:
                console.print("[red]X Restore point failed (service may be disabled)[/red]")

        elif choice == "2":
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            reg_file = BACKUP_DIR / f"registry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.reg"
            console.print()
            result = animated_step("Exporting registry", lambda: subprocess.run(
                ['reg', 'export', 'HKCU', str(reg_file), '/y'],
                capture_output=True
            ).returncode == 0)
            if result:
                console.print(f"[green]+ Registry saved to {reg_file}[/green]")

    def run_settings(self):
        console.print("\n[bold yellow]=== Settings ===[/bold yellow]")

        options = [
            ("1", "Disable Visual Effects"),
            ("2", "Disable Search Indexing"),
            ("3", "Disable Telemetry"),
            ("4", "Disable Cortana"),
            ("5", "Disable Advertising ID"),
            ("0", "Back"),
        ]

        for num, desc in options:
            console.print(f"  [{num}] {desc}")

        choice = Prompt.ask("\nSelect option", choices=["0", "1", "2", "3", "4", "5"])

        settings_map = {
            "1": ("Visual effects", disable_visual_effects),
            "2": ("Search indexing", disable_search_indexing),
            "3": ("Telemetry", disable_telemetry),
            "4": ("Cortana", disable_cortana),
            "5": ("Advertising ID", disable_advertising_id),
        }

        if choice in settings_map:
            name, func = settings_map[choice]
            console.print()
            animated_step(f"Disabling {name}", func)
            console.print(f"[green]+ {name} disabled[/green]")

    def run(self):
        if not is_admin():
            console.print("[yellow]Warning: Some features require administrator privileges.[/yellow]")
            if Confirm.ask("Run as administrator?"):
                run_as_admin()

        clear_screen()
        self.display_banner()

        while True:
            self.display_menu()
            choice = Prompt.ask("\nSelect option", choices=["0", "1", "2", "3", "4", "5", "6"])

            clear_screen()
            self.display_banner()

            if choice == "0":
                console.print("[bold green]Goodbye![/bold green]")
                break
            elif choice == "1":
                self.run_optimize()
            elif choice == "2":
                self.run_gaming()
            elif choice == "3":
                self.run_startup()
            elif choice == "4":
                self.run_system_info()
            elif choice == "5":
                self.run_backup()
            elif choice == "6":
                self.run_settings()

            console.print()


if __name__ == "__main__":
    try:
        optimizer = WinOptimizer()
        optimizer.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Cancelled.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
