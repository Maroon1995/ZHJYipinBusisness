from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import *
from common.Configuration import readConfig

# 创建库表类型
Base = declarative_base()


class MaterialResultInfo(Base):
    '''
    需要进行唯一化的批量数据
    '''
    __tablename__ = readConfig()["tablename"]["MaterialResultInfo"]  # 数据表的名字
    __table_args__ = {'extend_existing': True}
    ID = Column(Integer, primary_key=True)
    PDM_ID = Column(String(255), unique=True)
    ITEM_ID_NOSYMBOL = Column(String(255), unique=True)
    ITEM_ID = Column(String(128), unique=True)  # 物料标准图号
    ITEM_NAME_CH = Column(String(255), unique=True)  # 标准英文名称
    ITEM_NAME_EN = Column(String(255), unique=True)  # 标准中文名称
    ITEM_UNIT = Column(String(255), unique=True)  # 主英文计量单位
    PEOPLE_ONLYITEM = Column(String(255), unique=True)  # 物料唯一标识
    PEOPLE_NAME_CH = Column(String(255), unique=True)
    PEOPLE_NAME_EN = Column(String(255), unique=True)
    PEOPLE_UNIT = Column(String(255), unique=True)

    def keys(self):
        return ["PDM_ID", "ITEM_ID_NOSYMBOL", "ITEM_ID", "ITEM_NAME_CH", "ITEM_NAME_EN",
                "ITEM_UNIT", "PEOPLE_ONLYITEM", "PEOPLE_NAME_CH", "PEOPLE_NAME_EN", "PEOPLE_UNIT"]

    def __getitem__(self, item):
        return self.__getattribute__(item)

    def __init__(self, PDM_ID, ITEM_ID_NOSYMBOL, ITEM_ID, ITEM_NAME_CH, ITEM_NAME_EN,
                 ITEM_UNIT, PEOPLE_ONLYITEM, PEOPLE_NAME_CH, PEOPLE_NAME_EN, PEOPLE_UNIT):

        self.PDM_ID = PDM_ID
        self.ITEM_ID_NOSYMBOL = ITEM_ID_NOSYMBOL
        self.ITEM_ID = ITEM_ID
        self.ITEM_NAME_CH = ITEM_NAME_CH  # 声明需要调用的特征，可以只声明数据库中表格列的子集
        self.ITEM_NAME_EN = ITEM_NAME_EN
        self.ITEM_UNIT = ITEM_UNIT
        self.PEOPLE_ONLYITEM = PEOPLE_ONLYITEM
        self.PEOPLE_NAME_CH = PEOPLE_NAME_CH
        self.PEOPLE_NAME_EN = PEOPLE_NAME_EN
        self.PEOPLE_UNIT = PEOPLE_UNIT
