# 导入定义类需要的模块
from sqlalchemy.ext.declarative import declarative_base  # 调用sqlalchemy的基类
from sqlalchemy import Column  # 指定字段属性，索引、唯一、DML
from sqlalchemy.types import *  # 所有字段类型
from common.Configuration import readConfig
# 创建库表类型
Base = declarative_base()  # 调用sqlalchemy的基类


class StrReplaceInfo(Base):
    """
    需要替换的字符集
    """
    __tablename__ = readConfig()["tablename"]["StrReplaceInfo"]  # 数据表的名字
    __table_args__ = {'extend_existing': True}  # 当数据库中已经有该表时，或内存中已声明该表，可以用此语句重新覆盖声明。
    oid = Column(Integer, primary_key=True)
    Code = Column(String(255), unique=True) # 特殊字符
    Name = Column(String(255), unique=True) # 替换字符

    def keys(self):
        return ["Code", "Name"]

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __init__(self, Code, Name):
        self.Code = Code
        self.Name = Name