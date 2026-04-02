"""
JVM management module with automatic JRE download and initialization.
"""
import os
import sys
import platform
import urllib.request
import ssl
import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import Optional, Tuple
import jpype
from jpype import JClass

# Package root directory
PACKAGE_DIR = Path(__file__).parent
JRE_DIR = PACKAGE_DIR / "jre24"
JAR_FILE = PACKAGE_DIR / "resources" / "mukip-0.4.0-beta-all.jar"

MUKIP_INITIALIZED = False

# JRE download configuration
JRE_VERSION = "24.0.2_12"
JRE_BASE_URL = "https://github.com/WestlakeUniversity-WangLab/jre8-mirror/releases/download"

jvm_paths = {
    'windows': JRE_DIR / 'bin' / 'server' / 'jvm.dll',
    'linux': JRE_DIR / 'lib' / 'server' / 'libjvm.so',
    'darwin': JRE_DIR / 'Contents' / 'Home' / 'lib' / 'server' / 'libjvm.dylib'
}

def detect_system_arch() -> Tuple[str, str]:
    """
    Detect system OS and architecture.

    :return: Tuple of (system, arch) compatible with JRE downloads
    """
    raw_system = platform.system().lower()
    raw_machine = platform.machine().lower()

    if raw_system == "darwin":
        system = "mac"
    elif raw_system == "windows":
        system = "windows"
    elif raw_system == "linux":
        system = "linux"
    elif raw_system == "aix":
        system = "aix"
    else:
        system = raw_system

    if raw_machine in ["x86_64", "amd64"]:
        arch = "x64"
    elif raw_machine in ["arm64", "aarch64"]:
        arch = "aarch64"
    elif raw_machine in ["ppc64le", "powerpc64le"]:
        arch = "ppc64le"
    elif raw_machine == "s390x":
        arch = "s390x"
    elif raw_machine == "riscv64":
        arch = "riscv64"
    elif raw_machine.startswith("arm"):
        arch = "arm"
    else:
        arch = raw_machine

    if system == "linux":
        if os.path.exists("/etc/alpine-release"):
            system = "alpine-linux"

    if not arch:
        arch = raw_machine

    return system, arch


def get_jvm_library_path() -> Optional[str]:
    """
    Get the JVM library path for the downloaded JRE.

    :return: Path to JVM library or None if not found
    """
    if not JRE_DIR.exists():
        return None

    system = platform.system().lower()
    jvm_path = jvm_paths.get(system)
    if jvm_path and jvm_path.exists():
        return str(jvm_path)

    return None


def download_jre(progress_callback=None) -> bool:
    """
    Download and extract JRE from GitHub releases.

    :param progress_callback: Optional callback function(step, percent)
                          step: 'download' or 'extract'
                          percent: 0-100
    :return: True if successful, False otherwise
    """
    system, arch = detect_system_arch()
    extension = "zip" if system == "windows" else "tar.gz"
    filename = f"OpenJDK24U-jre_{arch}_{system}_hotspot_{JRE_VERSION}.{extension}"
    download_url = f"{JRE_BASE_URL}/{JRE_VERSION}/{filename}"

    temp_dir = PACKAGE_DIR / "temp_jre"
    temp_dir.mkdir(exist_ok=True)
    local_file = temp_dir / filename
    try:

        # Download with progress
        def download_hook(block_num, block_size, total_size):
            if progress_callback and total_size > 0:
                downloaded = block_num * block_size
                percent = int((downloaded * 100) / total_size)
                progress_callback('download', min(percent, 100))

        # Disable SSL verification for simplicity
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        urllib.request.urlretrieve(download_url, str(local_file), reporthook=download_hook)

        # Extract
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir(exist_ok=True)

        if local_file.suffix == '.zip':
            with zipfile.ZipFile(local_file, 'r') as zf:
                members = zf.namelist()
                total = len(members)
                for i, member in enumerate(members):
                    zf.extract(member, extract_dir)
                    if progress_callback:
                        progress_callback('extract', int((i + 1) * 100 / total))
        else:
            with tarfile.open(local_file, 'r:gz') as tf:
                members = tf.getmembers()
                total = len(members)
                for i, member in enumerate(members):
                    tf.extract(member, extract_dir)
                    if progress_callback:
                        progress_callback('extract', int((i + 1) * 100 / total))

        # Move extracted JRE to target directory
        if JRE_DIR.exists():
            shutil.rmtree(JRE_DIR)

        # Find the actual JRE directory
        extracted_items = list(extract_dir.iterdir())
        if len(extracted_items) == 1 and extracted_items[0].is_dir():
            # Single directory containing JRE
            shutil.move(str(extracted_items[0]), str(JRE_DIR))
        else:
            # Multiple items, move them all
            JRE_DIR.mkdir(exist_ok=True)
            for item in extracted_items:
                shutil.move(str(item), str(JRE_DIR / item.name))

        # Cleanup
        shutil.rmtree(temp_dir)

        return get_jvm_library_path() is not None

    except Exception as e:
        print(f"Failed to download/extract JRE: {e}", file=sys.stderr)
        print("Please check your network connection and retry.", file=sys.stderr)
        print("If the problem persists, please download it manually:", file=sys.stderr)
        print(f"1. Download: {download_url}", file=sys.stderr)
        print(f"2. Extract the contents to: {JRE_DIR}", file=sys.stderr)
        print(f"3. Ensure the file exists: {jvm_paths.get(platform.system().lower())}.", file=sys.stderr)
        return False


def ensure_jre() -> bool:
    """
    Ensure JRE is available, download if not present.

    :return: True if JRE is ready, False otherwise
    """
    if get_jvm_library_path():
        return True

    print("JRE not found. Downloading... (first-time setup only)")

    def progress_callback(step, percent):
        if step == 'download':
            print(f"\rDownloading: {percent}%", end='', flush=True)
        elif step == 'extract':
            print(f"\rExtracting: {percent}%", end='', flush=True)

    success = download_jre(progress_callback)
    if success:
        print("\nJRE installation complete!")
    else:
        print("\nJRE installation failed!")

    return success


def start_jvm():
    jvm_path = get_jvm_library_path()
    if not jvm_path:
        if not ensure_jre():
            return False
        jvm_path = get_jvm_library_path()
        if not jvm_path:
            return False

    try:
        jpype.startJVM(jvm_path, classpath=[JAR_FILE], convertStrings=False)
        return jpype.isJVMStarted()
    except Exception as e:
        print(f"Failed to start JVM: {e}", file=sys.stderr)
        return False


def initialize():
    """
    Initialize JVM and run MuKiP initialization.
    This should be called before any MuKiP functions.
    """
    global MUKIP_INITIALIZED
    if MUKIP_INITIALIZED:
        return
    try:
        if not jpype.isJVMStarted():
            start_jvm()
        JClass("com.wang_lab.mukip.components.ComponentsLoader").initializeComponents("")
        MUKIP_INITIALIZED = True
    except Exception as e:
        print(f"MuKiP initialization failed: {e}", file=sys.stderr)

def get_class(classpath: str):
    initialize()
    return JClass(classpath)
