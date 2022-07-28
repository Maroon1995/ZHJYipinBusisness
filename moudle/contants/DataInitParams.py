
from common.Configuration import readConfig
from common.DataInOut import DataIn, DataOut
from util.RedisUtil import RedisHelper
from util.SqlalchemyUtil import SQLUtil
from bean.MainMaterialInfo import MaterialInfo

# 配置文件
cfg = readConfig()
base_config = cfg["basevariable"]
mssql_config = cfg["database"]["mssql"]
# 参数设置
redis_config = cfg["database"]["redis"]["config"]
startmp_threshold = base_config["startmp_threshold"]
core_process = base_config["core_process"]
db_path = mssql_config["url"]  # 任务主机数据库地址
pb_path = mssql_config["p-url"]  # 保障平台主机数据库地址
tablename = MaterialInfo
# 实例化对象
db_output = DataOut(db_path)  # 输出到任务主机数据库
db_session = SQLUtil(path=db_path)
pd_input = DataIn(pb_path)  # 输入来自保障平台
redisUtil = RedisHelper(redis_config["host"], redis_config["port"], redis_config["db"], redis_config["pwd"])