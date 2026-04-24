import gc
import psutil
import logging
import threading
import time

class ResourceManager:
    def __init__(self, memory_cap_mb=256):
        self.memory_cap = memory_cap_mb
        self.logger = logging.getLogger("ResourceManager")
        self._stop_event = threading.Event()

    def start_monitoring(self):
        threading.Thread(target=self._monitor_loop, daemon=True).start()

    def _monitor_loop(self):
        while not self._stop_event.is_set():
            process = psutil.Process()
            mem_usage = process.memory_info().rss / (1024 * 1024)
            
            if mem_usage > self.memory_cap:
                self.logger.warning(f"Memory usage ({mem_usage:.2f}MB) exceeds cap. Triggering GC.")
                gc.collect()
            
            time.sleep(60) # check every minute

    def unload_module(self, module):
        # Implementation for explicit cleanup of heavy resources
        pass

    def stop(self):
        self._stop_event.set()
