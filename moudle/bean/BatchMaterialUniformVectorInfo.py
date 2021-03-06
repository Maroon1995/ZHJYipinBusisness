# 导入定义类需要的模块
from sqlalchemy.ext.declarative import declarative_base  # 调用sqlalchemy的基类
from sqlalchemy import Column  # 指定字段属性，索引、唯一、DML
from sqlalchemy.types import *  # 所有字段类型
from common.Configuration import readConfig
# 创建库表类型
Base = declarative_base()  # 调用sqlalchemy的基类

class BatchMaterialUniform(Base):
    '''
    数据统一后的数据对象
    '''
    __tablename__ = readConfig()["tablename"]["BatchMaterialUniform"]  # 数据表的名字
    __table_args__ = {'extend_existing': True}  # 当数据库中已经有该表时，或内存中已声明该表，可以用此语句重新覆盖声明。
    oid = Column(Integer, primary_key=True)
    task_id = Column(String(255), unique=True)
    MaterialDrawing = Column(String(128), unique=True)  # 物料标准图号
    uniformitem = Column(String(255), unique=True) # 统一修正后的图号编码
    EnglishName = Column(String(255), unique=True)  # 标准英文名称
    Name = Column(String(255), unique=True)  # 标准中文名称
    Unit = Column(String(255), unique=True)  # 主英文计量单位
    vector = Column(String(255), unique=True) # 向量
    SROOID = Column(Integer,unique=True) # 物料唯一标识

    def keys(self):
        return ["task_id", "MaterialDrawing", "uniformitem", "Name", "EnglishName", "Unit", "vector","SROOID"]

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __init__(self, task_id, MaterialDrawing, uniformitem, EnglishName, Name, Unit, vector,SROOID):
        self.task_id = task_id
        self.MaterialDrawing = MaterialDrawing
        self.uniformitem = uniformitem
        self.EnglishName = EnglishName  # 声明需要调用的特征，可以只声明数据库中表格列的子集
        self.Name = Name
        self.Unit = Unit
        self.vector = vector
        self.SROOID = SROOID
