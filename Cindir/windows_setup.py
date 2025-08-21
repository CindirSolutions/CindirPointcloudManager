#!/usr/bin/env python3
"""
Windows setup script for Cindir PointCloud Manager
Creates a proper Windows executable with dependencies
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    
    dependencies = [
        "requests>=2.28.0",
        "pyinstaller>=5.0.0"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✓ Installed {dep}")
        except subprocess.CalledProcessError as e:
            print(f"✗ Failed to install {dep}: {e}")
            return False
    
    return True

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cindir_pointcloud_manager_obfuscated.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['requests', 'json', 'socket', 'platform', 'datetime', 'base64'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CindirPointCloudManager_Obfuscated',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)'''
    
    with open('cindir_obfuscated.spec', 'w') as f:
        f.write(spec_content)
    
    print("✓ Created PyInstaller spec file for obfuscated version")

def build_executable():
    """Build the Windows executable"""
    print("Building heavily obfuscated Windows executable...")
    
    try:
        # Use the obfuscated spec file for building
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "cindir_obfuscated.spec"
        ])
        print("✓ Build completed successfully!")
        print("✓ Heavily obfuscated executable created: dist/CindirPointCloudManager_Obfuscated.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Build failed: {e}")
        return False

def create_installer():
    """Create NSIS installer script (optional)"""
    nsis_script = '''!define APPNAME "Cindir PointCloud Manager"
!define COMPANYNAME "Cindir Technologies"
!define DESCRIPTION "Professional PointCloud Processing Software"
!define VERSIONMAJOR 2
!define VERSIONMINOR 1
!define VERSIONBUILD 3

!define HELPURL "http://www.cindir.com/support"
!define UPDATEURL "http://www.cindir.com/updates"
!define ABOUTURL "http://www.cindir.com"

!define INSTALLSIZE 15000

RequestExecutionLevel admin

InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"
Name "${APPNAME}"
outFile "CindirPointCloudManagerInstaller.exe"

page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
        messageBox mb_iconstop "Administrator rights required!"
        setErrorLevel 740
        quit
${EndIf}
!macroend

function .onInit
	setShellVarContext all
	!insertmacro VerifyUserIsAdmin
functionEnd

section "install"
	setOutPath $INSTDIR
	file "dist\\CindirPointCloudManager.exe"
	file "README.md"
	
	writeUninstaller "$INSTDIR\\uninstall.exe"
	
	createDirectory "$SMPROGRAMS\\${COMPANYNAME}"
	createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\CindirPointCloudManager.exe" "" ""
	createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\CindirPointCloudManager.exe" "" ""
	
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayName" "${APPNAME}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "UninstallString" "$\\"$INSTDIR\\uninstall.exe$\\""
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "QuietUninstallString" "$\\"$INSTDIR\\uninstall.exe$\\" /S"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "InstallLocation" "$\\"$INSTDIR$\\""
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayIcon" "$\\"$INSTDIR\\CindirPointCloudManager.exe$\\""
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "Publisher" "${COMPANYNAME}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "HelpLink" "${HELPURL}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
	WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "VersionMinor" ${VERSIONMINOR}
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoModify" 1
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "NoRepair" 1
	WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "uninstall"
	delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
	delete "$DESKTOP\\${APPNAME}.lnk"
	rmDir "$SMPROGRAMS\\${COMPANYNAME}"
	
	delete $INSTDIR\\CindirPointCloudManager.exe
	delete $INSTDIR\\README.md
	delete $INSTDIR\\uninstall.exe
	rmDir $INSTDIR
	
	DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${COMPANYNAME} ${APPNAME}"
sectionEnd'''
    
    with open('installer.nsi', 'w') as f:
        f.write(nsis_script)
    
    print("✓ Created NSIS installer script (installer.nsi)")
    print("  Note: You'll need NSIS installed to build the installer")

if __name__ == "__main__":
    print("=== Cindir PointCloud Manager - Windows Build Script ===\n")
    
    # Check if we're on Windows or if this is a cross-compilation
    if os.name != 'nt':
        print("⚠️  Note: Building on non-Windows system. The executable will still work on Windows.")
    
    print("Step 1: Installing dependencies...")
    if not install_dependencies():
        print("❌ Failed to install dependencies. Please check your internet connection.")
        sys.exit(1)
    
    print("\nStep 2: Creating PyInstaller spec file...")
    create_spec_file()
    
    print("\nStep 3: Building executable...")
    if not build_executable():
        print("❌ Build failed. Please check the error messages above.")
        sys.exit(1)
    
    print("\nStep 4: Creating installer script...")
    create_installer()
    
    print("\n=== Build Complete! ===")
    print("✓ Executable: dist/CindirPointCloudManager.exe")
    print("✓ Installer script: installer.nsi")
    print("\nTo create the installer (optional):")
    print("1. Install NSIS (Nullsoft Scriptable Install System)")
    print("2. Right-click installer.nsi and select 'Compile NSIS Script'")
    print("\nThe standalone executable in dist/ folder is ready to distribute!")