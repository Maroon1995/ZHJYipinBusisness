
import os
from common.DataInOut import DataOut
from common.CalculateSimlary import similar
from util.LogUtil import MyLog
from multiprocessing import Pool
from typing import List
from bean.BatchMaterialUniformVectorInfo import BatchMaterialUniform
from bean.MaterialBatchResultInfo import MateialBatchResult
from bean.MainMaterialUniformVectorInfo import MaterialUniform

mylog = MyLog()

def BatchSimilarCalculate(BUIL: BatchMaterialUniform, MUIList: List, similarthreshold: float):
    """
    计算相似度，存储结果
    :param BUIList: 批量上传处理后数据
    :param MUIList: 主数据处理后的数据
    :param similarthreshold: 相似度阈值
    :return:
    """
    # print('<进程%s> get  %s' % (os.getpid(), BUIL.MaterialDrawing))
    # map(lambda x:similar(elemBUI,x), MUIList)
    resList: List = [similar(BUIL, MUIList[j], similarthreshold) for j in range(len(MUIList))]
    result = list(set(resList))
    result.remove(0)
    if len(result) == 0:  # 如果在相似度阈值内没有找到相似物料，则相似度用1.01表示只有自己,主数据中没有找到相似物料，最后一级分类和匹配状态分别显示为"NoClass",0；否则，将找到相似或相同物料输出到结果当中。
        result.append(MateialBatchResult(BUIL.task_id,BUIL.MaterialDrawing,BUIL.MaterialDrawing,None,1.01,
                                         BUIL.Name,BUIL.EnglishName,BUIL.Unit,None,None,0,BUIL.SROOID))
    return result


def OutDB(result, output: DataOut):
    """
    结果输出
    :param result: 可以是列表也可以是单个元素
    :param output: 数据输出的实例对象
    :param mainkeyCondition: 字段过滤条件，在输入数据时，哪些字段条件满足时，不需要插入满足条件的数据
    :return:返回结果为1表示输出成功，否则输出失败
    """
    # print('<进程%s> parse %s' % (os.getpid(), result[0].MaterialDrawing))
    try:
        output.sqlFileOut(result)
        return 1
    except Exception as e:
        mylog.error("Consumer.OutDB(): 计算结果数据存储失败 —— {}".format(e))
        return 0


def getResult(output: DataOut, BUILists: List[BatchMaterialUniform], MUILists: List[MaterialUniform], similarthreshold,
              core_process,startmp_threshold):
    """
    获取计算相似度后的结果，并存入DB数据库中的结果表中
    :param BUILists:
    :param MUILists:
    :param similarthreshold: 相似度阈值
    :param core_process: 计算多进程数量
    :return:
    """
    if len(BUILists)>startmp_threshold: # 如果满足条件，则进行多进程计算。
        print("进行多进程计算。。。！")

        p1 = Pool(core_process)
        res_liss = []
        # 相似度计算
        for elemBUI in BUILists:
            # res = p1.apply_async(__BatchSimilarCalculate,args=(elemBUI,MUIListIsDigit,similarthreshold,),callback=OutDB) # 回调函数
            res = p1.apply_async(BatchSimilarCalculate, args=(elemBUI, MUILists, similarthreshold,))
            res_liss.append(res)
        p1.close()
        p1.join()

        # ------------------------------------------------------------------------------------------------
        # 结果输出
        try:
            res_out = []
            if len(res_liss) > 0:  # 如果不为空者继续执行
                p2 = Pool(core_process)
                for elemRes in res_liss:
                    res = p2.apply_async(OutDB, args=(elemRes.get(), output,))
                    res_out.append(res.get())
                p2.close()
                p2.join()
            else:
                raise Exception("方法BatchSimilarCalculates的计算结果res_liss为空")

            res_out_set = list(set(res_out))  # 判断存储数据过程中是否存在由于存储失败造成的数据丢失
            if len(res_out_set) == 2:
                raise Exception("数据在存储过程中存在丢失，需要重新生成新的订单，然后提交计算！")
            elif res_out_set[0] == 1 and len(res_out_set) == 1:

                mylog.info("===" * 5 + "Sucessfully!" + "===" * 5)
            else:
                raise Exception("===" * 5 + "Failed!" + "===" * 5)

        except Exception as e:
            mylog.error("原因1：BatchSimilarCalculates计算结果res_liss为空；原因2：OutDB数据输出错误 {}".format(e))

    else:

        try:
            res_out = []
            # 相似度计算
            for elemBUI in BUILists:
                res = BatchSimilarCalculate(elemBUI, MUILists, similarthreshold)
                res_flag = OutDB(res,output)
                res_out.append(res_flag)
            res_out_set = list(set(res_out))  # 判断存储数据过程中是否存在由于存储失败造成的数据丢失
            if len(res_out_set) == 2:
                raise Exception("数据在存储过程中存在丢失，需要重新生成新的订单，然后提交计算！")
            elif res_out_set[0] == 1 and len(res_out_set) == 1:

                print("===" * 5 + "Sucessfully!" + "===" * 5)
                mylog.info("===" * 5 + "Sucessfully!" + "===" * 5)
            else:
                raise Exception("===" * 5 + "Failed!" + "===" * 5)

        except Exception as e:
            mylog.error("原因1：BatchSimilarCalculates计算结果res_liss为空；原因2：OutDB数据输出错误 {}".format(e))