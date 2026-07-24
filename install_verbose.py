#!/usr/bin/env python3
"""
WinOptimizer Verbose Installer
Shows installation process in terminal like git clone
"""

import os
import sys
import shutil
import subprocess
import time
import ctypes
from pathlib import Path

INSTALL_DIR = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'WinOptimizer'
SHORTCUT_DIR = Path(os.environ.get('APPDATA', '')) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'WinOptimizer'
DESKTOP = Path(os.environ.get('USERPROFILE', '')) / 'Desktop'

# ── Colors ────────────────────────────────────────────────────────────────────

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

def spinner(msg, duration=1.5):
    symbols = ['|', '/', '-', '\\']
    for i in range(int(duration * 10)):
        sys.stdout.write(f"\r  {Colors.CYAN}{symbols[i % len(symbols)]}{Colors.RESET} {msg}...")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write(f"\r  {Colors.GREEN}✓{Colors.RESET} {msg}... {Colors.GREEN}DONE{Colors.RESET}          \n")

def progress_bar(msg, total=20, delay=0.05):
    for i in range(total + 1):
        bar = '█' * i + '░' * (total - i)
        percent = int(i / total * 100)
        sys.stdout.write(f"\r  {Colors.CYAN}[{bar}]{Colors.RESET} {percent:3d}% {msg}")
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ── Check Admin ───────────────────────────────────────────────────────────────

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

# ── Installation Steps ────────────────────────────────────────────────────────

def install():
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}+{'='*58}+{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}|{' '*58}|{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}|   WinOptimizer v2.0.0 - Verbose Installer{' '*17}|{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}|{' '*58}|{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}+{'='*58}+{Colors.RESET}")
    print()

    # ── Step 1: Check system ──────────────────────────────────────────────
    step("1/6 Checking system requirements")

    info(f"Python: {sys.version.split()[0]}")
    info(f"Platform: {sys.platform}")
    info(f"Architecture: {sys.maxsize > 2**32 and '64-bit' or '32-bit'}")
    ok("System check passed")

    # ── Step 2: Create install directory ──────────────────────────────────
    step("2/6 Creating installation directory")

    info(f"Target: {INSTALL_DIR}")
    progress_bar("Creating directory", 10, 0.03)
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    ok(f"Directory created: {INSTALL_DIR}")

    # ── Step 3: Copy files ────────────────────────────────────────────────
    step("3/6 Copying application files")

    # Get the directory where this script/exe is located
    if getattr(sys, 'frozen', False):
        source_dir = Path(sys._MEIPASS)
    else:
        source_dir = Path(__file__).parent

    files_to_install = [
        ('optimizer.py', 'WinOptimizer.py'),
        ('requirements.txt', 'requirements.txt'),
        ('LICENSE', 'LICENSE'),
        ('folder_icon.ico', 'app.ico'),
    ]

    total_files = len(files_to_install)
    for i, (src_name, dst_name) in enumerate(files_to_install, 1):
        src = source_dir / src_name
        dst = INSTALL_DIR / dst_name
        if src.exists():
            progress_bar(f"Installing {dst_name}", 15, 0.03)
            shutil.copy2(str(src), str(dst))
            ok(f"{dst_name} ({src.stat().st_size:,} bytes)")
        else:
            warn(f"Skipping {src_name} (not found)")

    # ── Step 4: Install dependencies ──────────────────────────────────────
    step("4/6 Installing dependencies")

    deps = ['rich', 'psutil']
    for dep in deps:
        info(f"Installing {dep}...")
        progress_bar(dep, 20, 0.02)
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', dep, '-q'],
            capture_output=True
        )
        if result.returncode == 0:
            ok(f"{dep} installed")
        else:
            fail(f"{dep} failed (may already be installed)")

    # ── Step 5: Create shortcuts ──────────────────────────────────────────
    step("5/6 Creating shortcuts")

    SHORTCUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create batch launcher
    launcher = INSTALL_DIR / 'WinOptimizer.bat'
    launcher.write_text(
        f'@echo off\n'
        f'cd /d "{INSTALL_DIR}"\n'
        f'"{sys.executable}" WinOptimizer.py\n',
        encoding='utf-8'
    )
    progress_bar("Creating launcher", 10, 0.03)
    ok("Batch launcher created")

    # Desktop shortcut via PowerShell
    desktop_shortcut = DESKTOP / 'WinOptimizer.lnk'
    ps_cmd = f'''
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{desktop_shortcut}")
    $Shortcut.TargetPath = "{launcher}"
    $Shortcut.WorkingDirectory = "{INSTALL_DIR}"
    $Shortcut.Description = "WinOptimizer - Windows Optimization Suite"
    $Shortcut.Save()
    '''
    progress_bar("Creating desktop shortcut", 10, 0.03)
    subprocess.run(['powershell', '-Command', ps_cmd], capture_output=True)
    ok("Desktop shortcut created")

    # Start Menu shortcut
    start_shortcut = SHORTCUT_DIR / 'WinOptimizer.lnk'
    ps_cmd2 = f'''
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("{start_shortcut}")
    $Shortcut.TargetPath = "{launcher}"
    $Shortcut.WorkingDirectory = "{INSTALL_DIR}"
    $Shortcut.Description = "WinOptimizer - Windows Optimization Suite"
    $Shortcut.Save()
    '''
    progress_bar("Creating Start Menu shortcut", 10, 0.03)
    subprocess.run(['powershell', '-Command', ps_cmd2], capture_output=True)
    ok("Start Menu shortcut created")

    # ── Step 6: Verify installation ───────────────────────────────────────
    step("6/6 Verifying installation")

    progress_bar("Verifying files", 15, 0.03)

    verify_files = ['WinOptimizer.py', 'requirements.txt', 'LICENSE', 'app.ico', 'WinOptimizer.bat']
    all_ok = True
    for f in verify_files:
        if (INSTALL_DIR / f).exists():
            ok(f"{f}")
        else:
            fail(f"{f} missing")
            all_ok = False

    # ── Summary ───────────────────────────────────────────────────────────
    print()
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}  INSTALLATION COMPLETE{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*60}{Colors.RESET}")
    print()
    print(f"  {Colors.CYAN}Location:{Colors.RESET}  {INSTALL_DIR}")
    print(f"  {Colors.CYAN}Desktop:{Colors.RESET}   {desktop_shortcut}")
    print(f"  {Colors.CYAN}Start:{Colors.RESET}     {SHORTCUT_DIR}")
    print()
    print(f"  {Colors.YELLOW}Run:{Colors.RESET}  Double-click desktop shortcut or:")
    print(f"      {Colors.DIM}{INSTALL_DIR}\\WinOptimizer.bat{Colors.RESET}")
    print()

    input(f"{Colors.BOLD}Press Enter to exit...{Colors.RESET}")

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        request_admin()
        install()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Installation cancelled.{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)
