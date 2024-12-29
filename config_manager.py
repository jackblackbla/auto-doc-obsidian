import json
import os
from typing import Dict, Any, Optional

class ConfigManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """설정 파일 로드"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {}
            
    def save_config(self) -> None:
        """설정 저장"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def get_value(self, key: str, default: Any = None) -> Any:
        """설정 값 조회"""
        return self.config.get(key, default)
        
    def set_value(self, key: str, value: Any) -> None:
        """설정 값 설정"""
        self.config[key] = value
        self.save_config()