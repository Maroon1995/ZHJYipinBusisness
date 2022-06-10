import sys

sys.path.append('../')
from typing import List
from common.DataCleaning import UniformMaterial
from common.DataInOut import DataIn, DataOut
from bean.BatchMaterialInfo import BatchInfo
from bean.SpecialCharactersInfo import StrReplaceInfo


def getDatafromDB(input: DataIn, tabelname: BatchInfo, SRIList: List[StrReplaceInfo],
                  filterCondition=0,
                  limitnum: int = None,
                  startmp_threshold=100, core_process=6):
    """
    获取DB数据库数据
     :param input: 数据输入实例对象
     :param tablename: 批量数据的表名称 BatchInfo
     :param filterCondition: 筛选批量数据条件
     :param similarthreshold: 相似度阈值
     :param limitnum: 限制输出条数
     :param startmp_threshold: 开启多进程计算的阈值,默认为100
     :param core_process: 开启进程的核心数
     :return:
     """
    um = UniformMaterial(SRIList, startmp_threshold, core_process)  # 实例化
    um.input = input  # 输入数据实例化对象DataIn(path)
    um.filterCondition = filterCondition  # set筛选条件，一般是用不到的。
    um.limitnum = limitnum  # set限制条件，一般测试时用

    try:
        BUIList, query_milist = um.UniformMaterialCodeDatabase(byUniformDataInfo=tabelname)
        BUIListIsDigit = list(filter(lambda x: x.uniformitem.isdigit() == True, BUIList))  # 过滤出数值字符串图号
        BUIListNoDigit = list(filter(lambda x: x.uniformitem.isdigit() == False, BUIList))  # 过滤出非数值字符串图号
        return BUIListIsDigit, BUIListNoDigit, query_milist

    except Exception as e:
        print("getDatafromDB 获取数据失败,原因: {}".format(e))


def getDatafromHTTP(input: DataIn, output: DataOut, task_id: str, task_data: str, SRIList: List[StrReplaceInfo],
                    startmp_threshold=100, core_process=6):
    """
    获取HTTP请求来的数据
     :param input 数据输入实例对象
     :param output 数据输出实例对象
     :param task_id: 任务id
     :param task_data: 接收到的任务数据
     :param similarthreshold 相似度阈值
     :param limitnum: 限制输出条数
     :param startmp_threshold: 开启多进程计算的阈值,默认为100
     :param core_process: 开启进程的核心数
     :return:
     """
    um = UniformMaterial(SRIList, startmp_threshold, core_process)  # 实例化
    um.input = input  # 输入数据实例化对象DataIn(path)
    um.output = output  # 输出数据实例化对象DataOut(path)

    try:
        BUIList, query_milist = um.UniformMaterialCodeHttp(task_id=task_id, jsonString=task_data)
        BUIListIsDigit = list(filter(lambda x: x.uniformitem.isdigit() == True, BUIList))  # 过滤出数值字符串图号
        BUIListNoDigit = list(filter(lambda x: x.uniformitem.isdigit() == False, BUIList))  # 过滤出非数值字符串图号
        return BUIListIsDigit, BUIListNoDigit, query_milist

    except Exception as e:
        print("getDatafromHTTP 获取数据失败,原因: {}".format(e))


def getDatafromLocal(input: DataIn,local_path ,tabelname: BatchInfo, SRIList: List[StrReplaceInfo], startmp_threshold,
                     core_process, limitnum):
    """
    获取本地csv数据
     :param input: 数据输入实例对象
     :param local_path: 本地文件数据路径
     :param tablename: 批量数据的表名称 BatchInfo
     :param similarthreshold: 相似度阈值
     :param limitnum: 限制输出条数
     :param startmp_threshold: 开启多进程计算的阈值,默认为100
     :param core_process: 开启进程的核心数
     :return:
     """
    um = UniformMaterial(SRIList, startmp_threshold, core_process)  # 实例化
    um.input = input  # 输入数据实例化对象DataIn(path)
    um.limitnum = limitnum  # set限制条件，一般测试时用

    try:
        BUIList, query_milist = um.UniformMaterialCodeLocalbase(local_path,byUniformDataInfo=tabelname)
        BUIListIsDigit = list(filter(lambda x: x.uniformitem.isdigit() == True, BUIList))  # 过滤出数值字符串图号
        BUIListNoDigit = list(filter(lambda x: x.uniformitem.isdigit() == False, BUIList))  # 过滤出非数值字符串图号
        return BUIListIsDigit, BUIListNoDigit, query_milist

    except Exception as e:
        print("getDatafromLocal 获取数据失败,原因: {}".format(e))
