#!/usr/bin/env python3
"""
WinOptimizer Verbose Uninstaller
Shows uninstallation process in terminal
"""

import os
import sys
import shutil
import time
import ctypes
from pathlib import Path

INSTALL_DIR = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'WinOptimizer'
SHORTCUT_DIR = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'WinOptimizer'
DESKTOP = Path(os.environ.get('USERPROFILE', '')) / 'Desktop'

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def ok(msg):
    print(f"  {Colors.GREEN}✓{Colors.RESET} {msg}")

def fail(msg):
    print(f"  {Colors.RED}✗{Colors.RESET} {msg}")

def info(msg):
    print(f"  {Colors.CYAN}→{Colors.RESET} {msg}")

def step(msg):
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}  {msg}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.YELLOW}{'='*60}{Colors.RESET}")

def progress_bar(msg, total=20, delay=0.03):
    for i in range(total + 1):
        bar = '█' * i + '░' * (total - i)
        percent = int(i / total * 100)
        sys.stdout.write(f"\r  {Colors.CYAN}[{bar}]{Colors.RESET} {percent:3d}% {msg}")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def request_admin():
    if not is_admin():
        print(f"{Colors.YELLOW}⚠ Administrator privileges required{Colors.RESET}")
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit(0)
        except Exception:
            print(f"{Colors.RED}✗ Failed to get admin privileges{Colors.RESET}")
            sys.exit(1)

def uninstall():
    print()
    print(f"{Colors.BOLD}{Colors.RED}+{'='*58}+{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}|{' '*58}|{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}|   WinOptimizer v2.0.0 - Uninstaller{' '*20}|{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}|{' '*58}|{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.RED}+{'='*58}+{Colors.RESET}")
    print()

    if not INSTALL_DIR.exists():
        print(f"{Colors.YELLOW}WinOptimizer is not installed.{Colors.RESET}")
        input("Press Enter to exit...")
        return

    confirm = input(f"{Colors.RED}Are you sure you want to uninstall WinOptimizer? [y/N]: {Colors.RESET}")
    if confirm.lower() != 'y':
        print("Uninstall cancelled.")
        return

    # ── Step 1: Remove shortcuts ──────────────────────────────────────────
    step("1/3 Removing shortcuts")

    shortcuts = [
        DESKTOP / 'WinOptimizer.lnk',
        SHORTCUT_DIR / 'WinOptimizer.lnk',
    ]

    for shortcut in shortcuts:
        progress_bar(f"Removing {shortcut.name}", 10, 0.02)
        if shortcut.exists():
            shortcut.unlink()
            ok(f"Removed {shortcut.name}")
        else:
            info(f"{shortcut.name} not found (skipped)")

    if SHORTCUT_DIR.exists():
        progress_bar("Removing Start Menu folder", 10, 0.02)
        shutil.rmtree(str(SHORTCUT_DIR), ignore_errors=True)
        ok("Start Menu folder removed")

    # ── Step 2: Remove installation directory ─────────────────────────────
    step("2/3 Removing installation directory")

    info(f"Target: {INSTALL_DIR}")
    progress_bar("Removing files", 20, 0.03)

    removed_count = 0
    for item in INSTALL_DIR.rglob('*'):
        try:
            if item.is_file():
                item.unlink()
                removed_count += 1
        except Exception:
            pass

    try:
        INSTALL_DIR.rmdir()
    except Exception:
        pass

    ok(f"Removed {removed_count} files")

    # ── Step 3: Cleanup registry ──────────────────────────────────────────
    step("3/3 Cleaning up registry")

    import winreg
    registry_keys = [
        (winreg.HKEY_LOCAL_MACHINE, r'Software\Microsoft\Windows\CurrentVersion\Uninstall\WinOptimizer'),
        (winreg.HKEY_LOCAL_MACHINE, r'Software\WinOptimizer'),
    ]

    for hkey, subkey in registry_keys:
        progress_bar(f"Removing {subkey.split(chr(92))[-1]}", 10, 0.02)
        try:
            winreg.DeleteKey(hkey, subkey)
            ok(f"Removed registry key")
        except Exception:
            info("Key not found (skipped)")

    # ── Summary ───────────────────────────────────────────────────────────
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}  UNINSTALLATION COMPLETE{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")
    print()
    print(f"  {Colors.DIM}WinOptimizer has been removed from your system.{Colors.RESET}")
    print()

    input(f"{Colors.BOLD}Press Enter to exit...{Colors.RESET}")

if __name__ == "__main__":
    try:
        request_admin()
        uninstall()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Uninstall cancelled.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
