import sys

sys.path.append('../')
from typing import List
from util.LogUtil import MyLog
from sqlalchemy import create_engine  # 引擎
from sqlalchemy.orm import sessionmaker  # 创建orm的会话池，orm和sql均可以管理对象关系型数据库，需要绑定引擎才可以使用会话，
from bean.BatchMaterialInfo import BatchInfo


class SQLUtil(object):
    mylog = MyLog()

    # 初始化方法
    def __init__(self, host='localhost', databasetype='mysql+pymysql', database='default', user='root',
                 password='123456',
                 port: int = 3306,
                 path=None):
        """

        :param host:
        :param databasetype: 数据库类型：mysql+pymysql、mssql+pymssql等
        :param database:
        :param user:
        :param password:
        :param port:
        :param path:
        """
        self.host = host
        self.databasetype = databasetype
        self.database = database
        self.user = user
        self.password = password
        # self.charset = charset
        self.path = path
        self.port = port
        self.engine = None
        self.session = None

    def open(self):
        """
        初始化完后连接到数据库并创建好会话
        创建连接,需要安装mysql和pymysql的模块，用户名:密码@ip地址/某个数据库
        """
        if self.path == None:
            self.path = "{}://{}:{}@{}:{}/{}".format(self.databasetype, self.user, self.password, self.host,
                                                     self.port, self.database)
        self.engine = create_engine(
            self.path,
            # echo=True,          # 打印操作对应的SQL语句
            pool_size=8,  # 连接个数
            pool_recycle=60 * 30,  # 不使用时断开
            encoding='utf-8',
            convert_unicode=True
        )

        # 创建session
        DbSession = sessionmaker(bind=self.engine)  # 会话工厂，与引擎绑定。
        self.session = DbSession()  # 实例化

    def close(self):
        """
        关闭资源
        """
        self.session.close()  # 关闭会话

    def mainKeyExists(self, dataInfo, mainkeyCondition):
        """
        判断表数据中主键数据是否存在
        :param dataInfo: 要查询的表数据对象
        :param mainkeyCondition: 对字段进行过滤筛选的条件
        :return:
        """
        self.open()
        if mainkeyCondition == 0:
            row = self.session.query(dataInfo).first()
        else:
            row = self.session.query(dataInfo).filter(mainkeyCondition).first()

        self.close()  # 关闭资源
        if row is not None:
            return 1  # 存在
        else:
            return 0  # 不存在

    def upsertOneRow(self, updateOneDataInfo):
        """
        批量更新数据
        :param updateOneDataInfo: 要更新的实例对象数据
        :return:
        """
        # 开启资源
        self.open()
        try:
            # 插入单条数据
            # （1）如果存在就删除
            self.session.query(type(updateOneDataInfo)).filter(
                type(updateOneDataInfo).MaterialDrawing == updateOneDataInfo.MaterialDrawing).delete()
            # （2）然后插入新的数据
            self.session.add(updateOneDataInfo)
            self.session.commit()
        except Exception as e:
            # 当上述语句出现执行错误时，需要执行回滚语句，才能继续操作
            self.session.rollback()
            self.mylog.error('upsertOneRow: 数据更新failed {}'.format(e))
        finally:
            # 关闭资源
            self.close()

    def upsertBatchRow(self, updateBatchDataInfo: List):
        """
        批量更新数据
        :param updateBatchDataInfo: 要更新的实例对象数据
        :return:
        """
        if updateBatchDataInfo:
            # 开启资源
            self.open()
            for elemInfo in updateBatchDataInfo:

                try:
                    # 插入单条数据
                    # （1）如果存在就删除
                    self.session.query(type(elemInfo)).filter(
                        type(elemInfo).MaterialDrawing == elemInfo.MaterialDrawing).delete()
                    # （2）然后插入新的数据
                    self.session.add(elemInfo)
                    self.session.commit()
                except Exception as e:
                    # 当上述语句出现执行错误时，需要执行回滚语句，才能继续操作
                    self.session.rollback()
                    self.mylog.error('upsertBatchRow: 数据更新failed {}'.format(e))
                finally:
                    # 关闭资源
                    self.close()
        else:
            raise Exception("方法upsertBatchRow的参数updateBatchDataInfo为空列表集合")

    def insertOneRow(self, addOneDataRowInfo):
        """
        向表中添加一条数据：如果主键重复，则
        :param addOneDataRowInfo: 单条数据对象DataInfo()
        :param mainkeyCondition: 对主键字段进行过滤筛选的条件
        :return: 1表示插入成功
        """
        try:
            # 开启资源
            self.open()
            # 插入单条数据
            self.session.add(addOneDataRowInfo)
            self.session.commit()
            return 1
        except Exception as e:
            # 当上述语句出现执行错误时，需要执行回滚语句，才能继续操作
            self.session.rollback()
            print('failed', e)
            return 0
        finally:
            self.close()

    def insertBatchRow(self, addBatchDataRowInfo: List):
        """
        向表中添加多条数据
        :param addBatchDataRowInfo: 数据对象列表List[DataInfo]
        :return:
        """
        if addBatchDataRowInfo:
            try:
                self.open()
                # 插入多条数据
                # self.session.add_all(addBatchDataRowInfo)
                self.session.bulk_save_objects(addBatchDataRowInfo)
                self.session.commit()
                return 1

            except Exception as e:
                # 当上述语句出现执行错误时，需要执行回滚语句，才能继续操作
                self.session.rollback()
                self.mylog.error('insertBatchRow: 数据插入failed {}'.format(e))
                return 0
            finally:
                # 关闭资源
                self.close()
        else:
            raise Exception("方法insertBatchRow的输入参数addBatchDataRowInfo为空列表集合")

    def queryData(self, dataInfo, filterCondition, limitNum: int = None):
        """
        数据查询并获取返回结果
        :param dataInfo: 数据库中表数据对像DataInfo
        :param filterCondition: 数据查询筛选条件 0:表示没有条件
        = <: filter(DataInfo.EMP_ID <= '1009')、filter(DataInfo.EMP_ID != '1001')、
        IN : filter(~DataInfo.EDUCATION.in_(['Bachelor', 'Master']))、filter(DataInfo.EDUCATION.in_(['Bachelor', 'Master']))
        None :filter(DataInfo.MARITAL_STAT == None)、filter(DataInfo.MARITAL_STAT != None)
        AND :filter(and_(Employee.GENDER=='Female', Employee.EDUCATION=='Bachelor')、filter(DataInfo.GENDER=='Female', DataInfo.EDUCATION=='Bachelor'))
        OR : filter(or_(DataInfo.MARITAL_STAT=='Single', DataInfo.NR_OF_CHILDREN==0))
        LIKE : filter(DataInfo.EMP_ID.like('%9'))
        :param limitNum: 限制输出得条数
        :return:
        """
        try:
            # 打开对话
            self.open()
            # 查询数据
            if filterCondition == 0:
                res = self.session.query(dataInfo).limit(limitNum)
            else:
                res = self.session.query(dataInfo).filter(filterCondition).limit(limitNum).all()

            return res
        except Exception as e:
            print("查询的{}表数据不存在，err:{}".format(dataInfo, e))
        finally:
            # 关闭资源
            self.close()

    def dfSaveDb(self, df, tablename, savetype='append'):
        """
        将DataFrame表保存到数据库中
        :param df: 要保存得DataFrame
        :param tablename: 数据库中的表名称
        :return:
        """
        try:
            # 打开对话
            self.open()
            df.to_sql(name=tablename, con=self.session, if_exists=savetype, index=False)
        except Exception as e:

            self.mylog.error('dfSaveDb: 向DB保存dataframe failed {}'.format(e))
        finally:
            # 关闭资源
            self.close()