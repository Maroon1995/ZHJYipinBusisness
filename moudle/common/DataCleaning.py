
import json
from typing import List, Dict
from common.DataInOut import DataIn, DataOut
from process.Uniform import StrUniform, multProcessUniform
from util.LogUtil import MyLog
from bean.BatchMaterialInfo import BatchInfo
from bean.MainMaterialInfo import MaterialInfo
from bean.MaterialBatchResultInfo import MateialBatchResult
from bean.SpecialCharactersInfo import StrReplaceInfo


class UniformMaterial(object):
    """
    统一字符串，计算向量
    """
    filterCondition = 0
    limitnum = None
    input: DataIn
    output: DataOut
    mylog = MyLog()

    def __init__(self, sriList: List[StrReplaceInfo], startmp_threshold: int = 100,
                 core_process: int = 6):

        self.sriList = sriList  # List[StrReplaceInfo]
        self.startmp_threshold = startmp_threshold  # 开启多进程计算的阈值,默认为100
        self.core_process = core_process  # 开启进程的核心数，默认为6

    def _splitData(self, MIList: List):
        """
        将获取到的数切分成主数据中已经存在的和主数据中不存在的
        目的：存在的直接返回主数据中的数据，不存在的计算相似的推荐。
        :param MIList:
        :param caculate_simlar_milist : 存储用于计算相似字符串推荐的BatchInfo
        :param query_milist: 在主数据中查询到的数据从新封装成MateialBatchResult，并返回到该列表中
        :return:
        """
        caculate_simlar_milist = []  # 用于计算相似字符串推荐
        query_milist = []  # 在主数据中查询到的数据
        count = len(MIList)
        for i in range(count):
            elemMI: BatchInfo = MIList[i]
            # 在主数据中查询当前数据是否存在，如果存在返回查询到的数据，并封装成MateialBatchResult返回。
            queryRes: List[MaterialInfo] = self.input.mysqlFileData(MaterialInfo,
                                                                    filterCondition=MaterialInfo.MaterialDrawing == elemMI.MaterialDrawing)
            if len(queryRes) > 0:
                for eleQR in queryRes:
                    mbr = MateialBatchResult(elemMI.task_id,elemMI.MaterialDrawing, eleQR.MaterialDrawing, eleQR.oid,
                                             1, eleQR.Name, eleQR.EnglishName, eleQR.Unit, eleQR.Code, eleQR.FirstClass, 1,elemMI.SROOID)
                    query_milist.append(mbr)

            else:
                caculate_simlar_milist.append(elemMI)

        if len(query_milist) > 0:  # 如果主数据中存在，则将重新封装的MateialBatchResult数据直接存储到DB中
            self.output.sqlFileOut(query_milist)  # 直接输出到数据库的结果表中

        return caculate_simlar_milist, query_milist

    def _parseJsonString(self, jsonString: str):
        """
        解析json字符串str(Dict(key,List[Dict]))
        :param jsonString: json字符串
        :return: 返回值，一个列表集合List[Dict]
        """
        jsonDict: Dict = json.loads(jsonString)

        return list(jsonDict.values())[0]

    def _packageBatchInfo(self, dicts: Dict, task_id: str):
        """
        将字典封装成BatchInfo
        :param task_id: 当前任务id
        :param dicts: 要重新封装的字典
        :return: 返回一个BatchInfo实例
        """
        return BatchInfo(task_id, dicts.get("SROOID") ,dicts.get("MaterialDrawing"), dicts.get("EnglishName"), dicts.get("Name"),
                         dicts.get("Unit"))

    def UniformMaterialCode(self, MIList: List):
        """
        统一字符串，并计算向量
        :param MIList:
        :param startmp_threshold: 开启多进程计算的阈值,默认为100
        :param core_process: 开启进程的核心数
        :return:
        """
        if (len(MIList) >= self.startmp_threshold):  # 多进程执行
            self.mylog.info("统一字符串计算，数量超过: {}，开启多进程执行......".format(self.startmp_threshold))
            MUIList = multProcessUniform(self.core_process, MIList, self.sriList)
        else:
            self.mylog.info("统一字符串计算，数量未超过: {}，开启单进程执行......".format(self.startmp_threshold))
            MUIList = list(map(lambda el: StrUniform(el, self.sriList), MIList))  # 物料编码字符串处理函数: StrUniform

        return MUIList

    def UniformMaterialCodeHttp(self, jsonString: str, task_id: str):
        """
        将数据中多样性的元素进行统一
        :param jsonString: 请求到的json数据
        :param task_id: 本次请求的任务id
        :return: 返回一个统一后的新对象 MaterialUniformInfo
        """
        # 统一字符串：获取http请求到的数据
        values: List[Dict] = self._parseJsonString(jsonString)  # 解析数据
        MIList = list(map(lambda x: self._packageBatchInfo(x, task_id=task_id), values))  # 重新封装数据
        # 对获取到的数据进行分割：主数据存在与主数据不存在
        if len(MIList) > 0:
            caculate_simlar_milist, query_milist = self._splitData(MIList)
            # 统一字符串：替换多样元素
            MUIList = self.UniformMaterialCode(caculate_simlar_milist)
            return MUIList, query_milist
        else:
            raise Exception("http请求到的输入数据集合为空，请重新获取！！！")

    def UniformMaterialCodeDatabase(self, byUniformDataInfo):

        """
        数据库、将数据中多样性的元素进行统一
        :param byUniformDataInfo: 要被统一的BatchInfo
        :param path: 数据库路径
        :return: 返回一个统一后的列表实例化对象:例如 List[MaterialUniform]
        """
        # 统一字符串：获取数据
        MIList = self.input.mysqlFileData(byUniformDataInfo, self.filterCondition, self.limitnum)
        # 对获取到的数据进行分割：主数据存在与主数据不存在
        if len(MIList) > 0:
            caculate_simlar_milist, query_milist = self._splitData(MIList)
            # 统一字符串：替换多样元素
            MUIList = self.UniformMaterialCode(caculate_simlar_milist)
            return MUIList, query_milist
        else:
            raise Exception("从DB数据库中获取的输入数据集合为空，请重新获取！！！")

    def UniformMaterialCodeLocalbase(self, local_path: str, byUniformDataInfo):

        """
        本地数据csv、将数据中多样性的元素进行统一
        :param byUniformDataInfo: 要被统一的BatchInfo
        :param localpath: 本地文件路径
        :return: 返回一个统一后的列表实例化对象:例如 List[MaterialUniform]
        """
        # 统一字符串：获取数据
        MIList = self.input.localFileData(local_path, tablename=byUniformDataInfo)
        if len(MIList) > 0:
            if self.limitnum != None:
                import random
                MIList = random.sample(MIList, self.limitnum)  # 限制输出，随机抽取limitnum个数值

            caculate_simlar_milist, query_milist = self._splitData(MIList)
            # 统一字符串：替换多样元素
            MUIList = self.UniformMaterialCode(caculate_simlar_milist)
            return MUIList, query_milist
        else:
            raise Exception("从local获取的输入数据集合为空，请重新获取！！！")
