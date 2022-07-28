# 导入定义类需要的模块
from sqlalchemy.ext.declarative import declarative_base  # 调用sqlalchemy的基类
from sqlalchemy import Column  # 指定字段属性，索引、唯一、DML
from sqlalchemy.types import *  # 所有字段类型
from common.Configuration import readConfig
# 创建库表类型
Base = declarative_base()  # 调用sqlalchemy的基类

class MaterialInfo(Base):
    '''
    继承基类
    '''
    __tablename__ = readConfig()["tablename"]["MaterialInfo"]  # 数据表的名字
    __table_args__ = {'extend_existing': True}  # 当数据库中已经有该表时，或内存中已声明该表，可以用此语句重新覆盖声明。
    id = Column(Integer, primary_key=True)
    oid = Column(Integer, unique=True)
    Code = Column(String(255), unique=True) # 物料编码
    MaterialDrawing = Column(String(128), unique=True) # 物料标准图号
    EnglishName = Column(String(255), unique=True) # 标准英文名称
    Name = Column(String(255), unique=True) # 标准中文名称
    Unit = Column(String(255), unique=True) #  主英文计量单位
    FirstClass = Column(String(255), unique=True) # 一级分类
    Status = Column(Integer,unique=True)
    def keys(self):
        return ["oid","Code", "MaterialDrawing", "Name", "EnglishName", "Unit", "FirstClass","Status"]

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __init__(self, oid, Code, MaterialDrawing, EnglishName, Name, Unit, FirstClass,Status):
        self.oid = oid
        self.Code = Code
        self.MaterialDrawing = MaterialDrawing
        self.EnglishName = EnglishName  # 声明需要调用的特征，可以只声明数据库中表格列的子集
        self.Name = Name
        self.Unit = Unit
        self.FirstClass = FirstClass
        self.Status = Status
