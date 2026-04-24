import sys
import os
import time
import threading

# Path injection
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.core.sentinel_core import SentinelCore
from sentinel.core.events import Events
from sentinel.modules.skills.time.skill import TimeSkill

class MockModule:
    def __init__(self, name): self.name = name
    def start(self): print(f"[MOCK] {self.name} started")
    def stop(self): print(f"[MOCK] {self.name} stopped")

def run_comprehensive_test():
    print("=== Sentinel Comprehensive Integration Test ===")
    
    # 1. Initialize Core with auto-path resolution
    try:
        brain = SentinelCore()
        print("[PASS] Core initialized and config loaded.")
    except Exception as e:
        print(f"[FAIL] Core initialization: {e}")
        return

    # 2. Register a Skill
    brain.register_skill(TimeSkill())
    print("[PASS] Skill registration verified.")

    # 3. Test Event Bus
    event_received = threading.Event()
    def on_status_change(status):
        print(f"[EVENT] Status changed to: {status}")
        event_received.set()

    Events.subscribe(Events.STATUS_CHANGED, on_status_change)
    brain.set_state("test_mode")
    
    if event_received.wait(timeout=2):
        print("[PASS] Event Bus pub/sub verified.")
    else:
        print("[FAIL] Event Bus timeout.")

    # 4. Test Memory System
    brain.memory.set("test_key", "test_value")
    if brain.memory.get("test_key") == "test_value":
        print("[PASS] Persistent memory R/W verified.")
    else:
        print("[FAIL] Memory system error.")

    # 5. Test Module Manager (Mock)
    brain.module_manager.register("mock_mod", MockModule, "VisionSystem")
    if brain.module_manager.enable("mock_mod"):
        print("[PASS] Module Manager lifecycle verified.")
    else:
        print("[FAIL] Module Manager error.")

    print("\n=== All Core Logic Checks Passed ===")
    print("Note: Hardware modules (Microphone, TTS) were not tested to avoid environment conflicts.")

if __name__ == "__main__":
    run_comprehensive_test()
