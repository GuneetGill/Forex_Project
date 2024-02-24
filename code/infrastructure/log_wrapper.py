import logging #logging libary
import os

'''
Logging is a mechanism in software development that allows the 
recording of information about the execution of a program. 
It provides a way to capture and store messages, warnings, errors, 
and other relevant information during the runtime of an application

The Python standard library includes a built-in logging module that
facilitates the implementation of logging in Python programs.

Logger: A logger is an object that is used to emit log messages from a Python application. 
Loggers are named, and hierarchical names are separated by dots, similar to Python packages.

Handler: A handler is responsible for dispatching the log messages to the appropriate output.
Handlers can send log messages to various destinations, such as the console, files, 
or external services.

Formatter: A formatter defines the layout and content of the log messages. 
It specifies how log records are rendered as text.

Level: Log messages are assigned a severity level, such as DEBUG, INFO, WARNING, ERROR, 
or CRITICAL. Developers can set a minimum level for a logger, and messages below that 
level will be ignored.
'''


#telling log library what format we want to log each time
LOG_FORMAT = "%(asctime)s %(message)s"
DEFAULT_LEVEL = logging.DEBUG

class LogWrapper:

    PATH = './logs' #hard coded we will run bot from root of code COULD U SMTH DIFF

    #name of log the file name
    #mode is overwrite the exisitng logs to append change it to a 
    def __init__(self, name, mode="w"):

        #if directory isnt there make one
        self.create_directory()
        self.filename = f"{LogWrapper.PATH}/{name}.log"

        #make a logger
        self.logger = logging.getLogger(name)
        #we defined this above
        self.logger.setLevel(DEFAULT_LEVEL)

        #which file to write to and write, appedning or etc.
        file_handler = logging.FileHandler(self.filename, mode=mode)
        #how we want to format it 
        formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')

        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info(f"LogWrapper init() {self.filename}")

    #check if path exists 
    def create_directory(self):
        if not os.path.exists(LogWrapper.PATH):
            #if it doesnt exist make directory
            os.makedirs(LogWrapper.PATH)










