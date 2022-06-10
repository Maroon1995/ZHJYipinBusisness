# 导入定义类需要的模块
from sqlalchemy.ext.declarative import declarative_base  # 调用sqlalchemy的基类
from sqlalchemy import Column  # 指定字段属性，索引、唯一、DML
from sqlalchemy.types import *  # 所有字段类型
from common.Configuration import readConfig
# 创建库表类型
Base = declarative_base()  # 调用sqlalchemy的基类

class BatchInfo(Base):
    '''
    需要进行唯一化的批量数据
    '''
    __tablename__ = readConfig()["tablename"]["BatchInfo"]  # 数据表的名字
    __table_args__ = {'extend_existing': True}
    oid = Column(Integer, primary_key=True)
    task_id = Column(String(255), unique=True)
    MaterialDrawing = Column(String(128), unique=True)  # 物料标准图号
    EnglishName = Column(String(255), unique=True)  # 标准英文名称
    Name = Column(String(255), unique=True)  # 标准中文名称
    Unit = Column(String(255), unique=True)  # 主英文计量单位

    def keys(self):
        return ["task_id", "MaterialDrawing", "Name", "EnglishName", "Unit"]

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __init__(self, task_id, MaterialDrawing, EnglishName, Name, Unit):
        self.task_id = task_id
        self.MaterialDrawing = MaterialDrawing
        self.EnglishName = EnglishName  # 声明需要调用的特征，可以只声明数据库中表格列的子集
        self.Name = Name
        self.Unit = Unit