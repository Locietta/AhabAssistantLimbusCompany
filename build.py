#!/usr/bin/env python3
"""
Build script for AALC (Ahab Assistant Limbus Company)
Handles version injection, translation file generation, and executable bundling.
"""

import os
import sys
import shutil
import subprocess
import argparse
import glob
from pathlib import Path

import PyInstaller.__main__


def generate_qm_files():
    """Generate .qm translation files from .ts files."""
    print("Generating .qm translation files...")

    i18n_dir = Path("i18n")
    if not i18n_dir.exists():
        print("No i18n directory found, skipping translation file generation")
        return

    for ts_file in i18n_dir.glob("*.ts"):
        qm_file = ts_file.with_suffix(".qm")
        print(f"Generating {qm_file} from {ts_file}")

        cmd = ["pyside6-lrelease", str(ts_file), "-qm", str(qm_file)]
        subprocess.run(cmd, check=True, capture_output=True, text=True)


def build_executable():
    """Build the executable using PyInstaller Python API."""
    print("Building main executable...")

    # Build main application using spec file

    PyInstaller.__main__.run(
        [
            "main.spec",
            "-y",
        ]
    )
    print("Main executable built successfully")

    # Build updater
    print("Building updater executable...")

    PyInstaller.__main__.run(
        [
            "updater.spec",
            "--distpath=./dist/AALC",
            "-y",
        ]
    )
    print("Updater executable built successfully")


def bundle_resources(version: str):
    """Bundle all resources into the final distribution."""
    print("Bundling resources...")

    dist_release_dir = Path("dist_release")
    aalc_dir = dist_release_dir / "AALC"

    # Clean dist_release directories
    if dist_release_dir.exists():
        shutil.rmtree(dist_release_dir)

    # Ensure AALC directory exists
    aalc_dir.mkdir(exist_ok=True, parents=True)

    # Copy dist contents to dist_release
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.copytree(dist_dir, dist_release_dir, dirs_exist_ok=True)

    # Copy 3rdparty
    third_party_src = Path("3rdparty")
    if third_party_src.exists():
        third_party_dest = aalc_dir / "3rdparty"
        shutil.copytree(third_party_src, third_party_dest)
        print("Copied 3rdparty directory")

    # Copy assets
    assets_src = Path("assets")
    if assets_src.exists():
        assets_dest = aalc_dir / "assets"
        shutil.copytree(assets_src, assets_dest)
        print("Copied assets directory")

    # modify the version txt file in assets
    version_file = assets_dest / "config" / "version.txt"
    with open(version_file, "w") as f:
        f.write(version)

    # Copy translation files
    i18n_dest = aalc_dir / "i18n"
    i18n_dest.mkdir(exist_ok=True)

    qm_files = list(Path("i18n").glob("*.qm"))
    for qm_file in qm_files:
        shutil.copy2(qm_file, i18n_dest / qm_file.name)
        print(f"Copied {qm_file}")

    # Copy LICENSE and README
    for file in ["LICENSE", "README.md"]:
        src_file = Path(file)
        if src_file.exists():
            shutil.copy2(src_file, aalc_dir / file)
            print(f"Copied {file}")

    # Create 7z archive
    print(f"Creating 7z archive: AALC_{version}.7z")
    archive_path = dist_release_dir / f"AALC_{version}.7z"

    subprocess.run(
        [
            "7z",
            "a",
            "-mx=7",
            str(archive_path.resolve()),
            f"{str(aalc_dir.resolve())}",
        ]
    )

    print(f"Archive size: {archive_path.stat().st_size / (1024 * 1024):.2f} MB")


def main():
    """Main build function."""
    parser = argparse.ArgumentParser(description="Build AALC application")
    parser.add_argument("--version", required=True, help="Version number to inject")

    args = parser.parse_args()

    print(f"Starting build process for version: {args.version}")
    print(f"Working directory: {os.getcwd()}")

    generate_qm_files()
    build_executable()
    bundle_resources(args.version)
    print(f"Build process completed successfully for version {args.version}!")


if __name__ == "__main__":
    main()
