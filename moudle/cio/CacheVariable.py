
import json

from typing import List
from common.CalculateVector import getVectorString
from common.CalculateSymbol import getNoSymbol
from common.DataInOut import DataIn
from bean.MainMaterialUniformVectorInfo import MaterialUniform
from bean.SpecialCharactersInfo import StrReplaceInfo
from util.RedisUtil import RedisHelper
from util.SqlalchemyUtil import SQLUtil


def jsonTodict(stringdict: str):
    """
    将json字符串转换成字典，并重新封装成MaterialUniform实例对象
    :param stringdict: json字符串
    :return:
    """
    dicts = json.loads(stringdict)
    # 重新封装
    return MaterialUniform(dicts.get("Code"), dicts.get("MaterialDrawing"), dicts.get("uniformitem"),
                                               dicts.get("EnglishName"), dicts.get("Name"),
                                               dicts.get("Unit"),dicts.get("FirstClass"),
                                               dicts.get("vector"), dicts.get("status"))


def getIsOrNoDigitList(username: str, redisUtil: RedisHelper, expireTime: int):
    """
    读取redis缓存数据，并转换成List[MaterialUniform]
    :param username: redis中的哈希表名称
    :param redisUtil: redis工具类
    :return:
    """

    MUIListDict = redisUtil.getall_values_hset(username, expireTime)

    return list(map(lambda x: jsonTodict(x), MUIListDict))


