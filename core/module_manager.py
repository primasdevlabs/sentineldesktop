"""
-------------------------------------------------------------------------------
Primas Dev Labs - Sentinel Desktop AI
-------------------------------------------------------------------------------
File: core/module_manager.py
Description: The dynamic lifecycle manager for Sentinel's modular system.
             Handles registration, instantiation, and runtime status of hardware
             and software modules.
Author: Primas Dev Labs
-------------------------------------------------------------------------------
"""

import logging
from typing import Dict, Any, Type, Optional
from .events import Events

class ModuleManager:
    """
    Registry and lifecycle controller for Sentinel modules.
    
    Ensures that modules (STT, TTS, Wake Word) can be enabled, disabled,
    or restarted at runtime without crashing the core system.
    """
    
    def __init__(self, brain: Any) -> None:
        """
        Initializes the manager with a reference to the Core Brain.
        
        Args:
            brain: Reference to the SentinelCore instance.
        """
        self.brain = brain
        self.logger = logging.getLogger("ModuleManager")
        # Registry structure: name -> {instance, class, args, kwargs, status}
        self.registry: Dict[str, Dict[str, Any]] = {} 

    def register(self, name: str, instance_class: Type, *args: Any, **kwargs: Any) -> None:
        """
        Adds a module definition to the system registry.
        
        Note: This does not instantiate the module; it only stores the 
        recipe for how to create it when 'enable' is called.
        
        Args:
            name: Unique identifier for the module.
            instance_class: The class to be instantiated.
            *args: Positional arguments for the class constructor.
            **kwargs: Keyword arguments for the class constructor.
        """
        self.registry[name] = {
            "class": instance_class,
            "args": args,
            "kwargs": kwargs,
            "instance": None,
            "status": "inactive"
        }

    def enable(self, name: str) -> bool:
        """
        Instantiates and starts a registered module.
        
        If the module has a 'start()' method, it is invoked. 
        Broadcasts status changes via the event bus.
        
        Args:
            name: Identifier of the module to enable.
        Returns:
            bool: True if the module is active.
        """
        if name not in self.registry: 
            return False
            
        mod = self.registry[name]
        if mod["status"] == "active": 
            return True
        
        try:
            self.logger.info(f"Enabling module: {name}")
            # Dynamic instantiation with stored arguments
            mod["instance"] = mod["class"](*mod["args"], **mod["kwargs"])
            
            # Standard lifecycle hook
            if hasattr(mod["instance"], "start"):
                mod["instance"].start()
                
            mod["status"] = "active"
            Events.emit("module.status_changed", name=name, status="active")
            return True
        except Exception as e:
            self.logger.error(f"Failed to enable module '{name}': {e}")
            mod["status"] = "error"
            Events.emit("module.status_changed", name=name, status="error")
            return False

    def disable(self, name: str) -> bool:
        """
        Stops and unloads a module.
        
        Invokes the module's 'stop()' method if it exists, then clears
        the instance from memory to free hardware resources (Mic/Audio).
        
        Args:
            name: Identifier of the module to disable.
        Returns:
            bool: True if the module is now inactive.
        """
        if name not in self.registry: 
            return False
            
        mod = self.registry[name]
        if mod["status"] != "active": 
            return True
        
        try:
            self.logger.info(f"Disabling module: {name}")
            if hasattr(mod["instance"], "stop"):
                mod["instance"].stop()
            
            # Break references to allow Garbage Collection
            mod["instance"] = None
            mod["status"] = "inactive"
            Events.emit("module.status_changed", name=name, status="inactive")
            return True
        except Exception as e:
            self.logger.error(f"Failed to gracefully disable '{name}': {e}")
            return False

    def restart(self, name: str) -> bool:
        """
        Performs a full stop/start cycle on a module.
        
        Args:
            name: Identifier of the module.
        Returns:
            bool: True if the module was successfully restarted.
        """
        self.disable(name)
        return self.enable(name)

    def get_status(self, name: str) -> str:
        """Retrieves the current operational status of a module."""
        return self.registry.get(name, {}).get("status", "unknown")
