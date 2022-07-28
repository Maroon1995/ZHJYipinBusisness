import json
import sys

sys.path.append('../')
from typing import List
from util.LogUtil import MyLog
from contants.DataInitParams import *
from common.ResumeTime import get_time
from common.CalculateSymbol import getNoSymbol
from common.DataCleaning import UniformMaterial
from bean.SpecialCharactersInfo import StrReplaceInfo
from bean.MainMaterialUniformVectorInfo import MaterialUniform
from sqlalchemy import and_

mylog = MyLog()


def _writeToRedis(redisUtil: RedisHelper, field, eleMUI):
    """
    # 添加数据到redis和newList中
    :param field: 字符串\图号\物料编码
    :param eleMUI: DB数据库中查询到的每条数据
    """
    new_data = json.dumps(dict(eleMUI))
    if field.isdigit():  # 分类出数值字符串和非数值字符串
        redisUtil.add_hset("MUIListIsDigit", eleMUI.MaterialDrawing, new_data)  # 添加到缓存哈希表“MUIListIsDigit”中
    else:
        redisUtil.add_hset("MUIListNoDigit", eleMUI.MaterialDrawing, new_data)


def data_initialization(output: DataOut, sriList, startmp_threshold, core_process: int, MIList):
    """
    数据初始化
    对ProductData数据进行初始化，将初始化结果输出到http请求所在的主机数据库中，
    对应的表为: "material_uniform_vector"
    :param output: 到任务主机上的数据库地址
    :param sriList: 字符映射列表
    :param startmp_threshold: 开启多进程的数据量界限
    :param core_process: 多进程的数量
    :param MIList: 被处理成初始化的数据列表
    :return: 1表示数据存入成功，0表示数据存入失败
    """

    # 统一**数据库中**数据（MaterialInfo）的物料编码
    MUIList = UniformMaterial(sriList, startmp_threshold, core_process).UniformMaterialCode(MIList)  # 无筛选条件
    # -----------------------------------------------------------------------------
    # 将字段item_id中多样元素统一后的结果输出到数据库中（MaterialUniform）
    try:
        output.sqlFileOut(MUIList)  # 直接输出到mysql数据库
        mylog.info("主数据向量化并存储成功！！")
        return 1
    except Exception as e:
        mylog.error("主数据向量化后存储失败！！ —— {}".format(e))
        return 0


@get_time
def run():
    """
    清洗主数据以及向量化
    :return: 返回1，表示数据处理成功，且已存入数据库
    """
    mylog.info("------------进入了DataSynUpdate.run函数-----------")
    # TODO 3- 数据更新与初始化 DataCleaning
    # 查询MaterialUniform表是否存在数据，如果不存在，重新初始化。若存在则更新MaterialUniform
    flag = db_session.mainKeyExists(MaterialUniform, 0)
    SRIList = pd_input.mysqlFileData(StrReplaceInfo)  # 字符映射
    if flag == 0:
        # 获取数据 Data.DataIn
        MIList = pd_input.mysqlFileData(tablename)
        data_initialization(output=db_output,
                            sriList=SRIList,
                            startmp_threshold=startmp_threshold,
                            core_process=core_process,
                            MIList=MIList)
        mylog.info("数据重新初始化成功！！！")
    else:  # 更新mssql和redis中的数据
        filterCondition_insert = MaterialInfo.Status > 2  # 状态：已停用-2、已变更-4、新增-3
        # 如果ProductData表中有数据变更、新增,即Status>2
        insertMIStatusList: List[MaterialInfo] = pd_input.mssqlFileData(MaterialInfo, filterCondition_insert)
        # 数据被删除停用了，status==2
        filterCondition_delete = MaterialInfo.Status == 2
        deleteMIStatusList: List[MaterialInfo] = pd_input.mssqlFileData(MaterialInfo, filterCondition_delete)
        if len(insertMIStatusList) > 0 and insertMIStatusList != None:  # 将数据处理后插入初始化表，存入mssql,redis
            # （1）将新增变更数据初始化到mssql
            # 统一**数据库中**数据（MaterialInfo）的物料编码
            MUIList = UniformMaterial(SRIList, startmp_threshold, core_process). \
                UniformMaterialCode(insertMIStatusList)
            # 将字段item_id中多样元素统一后的结果输出到数据库中（MaterialUniform）
            try:
                for elemMUI in MUIList:  # 删除MaterialDrawing,Code均相同的图号
                    db_session.delete(MaterialUniform,
                                      and_(MaterialUniform.MaterialDrawing == elemMUI.MaterialDrawing,
                                           MaterialUniform.Code == elemMUI.Code)
                                      )

                db_output.sqlFileOut(MUIList)  # 将查询到的3、4状态数据插入到初始化表中
                mylog.info("主数据-新增变更数据-向量化并存储成功！！")
            except Exception as e:
                mylog.error(f"主数据-新增变更数据-向量化后存储失败: {e}")
            # （2）将新增变更数据初始化到redis
            for eleMUI in MUIList:
                _writeToRedis(redisUtil, eleMUI.uniformitem, eleMUI)

        if len(deleteMIStatusList) > 0 and deleteMIStatusList != None:  # 将查询到的数据从mssql和redis中删除
            for elemDMI in deleteMIStatusList:
                # （1）删除mssql中的初始表数据
                condition = MaterialUniform.MaterialDrawing == elemDMI.MaterialDrawing
                db_session.delete(MaterialUniform, condition)
                # （2）删除redis中的初始表数据
                uniformitem = getNoSymbol(elemDMI, SRIList)
                if uniformitem.isdigit():
                    redisUtil.del_hset("MUIListIsDigit", elemDMI.MaterialDrawing)
                else:
                    redisUtil.del_hset("MUIListNoDigit", elemDMI.MaterialDrawing)

if __name__ == '__main__':
    run()