def CacheValue(input: DataIn, SRIList: List[StrReplaceInfo], conn_db: SQLUtil, redisUtil: RedisHelper, expireTime: int):
    """
        使其以服务的形式在后台一直执行
    :param input: 实例化的输出对象DataIn
    :param SRIList: 替换字符列表
    :param conn_db: DB数据库实例对象SQLUtil
    :param redisUtil: redis工具类实例
    :param expireTime: redis中数据有效期
    :return: MUIListIsDigit, MUIListNoDigit
    """
    MUIListIsDigit: List = []
    MUIListNoDigit: List = []
    newList = []  # 存放status=2，需要被更新的MaterialUniform

    flag: int = conn_db.mainKeyExists(MaterialUniform,
                                      MaterialUniform.status == 1)  # 查询MaterialUniform表中是否存在status为1的数据，若存在则更缓存redis
    if flag == 0 and redisUtil.is_existsKey("MUIListIsDigit", expireTime) == True and redisUtil.is_existsKey(
            "MUIListNoDigit", expireTime) == True:  # 如果，两个username如果均存在且flag=0，则从redis中获取
        print("从redis中获取")
        MUIListIsDigit = getIsOrNoDigitList("MUIListIsDigit", redisUtil, expireTime)
        MUIListNoDigit = getIsOrNoDigitList("MUIListNoDigit", redisUtil, expireTime)

    elif flag == 1 and redisUtil.is_existsKey("MUIListIsDigit", expireTime) == True and redisUtil.is_existsKey(
            "MUIListNoDigit", expireTime) == True:  # 如果，两个username均存在, 且flag=1，则更新redis中对应的值，然后再获取数据
        # 从DB中获取MaterialUniform中status == 1的所有数据
        MUIListStatus: List[MaterialUniform] = input.mysqlFileData(MaterialUniform,
                                                                       filterCondition=MaterialUniform.status == 1)
        for i in range(len(MUIListStatus)): # 更新数据
            eleMUIStatus = MUIListStatus[i]
            eleMUIStatus.vector = getVectorString(eleMUIStatus.MaterialDrawing)  # 更新向量
            eleMUIStatus.uniformitem = getNoSymbol(eleMUIStatus, SRIList)  # 更新uniformitem
            eleMUIStatus.status = 0  # 将状态更新成0，表示已经成为历史物料
            new_data = json.dumps(dict(eleMUIStatus))
            dicts = dict(eleMUIStatus)
            newList.append(MaterialUniform(dicts.get("Code"), dicts.get("MaterialDrawing"), dicts.get("uniformitem"),
                                               dicts.get("EnglishName"), dicts.get("Name"),
                                               dicts.get("Unit"),dicts.get("FirstClass"),
                                               dicts.get("vector"), dicts.get("status"))) # 将更后的数据添加到等待同步到DB数据库的列表中

            if redisUtil.isExists_hset("MUIListIsDigit", eleMUIStatus.MaterialDrawing,
                                       expireTime) == 1:  # 如果存在,则先删除该key-value，再添加key_newvalue
                redisUtil.del_hset("MUIListIsDigit", eleMUIStatus.MaterialDrawing, expireTime)
                redisUtil.add_hset("MUIListIsDigit", eleMUIStatus.MaterialDrawing, new_data, expireTime)

            elif redisUtil.isExists_hset("MUIListNoDigit", eleMUIStatus.MaterialDrawing,
                                         expireTime) == 1:  # 如果存在,则先删除该key-value，再添加key_newvalue
                redisUtil.del_hset("MUIListNoDigit", eleMUIStatus.MaterialDrawing, expireTime)
                redisUtil.add_hset("MUIListNoDigit", eleMUIStatus.MaterialDrawing, new_data, expireTime)
            else:
                if eleMUIStatus.uniformitem.isdigit():  # 以上两种情况都不存在，则直接判断是否为数值型字符串，然后添加
                    redisUtil.add_hset("MUIListIsDigit", eleMUIStatus.MaterialDrawing, new_data, expireTime)
                else:
                    redisUtil.add_hset("MUIListNoDigit", eleMUIStatus.MaterialDrawing, new_data, expireTime)

    else:  # 否则，从DB数据库中获取,并重新更新redis中的全部数据
        # 从数据库中获取数据
        print("从DB数据库获取,并更新数据")
        # 从数据库中获取数据
        MUIList: List[MaterialUniform] = input.mysqlFileData(MaterialUniform)
        # 清除一次redis
        redisUtil.flushData("MUIListIsDigit")
        redisUtil.flushData("MUIListNoDigit")
        # ---------------------
        for i in range(len(MUIList)):
            eleMUI = MUIList[i]
            # -----------------------------------------------
            # （1）更新MaterialUniform中的向量vector，当状态status为1的时候
            if eleMUI.status == 1:  # 当eleMUI状态为1时，说明该图号已经被确认过，需要对其进行一次更新向量的操作
                eleMUI.vector = getVectorString(eleMUI.uniformitem)  # 更新向量
                eleMUI.uniformitem = getNoSymbol(eleMUI, SRIList)  # 更新uniformitem
                eleMUI.status = 0  # 更改状态为3，防止下次读取的时候，进行多余的向量更新操作
                dicts = dict(eleMUI)
                print(dicts)
                newList.append(MaterialUniform(dicts.get("Code"), dicts.get("MaterialDrawing"), dicts.get("uniformitem"),
                                    dicts.get("EnglishName"), dicts.get("Name"),
                                    dicts.get("Unit"), dicts.get("FirstClass"),
                                    dicts.get("vector"), dicts.get("status")))  # 将更后的数据添加到等待同步到DB数据库的列表中

            # -----------------------------------------------
            # (2) 更新缓存redis
            new_data = json.dumps(dict(eleMUI))
            if eleMUI.uniformitem.isdigit():  # 过滤，分类出数值字符串和非数值字符串
                MUIListIsDigit.append(eleMUI)  # 添加到列表
                redisUtil.add_hset("MUIListIsDigit", eleMUI.MaterialDrawing, new_data, expireTime)  # 添加到缓存哈希表“MUIListIsDigit”中
            else:
                MUIListNoDigit.append(eleMUI)
                redisUtil.add_hset("MUIListNoDigit", eleMUI.MaterialDrawing, new_data, expireTime)

    if newList: # 如果存在新增则同时更新DB数据库
        conn_db.upsertBatchRow(newList)

    return MUIListIsDigit, MUIListNoDigit
