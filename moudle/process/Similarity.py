import numpy as np
from numpy import dot
from numpy.linalg import norm
from typing import List

def cosinesimilarityNp(vecInt1: List[int], vecInt2: List[int]):
    """
    计算两个向量的余弦相似度
    :param vecInt1: 向量1
    :param vecInt2: 向量2
    :return: 返回相似度
    """
    res: float = 0.0
    if len(vecInt1) > 0 and len(vecInt1) == len(vecInt2):
        res = round(dot(vecInt1, vecInt2) / (norm(vecInt1) * norm(vecInt2)), 3)  # 计算相似度，并保留3位小数

    return res

def jaccardsimilarityNp(x, y):
    """
    计算Jaccard相似系数
    :param x: Array[]
    :param y: Array[]
    :return:
    """
    union = np.union1d(x, y)
    inter = np.intersect1d(x, y)
    return union, inter


def similarityNp(vecInt1: List[int], vecInt2: List[int]):
    """
    计算相似度
    :param vecInt1: 被对比对象向量
    :param vecInt2: 对比对象向量
    :return:
    """
    x = np.array(vecInt1)
    y = np.array(vecInt2)
    # dis = 1 / (1 + np.sqrt(np.sum((x - y) ^ 2)))  # 欧几里得
    cor = np.abs(np.corrcoef(x, y)[0][1])  # 皮尔逊相关系数
    cos = cosinesimilarityNp(list(x), list(y))  # 余弦相似度
    union, inter = jaccardsimilarityNp(x, y)
    jaccard = len(inter) / len(union)  # Jaccard相似系数

    return round((cor * 0.5 + cos * 1 + jaccard * 8.5) / 10, 3)
