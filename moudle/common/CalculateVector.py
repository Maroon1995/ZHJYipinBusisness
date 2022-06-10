
from collections import Counter
from common.CollectFunc import getOrElse, mkString


def getVectorString(strings: str):
    """
    将字符串转换成向量字符串：'ZYXWVUTSR0090' -> '02324301233'
    :param strings: 字符串必须是只含有字母或数字的
    :return: 返回一个向量字符串:最终目的是方便在数据库中存储
    """
    vectorstr: str

    if strings.isdigit() and len(strings) < 10:  # 如果字符串为数值字符串,并且长度小于10（目的是将Z923124124545和23124124545放在一起），则直接构造一个长度为15的数值字符串
        vectorstr = strings + "0" * (15 - len(strings))

    else:

        template = list("ZYXWVUTSRQPONMLKJIHGFEDCBA9876543210")  # 向量模板
        elemcounts = dict(Counter(list(strings)))  # 字符串元素个数计数，生成字典。
        vectorstr = mkString(list(map(lambda x: getOrElse(x, elemcounts, 0), template)))  # 生成向量

    return vectorstr
