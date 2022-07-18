
from common.CollectFunc import mkList
from bean.MaterialBatchResultInfo import MateialBatchResult
from bean.BatchMaterialUniformVectorInfo import BatchMaterialUniform
from bean.MainMaterialUniformVectorInfo import MaterialUniform
from process.Similarity import similarityNp, cosinesimilarityNp
from util.LogUtil import MyLog

mylog = MyLog()


def similar(elemBUI: BatchMaterialUniform, elemMUI: MaterialUniform, similarthreshold: float):
    """
    计算两个物料的相似度
    :param elemBUI: 物料数据信息（BatchUniformInfo）
    :param elemMUI: 基础物料数据信息（MaterialUniformInfo）
    :param similarthreshold: 相似度阈值
    :return: 返回 MateialBatchResult 和 0
    """
    vecInt2 = mkList(elemBUI.vector)
    vecInt1 = mkList(elemMUI.vector)
    sim: float = 0.0
    if len(elemBUI.vector) == 15 and len(elemBUI.vector) == len(elemMUI.vector):
        sim = similarityNp(vecInt1=vecInt1, vecInt2=vecInt2)  # 平均相似度
    else:
        sim = cosinesimilarityNp(vecInt2, vecInt1)  # 余弦相似度

    if sim >= similarthreshold:
        return MateialBatchResult(elemBUI.task_id, elemBUI.MaterialDrawing, elemMUI.MaterialDrawing, elemMUI.oid,
                                  sim, elemMUI.Name, elemMUI.EnglishName,
                                  elemMUI.Unit, elemMUI.Code, elemMUI.FirstClass, 1, elemBUI.SROOID)
    else:
        return 0
