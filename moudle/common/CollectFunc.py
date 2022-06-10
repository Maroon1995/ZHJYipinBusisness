from typing import List,Dict


def getOrElse(key, elemDict: Dict, notIn: int = 0):
    """
    判断列表元素是否为另外一个字典集合(elemDict)的key，如果是，则返回字典集合key对应的元素，否则返回notIn
    :param key:
    :param elemDict:
    :param notIn:
    :return:
    """
    keyList = sorted(elemDict.keys(), reverse=True)
    if keyList:
        if key in keyList:
            return elemDict.get(key)
        else:
            return notIn
    else:
        raise Exception("在对字符串重新编码时，输入方法getOrElse中的字符串keys为空，即字符串不存在")


def mkString(elemList: List):
    """
    将列表中的元素拼接成一个字符串
    :param elemList: 列表 [1,2,3,1] -> '1231'
    :return: 返回字符串
    """
    strings = ""
    if elemList:
        for el in elemList:
            strings = strings + str(el)
        return strings
    else:
        raise Exception("输入方法mkString中的参数elemList为空！！！")


def mkList(strings :str):
    """
    作用在整数字符串，目的： '1231' -> [1,2,3,1]
    :param strings:
    :return:
    """
    return list(map(lambda x :int(x) ,list(strings)))