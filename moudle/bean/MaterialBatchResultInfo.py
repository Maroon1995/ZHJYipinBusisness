# 导入定义类需要的模块
from sqlalchemy.ext.declarative import declarative_base  # 调用sqlalchemy的基类
from sqlalchemy import Column  # 指定字段属性，索引、唯一、DML
from sqlalchemy.types import *  # 所有字段类型
from common.Configuration import readConfig
# 创建库表类型
Base = declarative_base()  # 调用sqlalchemy的基类


class MateialBatchResult(Base):
    '''
     需要进行唯一化的批量数据进行统一后的数据对象
    '''
    __tablename__ = readConfig()["tablename"]["MateialBatchResult"]  # 数据表的名字
    __table_args__ = {'extend_existing': True}  # 当数据库中已经有该表时，或内存中已声明该表，可以用此语句重新覆盖声明。
    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), unique=True)
    uniformitem = Column(String(128), unique=True)
    MaterialDrawing = Column(String(128), unique=True)
    oid = Column(Integer, unique=True)
    similar = Column(Float(10), unique=True)
    Name = Column(String(255), unique=True)
    EnglishName = Column(String(255), unique=True)
    Unit = Column(String(255), unique=True)
    Code = Column(String(255), unique=True)  # 物料编码
    FirstClass = Column(String(255), unique=True)  # 一级分类
    MatchLogo = Column(Integer, unique=True) # 0表示主数据中未匹配到，计算了相似物料；1表示主数据中匹配到

    def keys(self):
        return ["task_id", "uniformitem", "MaterialDrawing", "oid","similar", "Name", "EnglishName", "Unit", "Code","FirstClass",
                "MatchLogo"]

    def __getitem__(self, item):
        return self.__getattribute__(item)


    def __init__(self, task_id, uniformitem, MaterialDrawing, oid,similar, Name, EnglishName, Unit,Code,FirstClass,
                 MatchLogo):
        self.task_id = task_id
        self.uniformitem = uniformitem
        self.MaterialDrawing = MaterialDrawing  # 声明需要调用的特征，可以只声明数据库中表格列的子集
        self.oid = oid
        self.similar = similar
        self.Name = Name
        self.EnglishName = EnglishName
        self.Unit = Unit
        self.Code = Code
        self.FirstClass = FirstClass
        self.MatchLogo = MatchLogo