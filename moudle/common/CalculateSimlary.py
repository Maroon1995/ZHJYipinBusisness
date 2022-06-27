
from numpy import dot
from numpy.linalg import norm
from typing import List
from common.CollectFunc import mkList
from bean.MaterialBatchResultInfo import MateialBatchResult
from bean.BatchMaterialUniformVectorInfo import BatchMaterialUniform
from bean.MainMaterialUniformVectorInfo import MaterialUniform
from util.LogUtil import MyLog

mylog = MyLog()

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


def similar(elemBUI: BatchMaterialUniform, elemMUI: MaterialUniform, similarthreshold: float):
    """
    计算两个物料的相似度
    :param elemBUI: 物料数据信息（BatchUniformInfo）
    :param elemMUI: 基础物料数据信息（MaterialUniformInfo）
    :param similarthreshold: 相似度阈值
    :return: 返回 MateialBatchResult 和 0
    """
    vecInt1 = mkList(elemBUI.vector)
    vecInt2 = mkList(elemMUI.vector)

    sim = cosinesimilarityNp(vecInt1, vecInt2)

    if sim >= similarthreshold:
        return MateialBatchResult(elemBUI.task_id, elemBUI.MaterialDrawing, elemMUI.MaterialDrawing, elemMUI.oid,
                                  sim, elemMUI.Name, elemMUI.EnglishName,
                                  elemMUI.Unit, elemMUI.Code, elemMUI.FirstClass, 1,elemBUI.SROOID)
    else:
        return 0
