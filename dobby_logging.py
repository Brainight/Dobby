import logging
import sys

def getDobbyLogger(name:str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(logging.Formatter('[%(levelname)s] %(module)s: %(message)s'))
    
    file_handler = logging.FileHandler(filename='dobby.log', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s - %(module)s: %(message)s'))
    file_handler.setLevel(logging.INFO)
    
    logger.addHandler(stdout_handler)
    logger.addHandler(file_handler)
    return logger

    
def loadDiscordLogging():
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename="discord.log")
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    return logger

def join_multiple_configurations(*args):
    return '\n\n' + '\n\n'.join(args) + '\n'