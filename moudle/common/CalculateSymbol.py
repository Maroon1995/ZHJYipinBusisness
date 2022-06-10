
import sys

sys.path.append('../')
from typing import List
from bean.SpecialCharactersInfo import  StrReplaceInfo
from process.Function import HandleItem


def Replace(coding: str, elemList: List[StrReplaceInfo]):
    """
    替换字符串中的多样元素，做到统一coding
    :param coding: 被统一的字符串
    :param elemList: List[StrReplaceInfo]
    :return:
    """
    newcoding: str = coding.upper()  # 初始化,将字符串中的小写转换为大写
    for elem in elemList:
        if elem.Code in newcoding:
            newcoding = newcoding.replace(elem.Code, elem.Name)

    return newcoding

def getNoSymbol(byUniformDataInfo, elemList: List[StrReplaceInfo]):
    """
    处理单条字符串中多样性元素
    :param byUniformDataInfo: 是一个被统一的DataInfo实例对象
    :param elemList: 用于需要统一的元素对象
    :return: 返回单条处理后的字符串
    """
    HI = HandleItem
    # TODO 1- 元素多样
    newstr = Replace(byUniformDataInfo.MaterialDrawing, elemList)
    # TODO 2- 处理首行缺零字符的编码-'0247773','247773'
    newstr2 = HI(newstr).FirstCharZeros()
    # TODO 3- 转换罗马数字
    newstr3 = HI(newstr2).romanNumberTransform()
    # TODO 4- 去除多0的字符串
    newstr4 = HI(newstr3).multizero()
    # TODO 5- 转换小数 20.34 -> 20DIAN34
    newstr5 = HI(newstr4).floattransform()
    # TODO 6- 去除符号
    newstr6 = HI(newstr5).deletesymbol()

    return newstr6