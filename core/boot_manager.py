"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: core/boot_manager.py
Description: Handles OS-level boot registration and autostart capabilities.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import os
import platform
import sys
import logging

class BootManager:
    """
    Cross-platform manager for persistent system registration.
    
    Provides static methods to register or unregister the Sentinel 
    executable from the OS's startup sequence (Windows Registry or Linux XDG).
    """
    
    @staticmethod
    def enable_autostart() -> bool:
        """
        Registers Sentinel to launch automatically upon user login.
        
        Logic:
        - Windows: Writes to HKEY_CURRENT_USER Run key.
        - Linux: Creates an XDG autostart .desktop file in ~/.config/autostart.
        
        Returns:
            bool: True if registration was successful.
        """
        if platform.system() == "Windows":
            try:
                import winreg
                # Get the absolute path to the current python executable and script
                pth = sys.executable
                script_path = os.path.abspath(sys.argv[0])
                
                # Command runs Sentinel in minimized mode
                cmd = f'"{pth}" "{script_path}" --minimized'
                
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.SetValueEx(reg_key, "SentinelAI", 0, winreg.REG_SZ, cmd)
                return True
            except Exception as e:
                logging.error(f"Failed to set Windows autostart: {e}")
                
        elif platform.system() == "Linux":
            # XDG Autostart Specification implementation
            autostart_dir = os.path.expanduser("~/.config/autostart")
            os.makedirs(autostart_dir, exist_ok=True)
            desktop_file = os.path.join(autostart_dir, "sentinel.desktop")
            
            with open(desktop_file, "w") as f:
                f.write(
                    f"[Desktop Entry]\n"
                    f"Type=Application\n"
                    f"Name=Sentinel AI\n"
                    f"Exec={sys.executable} {os.path.abspath(sys.argv[0])} --minimized\n"
                    f"Hidden=false\n"
                    f"NoDisplay=false\n"
                    f"X-GNOME-Autostart-enabled=true\n"
                )
            return True
            
        return False

    @staticmethod
    def disable_autostart() -> bool:
        """
        Removes Sentinel from the OS's startup sequence.
        
        Returns:
            bool: True if unregistration was successful.
        """
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.HKEY_CURRENT_USER
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.DeleteValue(reg_key, "SentinelAI")
                return True
            except Exception: 
                pass
        
        elif platform.system() == "Linux":
            autostart_file = os.path.expanduser("~/.config/autostart/sentinel.desktop")
            if os.path.exists(autostart_file):
                os.remove(autostart_file)
                return True
                
        return False
