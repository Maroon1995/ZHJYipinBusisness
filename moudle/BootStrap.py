import sys

sys.path.append('../')

from time import time
from cio.CacheVariable import CacheValue
from process.Produce import getDatafromHTTP
from process.Consumer import getResult
from util.RedisUtil import RedisHelper
from util.SqlalchemyUtil import SQLUtil
from util.LogUtil import MyLog
from bean.SpecialCharactersInfo import StrReplaceInfo
from common.DataInOut import DataIn, DataOut
from common.Configuration import readConfig
from sqlalchemy import exists, and_, or_


def run(task_id: str, task_data: str):
    """
    :param task_id: 任务id
    :param task_data: 接收到的任务数据
    :return:
    """
    # ------------------------------------------------------------------------------------------------
    # TODO 0- 配置文件
    cfg = readConfig()
    base_config = cfg["basevariable"]
    redis_config = cfg["database"]["redis"]["config"]
    mssql_config = cfg["database"]["mssql"]
    # TODO 1- 参数设置
    similarthreshold: float = base_config["similarthreshold"]
    startmp_threshold: int = base_config["startmp_threshold"]
    core_process: int = base_config["core_process"]

    # db_path = cfg["database"]["mysql"]["url"]                 # mysql 数据库的url
    db_path = mssql_config["url"]                               # mssql 数据库的url
    un_task_data = task_data.encode("UTF-8").decode("UTF-8")    # 请求到的任务数据

    # ----------------------------------------------------------------------------------------------
    # TODO 2- 实例化对象
    conn_db = SQLUtil(path=db_path)
    redisUtil = RedisHelper(redis_config["host"], redis_config["port"], redis_config["db"])
    input = DataIn(db_path)
    output = DataOut(db_path)
    mylog = MyLog()
    # ------------------------------------------------------------------------------------------------
    # TODO 3- 获取数据 getData（包含了数据处理）————进行了缓存优化
    # （1）替换字符
    SRIList = input.mysqlFileData(StrReplaceInfo)  # 替换字符
    # （2）批量数据
    # 从HTTP获取数据
    BUIListIsDigit, BUIListNoDigit, query_milist = getDatafromHTTP(input=input, output=output, task_id=task_id,
                                                                   task_data=un_task_data,
                                                                   SRIList=SRIList,
                                                                   startmp_threshold=startmp_threshold,
                                                                   core_process=core_process)

    print("BUIListIsDigit: {}; BUIListNoDigit: {};query_milist:{}".format(len(BUIListIsDigit), len(BUIListNoDigit),
                                                                          len(query_milist)))
    # （3）主量数据
    MUIListIsDigit, MUIListNoDigit = CacheValue(input=input, SRIList=SRIList, conn_db=conn_db, redisUtil=redisUtil,
                                                expireTime=6000)
    print("MUIListIsDigit: {}; MUIListNoDigit: {}".format(len(MUIListIsDigit), len(MUIListNoDigit)))
    # ------------------------------------------------------------------------------------------------
    # TODO 3- 计算相似度 CalculateSimlary 并输出结果 Data.DataOut ————进行了多进程优化
    if (len(BUIListIsDigit) == 0 and len(BUIListNoDigit) == 0 and len(query_milist) == 0):
        mylog.error("输入的数据为None")
        return 0
    else:
        try:
            if len(BUIListIsDigit) > 0:  # 数值型
                getResult(output, BUIListIsDigit, MUIListIsDigit, similarthreshold, core_process,startmp_threshold)
            if len(BUIListNoDigit) > 0:  # 非数值型
                getResult(output, BUIListNoDigit, MUIListNoDigit, similarthreshold, core_process,startmp_threshold)
            return 1
        except Exception as e:
            mylog.error("getResult Failed:{}".format(e))
            return 3


if __name__ == '__main__':
    # 任务id
    task_id: str = "6af27c8e-6c6a-4c5e-b716-4d6d41d9a64b"
    # 任务data
    task_data = """{"data":[{"MaterialDrawing": "ZWY-2", "Name": "保险丝3", "EnglishName": "ПРОВОЛОКА3", "Unit": "Meter3"},{"MaterialDrawing": "ZXR-11C", "Name": "保险丝8", "EnglishName": "ПРОВОЛОКА8", "Unit": "Meter8"},{"MaterialDrawing": "CCCCCCC", "Name": "保险丝3", "EnglishName": "ПРОВОЛОКА3", "Unit": "Meter3"},{"MaterialDrawing": "234356", "Name": "保险丝3", "EnglishName": "ПРОВОЛОКА3", "Unit": "Meter3"}]}"""

    start_time2 = time()
    res = run(task_id, task_data)
    end_time2 = time()

    print('存储耗时(ms)：', (end_time2 - start_time2) * 1000)
