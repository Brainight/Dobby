import logging
import sys

def getSTDOUTLogger(name:str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('[%(levelname)s] %(module)s: %(message)s'))
    logger.addHandler(handler)
    return logger
    
    
def getFileLogger(name:str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='discord.log')
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