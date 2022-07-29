# 中航技物料编码唯一化项目
# 一、开发环境
python3.8.3 + redis3.0.4 + mssql-server-2017 + centos7.6
（1） redis,mssql安装

    redis3.0.4安装：https://peppered-yard-1b6.notion.site/Centos7-redis3-0-4-7521006f9b2747c1b6d7e5e3b88b492a
    mssql-server-2017 安装： https://peppered-yard-1b6.notion.site/Centos7-SQLServer-9c82acd744cc45199fbebf7722cad74f

（2）项目环境依赖 ./requirements.txt

# 二、项目背景
当前这个模型主要满足以下这四个场景的需求：
    （1）物料新增时，查询物料是否在主数据中存在相同、相似、完全新增；
    （2）新品需求录入时
    （3）采购询价任务分配时
    （4）返修需求校验时
    
# 三、项目目录
- OnlyMaterialZHJSys
    - logs
    - resource
    - moudle
        - bean
        - cio
        - common
        - process
        - util
        - BootStrap.py
        - DataDealModel.py
        - DataSynUpdate.py
        
# 四、项目概况
1、OnlyMaterialZHJSys主要实现两个内容：

（1）数据清洗 （2）相似度计算

2、OnlyMaterialZHJSys存在三个主要入口类：

（1）DataDealModel
    
    主要作用：将主数据“ MainMaterialInfo ”转换成统一编码和向量表数据“ MainMaterialUniformVector ” ；只执行一次，对主数据进行初始化。
（2）BootStrap
 
    主要作用：① 接收前端传回来的数据；② 将接收到的数据分割成主数据中存在查询到的结果集合query_milist和主数据中不存在caculate_simlar_milist数据集合；③ 集合caculate_simlar_milist数据处理后同 MainMaterialUniformVector
    计算相似度，并返回相似结果。
 (3)DataSynUpdate
    
    主要作用：用来同步保障平台主数据ProductData的数据变更、新增、删除数据到初始化表数据中MainMaterialUniformVector
 (4)三个主类的执行顺序
 
    step-1 DataDealModel：现要对保障平台主数据进行初始化MainMaterialUniformVector（会清除mssql和redis中的初始化表数据），即生成图号统一处理后的编码和向量。
    step-2 BootStrap: 通过http请求执行相似度计算和图号匹配任务，将计算结果写入结果表中。
    step-3 DataSynUpdate：当主数据中有数据发生变更时，通过接口的方式触发该数据同步程序的执行。
3、参数

3.1 BootStrap.run(task_id: str, task_data: str)

(1) 默认参数

    similarthreshold: float = 0.98                 # 相似度阈值
    startmp_threshold: int = 100                   # 开启多进程计算向量的阈值
    core_process: int = 6                          # 多进程核心数
    filterCondition = 0                            # 没有条件
    tablename: BatchInfo = BatchInfo               # 表名称
    db_path = "mysql+pymysql://root:123456@192.168.192.137:3306/db_onlymaterial_businessflow"  # 数据库地址
(2) 传入参数
    
    task_id: str = "1001"                          # 任务id
    task_data =  """
    {"data":[
        {"MaterialDrawing": "0777777", "Name": "保险丝3", "EnglishName": "ПРОВОЛОКА3", "Unit": "Meter3"},
        {"MaterialDrawing": "0888888", "Name": "保险丝8", "EnglishName": "ПРОВОЛОКА8", "Unit": "Meter8"}
        ]
    }
    """                                            # 前端传过来的数据"data"——jsonString
3.2 DataDealModel.run()

（1）默认参数
    
    db_path = "mysql+pymysql://root:123456@192.168.192.137:3306/db_onlymaterial_businessflow"
    core_process = 6
    startmp_threshold = 100
    filterCondition = 0
    tablename:MaterialInfo = MaterialInfo
    
4、数据来源
数据源可分为三种情况：本地csv数据getDatafromLocal、数据库数据getDatafromDB、http请求来的jsonstring数据 getDatafromHTTP
 
 (1) 本地csv数据 - getDatafromLocal
    
    # 从本地csv文件中获取数据需要加上下边两个参数
    # local_path = cfg["database"]["localcsv"]["url"]
    # tablename: BatchInfo = BatchInfo # 表名称
    # limitnum = base_config["limitnum"]

 BUIListIsDigit, BUIListNoDigit, query_milist = getDatafromLocal(input=input, local_path=local_path,
                                                                    tabelname=tabelname, SRIList=SRIList,
                                                                    startmp_threshold=startmp_threshold,
                                                                    core_process=core_process, limitnum=limitnum)

 (2) 数据库数据 - getDatafromDB
 
    # 从数据库中获取数据需要加上下边两个参数
    # filterCondition = cfg["basevariable"]["filterCondition"]  # 没有条件
    # tablename: BatchInfo = BatchInfo # 表名称
    # limitnum = base_config["limitnum"]

    BUIListIsDigit, BUIListNoDigit, query_milist = getDatafromDB(input=input, tabelname=tablename,
                                                                 SRIList=SRIList, filterCondition=0,
                                                                 startmp_threshold=startmp_threshold,
                                                                 core_process=core_process, limitnum=limitnum)
 (3) http请求来的jsonstring数据 - getDatafromHTTP
 
    BUIListIsDigit, BUIListNoDigit, query_milist = getDatafromHTTP(input=input, output=output, task_id=task_id,
                                                                   task_data=un_task_data,
                                                                   SRIList=SRIList,
                                                                   startmp_threshold=startmp_threshold,
                                                                   core_process=core_process)
# 五、注意事项
1、BatchSimilarCalculate()

在计算相似度的时，计算结果分为两种情况：

（1）找到相同或者相似的物料：`MatchLogo`: `0`表示没用匹配到，`1`表示匹配到了(包含匹配到的相同和相似的字符串)

（2）没有匹配到相同或相似数据，属于完全新增：相似度`similary=1.01`,表示只有自己,主数据中没有找相同或相似物料。编码Code、一级分类FirstClass、匹配状态MatchLogo分别赋值None,None,0；

2、需要修改的地方

（1）moudle.commom.Configuration.py

修改`configuration.yaml`配置文件的默认绝对路径yaml_file，将其修改为自己的绝对路径。

（2）在配置文件resource.configuration.yaml中

将mssql数据库修改成自己的`url`: database.mssql.url
将redis数据库修改为自己的`host`,`port`,`db`,`pwd`
将mylog日志路径修改为自己的本地路径 `path.log_path`

3、在所有BootStrap任务执行前，一定要有对主数据进行一次数据清洗和向量化DataDealModel，将其结果存入数据库表`material_uniform_vector`中供BootStrap任务调用
    因为所有的BootStrap任务都是基于DataDealModel它的计算结果来执行的。
    
    
4、相似度计算模型需要优化，要去process目录下对Similarity文件内的函数进行优化