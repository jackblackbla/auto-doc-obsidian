import logging
import os
from datetime import datetime

class CustomLogger:
    def __init__(self, name: str, log_dir: str = "logs"):
        self.name = name
        self.log_dir = log_dir
        self.logger = None
        self.setup_logger()
        
    def setup_logger(self):
        """로거 초기 설정"""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            
        log_file = os.path.join(
            self.log_dir,
            f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        # 파일 핸들러 추가
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)
        
        # 콘솔 핸들러 추가
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # 포매터 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        # 핸들러 등록
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def debug(self, message: str):
        self.logger.debug(message)
        
    def info(self, message: str):
        self.logger.info(message)
        
    def warning(self, message: str):
        self.logger.warning(message)
        
    def error(self, message: str):
        self.logger.error(message)
        
    def critical(self, message: str):
        self.logger.critical(message)