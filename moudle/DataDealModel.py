import sys

sys.path.append('../')
from util.LogUtil import MyLog
from common.ResumeTime import get_time
from common.DataCleaning import UniformMaterial
from bean.SpecialCharactersInfo import StrReplaceInfo
from contants.DataInitParams import *

mylog = MyLog()

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
        print("主数据向量化并存储成功！！！")
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
    mylog.info("------------进入了DataDealModel.run函数-----------")

    # TODO 3- 获取数据 Data.DataIn
    SRIList = pd_input.mysqlFileData(StrReplaceInfo)
    MIList = pd_input.mysqlFileData(tablename)
    # TODO 4- 数据初始化 DataCleaning
    try:
        # 清空 redis
        redisUtil.flushData("MUIListIsDigit")
        redisUtil.flushData("MUIListNoDigit")
        # 清空 mssql中的 material_uniform_vector数据
        db_session.execute("truncate table material_uniform_vector")
        # 重新初始化material_uniform_vector数据
        data_initialization(output=db_output,
                            sriList=SRIList,
                            startmp_threshold=startmp_threshold,
                            core_process=core_process,
                            MIList=MIList)

        mylog.info("数据初始化完成！！！")

    except Exception as e:
        mylog.error(f"数据初始化失败:{e}")


if __name__ == '__main__':
    run()
