import sys

sys.path.append('../')
from util.LogUtil import MyLog
from common.ResumeTime import get_time
from common.Configuration import readConfig
from common.DataInOut import DataIn, DataOut
from common.DataCleaning import UniformMaterial
from bean.MainMaterialInfo import MaterialInfo
from bean.SpecialCharactersInfo import StrReplaceInfo

@get_time
def run():
    """
    清洗主数据以及向量化
    :return: 返回1，表示数据处理成功，且已存入数据库
    """
    mylog = MyLog()
    mylog.info("------------进入了DataDealModel.run函数-----------")
    # TODO 0- 配置文件
    cfg = readConfig()
    base_config = cfg["basevariable"]
    mssql_config = cfg["database"]["mssql"]

    # TODO 1- 参数设置
    startmp_threshold = base_config["startmp_threshold"]
    core_process =  base_config["core_process"]
    # db_path = cfg["database"]["mysql"]["url"]
    db_path = mssql_config["url"]
    tablename = MaterialInfo
    # -----------------------------------------------------------------------------
    # TODO 2- 实例化对象
    input = DataIn(db_path)     # 输入
    output = DataOut(db_path)   # 输出

    # TODO 3- 获取数据 Data.DataIn
    SRIList = input.mysqlFileData(StrReplaceInfo)
    MIList = input.mysqlFileData(tablename)
    # TODO 4- 数据清洗 DataCleaning
    # 统一**数据库中**数据（MaterialInfo）的物料编码
    MUIList = UniformMaterial(sriList=SRIList,startmp_threshold=startmp_threshold,core_process=core_process).UniformMaterialCode(MIList)  # 无筛选条件
    # -----------------------------------------------------------------------------
    # TODO 5- 数据输出 DataOut
    # 将字段item_id中多样元素统一后的结果输出到数据库中（MaterialUniform）
    try:
        output.sqlFileOut(MUIList)  # 直接输出到mysql数据库
        print("主数据向量化并存储成功！！！")
        mylog.info("主数据向量化并存储成功！！")
        return 1
    except Exception as e:
        mylog.error("主数据向量化后存储失败！！ —— {}".format(e))
        return 0

if __name__ == '__main__':

    run()
