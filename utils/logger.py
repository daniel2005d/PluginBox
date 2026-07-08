import colorlog
import logging
import sys

class Logger:

    def __init__(self, task_name:str):
        self._log = self.setup_logger('information', self.get_formatter('information','cyan'))
        self._task = task_name

    def error(self, message:str):
        self._log.error(f'[{self._task}]: {message}')

    def info(self,  message:str):
        self._log.info(f'[{self._task}]: {message}')

    def warning(self, message:str):
        self._log.warning(f'[{self._task}]: {message}')



    def get_formatter(self, name:str, color:str):
        #COLORS = ['green', 'yellow', 'blue',  'cyan', 'white']
        formatter = colorlog.ColoredFormatter(
                fmt=f"%(log_color)s%(asctime)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                log_colors={
                    'DEBUG': color,
                    'INFO': color,
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white'
                }
            )
        
        return formatter
    
    def setup_logger(self, name, formatter=None):
        if not formatter:
            formatter = self.get_formatter(name)
        
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(formatter)

        logger = logging.getLogger(name)
        if not logger.hasHandlers():
            logger.propagate = False
            logger.addHandler(streamHandler)

            logger.setLevel(logging.__dict__["INFO"])

        return logger