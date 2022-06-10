
import csv

from util.LogUtil import MyLog
from util.SqlalchemyUtil import SQLUtil
from typing import List
from bean.BatchMaterialInfo import BatchInfo

class DataIn(object):
    mylog = MyLog()

    def __init__(self, path="mysql+pymysql://root:123456@192.168.192.137:3306/db_onlymaterial_zhj"):
        self.path = path

    def localFileData(self, local_path:str, tablename=BatchInfo):
        """
        读取本地
        :param dataInfo: 该参数的数据结构为4列
        :param local_path: 本地数据文件路径
        :return: 输出一个可迭代的列表List集合，其中元素为MaterialInfo对象
        """
        resList = []
        with open(local_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                resList.append(tablename(row[0],row[1],row[2],row[3],row[4]))

        return resList

    def mysqlFileData(self, dataInfo, filterCondition=0, limitNum: int = None):
        """
        读取mysql数据库
        :param dataInfo:
        :return: 输出一个可迭代的集合，元素为dataInfo对象
        """
        conn = SQLUtil(path=self.path)
        sql_reader = conn.queryData(dataInfo, filterCondition=filterCondition, limitNum=limitNum)
        resList = []
        for item in sql_reader:
            resList.append(item)
        return resList

    def mssqlFileData(self, dataInfo, filterCondition=1, limitNum: int = None):
        """
        读取sqlserver数据库
        :param dataInfo:
        :return:输出一个可迭代的集合，元素为dataInfo对象
        """
        conn = SQLUtil(databasetype='mssql', path=self.path)
        sql_reader = conn.queryData(dataInfo, filterCondition, limitNum)
        resList = []
        for item in sql_reader:
            resList.append(item)
        return resList


class DataOut(object):

    mylog = MyLog()

    def __init__(self, path):
        self.path = path

    def sqlFileOut(self, dataInfoS):
        """
        将数据输出到mysql中，插入与已有数据不同的数据
        :param dataInfoS:
        :return:
        """
        conn = SQLUtil(path=self.path)
        if isinstance(dataInfoS, List)==True and len(dataInfoS) > 0:  # 判断输入数据是否为批量列表，如果是批量上传，否则单条上传

            res = conn.insertBatchRow(dataInfoS)
        else:
            res = conn.insertOneRow(dataInfoS)

        if res == 0:
            raise Exception('sqlFileOut输出数据failed!!')

    def sqlFileOutUpsert(self, dataInfos):
        """
        将批量数据输出到mysql中,并更新数据
        :param dataInfos:
        :return:
        """
        conn = SQLUtil(path=self.path)
        try:
            if isinstance(dataInfos, List) and len(dataInfos) > 0:  # 判断输入数据是否为批量列表，如果是批量上传，否则单条上传

                conn.upsertBatchRow(dataInfos)
            else:
                conn.upsertOneRow(dataInfos)

        except Exception as e:
            self.mylog.error('sqlFileOutUpsert输出数据failed: {}'.format(e))


