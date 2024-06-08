from threading import Lock, Thread
from queue import Queue
from datetime import datetime
from config import *

class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
          if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Logger(metaclass = SingletonMeta):
    def __init__(self, log_file_path = f"{LOGS_FOLDER}/", log_queue_length = 1000):

        # Створення лог-файлу з меткою часу
        date_time = datetime.now().strftime("%Y-%m-%d %H%M%S")
        self.log_file_path = f"{log_file_path}log {date_time}.txt"
        file = open(self.log_file_path, 'w', encoding = 'utf-8')
        file.close()
        
        # Сторвення черги та запуск логгеру
        self.log_queue = Queue(maxsize=log_queue_length)
        log_thread = Thread(target = self.__write_data_in_file_thread)
        log_thread.daemon = True
        log_thread.start()

    def log_data(self, data):
        while self.log_queue.full():
            pass
        self.log_queue.put(f"[{datetime.now()}]: {data} \n")
        return True


    # Функція запису даних, взятих з черги
    # Працює у паралельному потоці 
    def __write_data_in_file_thread(self):
        while True:
            if self.log_queue.empty():
                continue
            
            # Відкриття файлу у режимі дописування
            log_file = open(self.log_file_path, 'a', encoding='utf-8')
            
            # Запис у файл, поки черга не спорожніє
            while not self.log_queue.empty():
                log_file.write(self.log_queue.get())
            log_file.close()
    