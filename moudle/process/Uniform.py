
from typing import List
from multiprocessing import Pool
from common.CalculateVector import getVectorString
from common.CalculateSymbol import getNoSymbol
from bean.BatchMaterialInfo import BatchInfo
from bean.MainMaterialInfo import MaterialInfo
from bean.BatchMaterialUniformVectorInfo import BatchMaterialUniform
from bean.MainMaterialUniformVectorInfo import MaterialUniform
from bean.SpecialCharactersInfo import StrReplaceInfo


def StrUniform(byUniformDataInfo, elemList: List[StrReplaceInfo]):
    """
    单进程统一字符串编码和向量化
    :param byUniformDataInfo: 是一个被统一的DataInfo实例对象
    :param elemList: 用于需要统一的元素对象
    :param UniformDataInfo: 结果输出封装对象
    :return: 返回统一后的数据对象
    """
    # print('<进程%s> StrUniform get  %s' % (os.getpid(), byUniformDataInfo.item_id))
    # TODO 1- 计算统一码
    newstr6 = getNoSymbol(byUniformDataInfo, elemList)
    # TODO 2- 计算向量 CalculateVector.getVectorString
    newstr7 = getVectorString(newstr6)
    # TODO 3- 封装成实例对象 MaterialUniformInfo
    # 加一个byUniformDataInfo的类型判断
    if isinstance(byUniformDataInfo, BatchInfo)==True:
        return BatchMaterialUniform(byUniformDataInfo.task_id,byUniformDataInfo.MaterialDrawing,newstr6,
                             byUniformDataInfo.EnglishName,byUniformDataInfo.Name,byUniformDataInfo.Unit,newstr7,byUniformDataInfo.SROOID)

    elif isinstance(byUniformDataInfo, MaterialInfo)==True:
        return MaterialUniform(byUniformDataInfo.oid,byUniformDataInfo.Code,byUniformDataInfo.MaterialDrawing,newstr6,
                        byUniformDataInfo.EnglishName,byUniformDataInfo.Name,byUniformDataInfo.Unit,byUniformDataInfo.FirstClass,
                        newstr7,0)# 状态为0表示已有主数据

    else:
        raise Exception("在StrUniform方法中，期待传入参数byUniformDataInfo的类型为BatchInfo或MaterialInfo")

def multProcessUniform(core_process,MIList,sriList):
    """
    多进程统一字符串编码和向量化
    :param core_process:
    :param MIList:
    :param sriList:
    :return:
    """
    p = Pool(core_process)
    MUIListR = []
    for elemBUI in MIList:
        res = p.apply_async(StrUniform, args=(elemBUI, sriList,))
        MUIListR.append(res)
    p.close()
    p.join()  # 等待进程池中所有进程执行完毕

    MUIList = []
    for ele in MUIListR:
        MUIList.append(ele.get())

    return MUIList