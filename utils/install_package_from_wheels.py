"""Utility module for installing wheels from GitHub releases in Colab"""

import sys
import urllib.request
import json
import subprocess
from typing import Optional, Tuple

def get_python_compatibility() -> Tuple[int, int, list]:
    """Check Python version and return compatibility info."""
    major, minor = sys.version_info[:2]
    warnings = []
    
    if major == 3 and minor >= 13:
        warnings.append("Python 3.13+ detected - ensuring package compatibility")
    
    return major, minor, warnings

def install_from_github(repo: str = "DanielOmola/assistant-juridique", 
                        upgrade: bool = True,
                        install_deps: bool = True) -> None:
    """
    Auto-detect Colab environment and install correct wheel from GitHub releases.
    
    Args:
        repo: GitHub repository in format "username/repo"
        upgrade: Whether to upgrade if already installed
        install_deps: Whether to install from requirements.txt first
    """
    py_major, py_minor, warnings = get_python_compatibility()
    
    if warnings:
        for w in warnings:
            print(f"⚠️  {w}")
    
    # Upgrade pip for Python 3.13+
    if py_minor >= 13:
        print("🔄 Upgrading pip for Python 3.13 compatibility...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ])
    
    # Install dependencies from requirements.txt if requested
    if install_deps:
        req_url = f"https://raw.githubusercontent.com/{repo}/main/requirements.txt"
        try:
            print("📦 Installing dependencies from requirements.txt...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-q",
                "-r", req_url
            ])
            print("✅ Dependencies installed")
        except Exception as e:
            print(f"⚠️ Could not install from requirements.txt: {e}")
    
    # Get Python version string (e.g., "cp312", "cp313")
    py_ver = f"cp{py_major}{py_minor}"
    
    # Get latest release from GitHub
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    
    try:
        with urllib.request.urlopen(api_url) as response:
            release = json.loads(response.read())
    except Exception as e:
        raise Exception(f"Failed to fetch latest release: {e}")
    
    # Find matching wheel
    wheel_url = None
    for asset in release['assets']:
        if asset['name'].endswith('.whl'):
            # Prefer exact Python version match
            if py_ver in asset['name']:
                wheel_url = asset['browser_download_url']
                break
            # Fallback to any manylinux wheel
            elif 'manylinux' in asset['name'] and not wheel_url:
                wheel_url = asset['browser_download_url']
    
    if not wheel_url:
        raise Exception(f"No compatible wheel found for Python {py_ver}")
    
    # Install the wheel
    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    cmd.append(wheel_url)
    
    print(f"📦 Installing wheel from {wheel_url}...")
    subprocess.check_call(cmd)
    print(f"✅ Package installed successfully on Python {py_major}.{py_minor}")

# Alias for convenience
install = install_from_github

# For backward compatibility with your __all__
__all__ = ['install_from_github', 'install']