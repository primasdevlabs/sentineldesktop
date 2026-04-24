import logging
import importlib

class DependencyManager:
    @staticmethod
    def check_and_import(module_name, fallback_callback=None):
        try:
            return importlib.import_module(module_name)
        except ImportError:
            logging.warning(f"Optional module '{module_name}' not found. Using fallback.")
            if fallback_callback:
                return fallback_callback()
            return None

    @staticmethod
    def is_available(module_name):
        try:
            importlib.util.find_spec(module_name)
            return True
        except:
            return False
