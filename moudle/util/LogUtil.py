
import logging
import getpass
from common.Configuration import readConfig

# 定义MyLog类

class MyLog(object):
    '''这个类用于创建一个自用的log'''

    def __init__(self):  # 类MyLog的构造函数
        user = getpass.getuser()  # 返回当前系统用户名称
        fmt = '%(asctime)-12s %(levelname)-8s %(name)-10s %(message)-12s'

        self.logger = logging.getLogger(user)  # 返回一个特定名字的日志
        self.logger.setLevel(logging.ERROR)  # 对显示的日志信息设置一个阈值低于DEBUG级别的不显示

        logFile = readConfig()["path"]["log_path"]  # 日志文件路径
        formatter = logging.Formatter(fmt) # 日志格式

        '''日志显示到屏幕上并输出到日志文件内'''
        logHand = logging.FileHandler(logFile)  # 输出日志文件，文件名是logFile
        logHand.setFormatter(formatter)  # 为logHand以formatter设置格式
        logHand.setLevel("ERROR")  # 设置输出到日志文件logfile中的日志级别

        logHandSt = logging.StreamHandler()  # class logging.StreamHandler(stream=None)
        # 返回StreamHandler类的实例，如果stream被确定，使用该stream作为日志输出，反之，使用
        # sys.stderr
        logHandSt.setFormatter(formatter)  # 为logHandSt以formatter设置格式
        self.logger.addHandler(logHand)  # 添加特定的handler logHand到日志文件logger中
        self.logger.addHandler(logHandSt)  # 添加特定的handler logHandSt到日志文件logger中

    '''日志的5个级别对应以下的五个函数'''

    def debug(self, msg):
        self.logger.debug(msg)  # Logs a message with level DEBUG on this logger.

    # The msg is the message format string

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

