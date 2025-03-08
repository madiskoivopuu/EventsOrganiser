


import logging
import time
import threading
logging.basicConfig(level=logging.INFO)
from typing import Callable
from dataclasses import dataclass

from modules import parser, validator, user_listener

@dataclass
class ThreadModule:
    thread_instance: threading.Thread = None
    thread_constructor: Callable[[], threading.Thread]


THREADS: list[ThreadModule] = [
    ThreadModule(None, parser.ParserThread),
    ThreadModule(None, validator.EventValidatorThread),
    ThreadModule(None, user_listener.UserListener),
]

class PrivateEventsServer():
    def __init__(self):
        self.__logger = logging.getLogger(__name__ + "." + type(self).__name__)

    def run(self):
        for i in range(len(THREADS)):
            THREADS[i].thread_instance = THREADS[i].thread_constructor()
            THREADS[i].thread_instance.daemon = True
            THREADS[i].thread_instance.start()

        self.__logger.info("Server started")

        while True:
            for i in range(len(THREADS)):
                if(not THREADS[i].thread_instance.is_alive()):
                    self.__logger.warning(f"{THREADS[i].thread_constructor.__name__} unexpectedly crashed, restarted it")

                    THREADS[i].thread_instance = THREADS[i].thread_constructor()
                    THREADS[i].thread_instance.daemon = True
                    THREADS[i].thread_instance.start()

            time.sleep(5)


if __name__ == "__main__":
    server = PrivateEventsServer()
    server.run()