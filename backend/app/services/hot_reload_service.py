import asyncio
import time
from pathlib import Path
from typing import Dict, Set, Callable, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.core.enhanced_settings import get_settings
from app.core.configuration_manager import config_manager

class ConfigFileHandler(FileSystemEventHandler):
    """File system event handler for configuration changes"""
    
    def __init__(self, reload_callback: Callable):
        self.reload_callback = reload_callback
        self.last_reload = {}
        self.debounce_seconds = 2  # Avoid multiple rapid reloads
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(('.yml', '.yaml')):
            self._handle_file_change(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(('.yml', '.yaml')):
            self._handle_file_change(event.src_path)
    
    def _handle_file_change(self, file_path: str):
        """Handle configuration file changes with debouncing"""
        current_time = time.time()
        last_time = self.last_reload.get(file_path, 0)
        
        if current_time - last_time > self.debounce_seconds:
            self.last_reload[file_path] = current_time
            self.reload_callback(file_path)

class HotReloadService:
    """Service for hot reloading configuration changes"""
    
    def __init__(self):
        self.observer = None
        self.is_running = False
        self.watched_paths = set()
        self.reload_callbacks = []
        
        # Get configuration paths
        self.config_root = Path(__file__).parent.parent.parent.parent / "config"
        self.env_config_path = self.config_root / "environment"
    
    def start(self):
        """Start watching configuration files for changes"""
        settings = get_settings()
        
        if not settings.ENABLE_HOT_RELOAD:
            return
        
        self.observer = Observer()
        handler = ConfigFileHandler(self._on_config_change)
        
        # Watch main config directory
        if self.config_root.exists():
            self.observer.schedule(handler, str(self.config_root), recursive=True)
            self.watched_paths.add(str(self.config_root))
        
        # Watch environment config directory
        if self.env_config_path.exists():
            self.observer.schedule(handler, str(self.env_config_path), recursive=True)
            self.watched_paths.add(str(self.env_config_path))
        
        self.observer.start()
        self.is_running = True
        print(f"🔥 Hot reload enabled - watching {len(self.watched_paths)} configuration paths")
    
    def stop(self):
        """Stop watching configuration files"""
        if self.observer and self.is_running:
            self.observer.stop()
            self.observer.join()
            self.is_running = False
            print("🛑 Hot reload stopped")
    
    def _on_config_change(self, file_path: str):
        """Handle configuration file changes"""
        print(f"🔄 Configuration file changed: {file_path}")
        
        try:
            # Determine what type of config changed
            file_path_obj = Path(file_path)
            
            if "environment" in file_path:
                # Environment configuration changed
                self._reload_environment_config()
            else:
                # Regular configuration file changed
                config_name = file_path_obj.stem
                self._reload_yaml_config(config_name)
            
            # Execute custom reload callbacks
            for callback in self.reload_callbacks:
                try:
                    callback(file_path)
                except Exception as e:
                    print(f"❌ Error in reload callback: {e}")
            
            print(f"✅ Configuration reloaded successfully")
            
        except Exception as e:
            print(f"❌ Error reloading configuration: {e}")
    
    def _reload_environment_config(self):
        """Reload environment configuration"""
        settings = get_settings(reload=True)
        print(f"🔄 Environment configuration reloaded for: {settings.ENVIRONMENT}")
    
    def _reload_yaml_config(self, config_name: str):
        """Reload specific YAML configuration"""
        config_manager.clear_cache()
        try:
            # Preload the configuration to validate it
            config_manager.get_config(config_name)
            print(f"🔄 YAML configuration reloaded: {config_name}")
        except Exception as e:
            print(f"❌ Error reloading {config_name}: {e}")
    
    def add_reload_callback(self, callback: Callable[[str], None]):
        """Add a callback to be executed when configuration changes"""
        self.reload_callbacks.append(callback)
    
    def remove_reload_callback(self, callback: Callable[[str], None]):
        """Remove a reload callback"""
        if callback in self.reload_callbacks:
            self.reload_callbacks.remove(callback)

# Global instance
hot_reload_service = HotReloadService()