


import logging
import time
logging.basicConfig(level=logging.INFO)

import parser, validator

class PrivateEventsServer():
    def __init__(self):
        self.__logger = logging.getLogger(__name__ + "." + type(self).__name__)

    def run(self):
        parser_thread = parser.ParserThread()
        parser_thread.daemon = True
        parser_thread.start()

        validator_thread = validator.EventValidatorThread()
        validator_thread.daemon = True
        validator_thread.start()

        self.__logger.info("Server started")

        while True:
            if(not parser_thread.is_alive()):
                parser_thread = parser.ParserThread()
                parser_thread.start()
                self.__logger.warning("Parser thread unexpectedly crashed, restarted it")

            if(not validator_thread.is_alive()):
                validator_thread = validator.EventValidatorThread()
                validator_thread.start()
                self.__logger.warning("Event validator thread unexpectedly crashed, restarted it")

            time.sleep(5)


if __name__ == "__main__":
    server = PrivateEventsServer()
    server.run()