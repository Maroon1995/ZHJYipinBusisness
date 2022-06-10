import redis
import json
from util.LogUtil import MyLog
from bean.MainMaterialInfo import MaterialInfo

class RedisHelper:

    mylog = MyLog()

    def __init__(self, host, port, db):
        """
        连接redis
        :param host:
        :param port:
        :param db:
        """
        try:
            conn = redis.ConnectionPool(host=host, port=port, db=db)
            self.__redis = redis.StrictRedis(connection_pool=conn, decode_responses=True, charset="UTF-8",
                                             encoding="UTF-8")
        except Exception as error:
            self.mylog.error('连接redis出现问题Error: {}'.format(error))
            exit()

    # -------------------------------------------------------------
    def set(self, key, value):
        """
        存入string类型：k-v
        :param key:
        :param value:
        :return:
        """
        self.__redis.set(key, value)

    def get(self, key):
        """
        获取string类型的值
        :param key:
        :return:
        """
        return self.__redis.get(key).decode()

    def is_existsKey(self, key, expireTime: int = 600):
        """
        判断key是否存在
        :param key:
        :param expireTime: 过期时间，单位秒s
        :return: 返回True存在，False不存在
        """
        self.__redis.expire(key, expireTime)
        return self.__redis.exists(key)

    # ----------------------------------------------------------------
    def add_set(self, key, value, expireTime: int = 600):
        """
        集合set中存在该元素则返回0,不存在则添加进集合中，并返回1
        如果key不存在，则创建key集合，并添加元素进去,返回1
        :param key:
        :param value:
        :return:
        """
        self.__redis.expire(key, expireTime)
        return self.__redis.sadd(key, value)

    def del_set(self, key, *values, expireTime: int = 600):
        """
        移除集合中一个或多个成员
        :param key: 集合名称
        :param *values:多个值
        """
        if values:
            self.__redis.expire(key, expireTime)
            self.__redis.srem(key, *values)
        else:
            raise Exception("*values不能为空！")

    def get_set(self, key, expireTime: int = 600):
        """
        返回集合中的所有成员
        :param key:
        :param expireTime:
        :return: 返回一个set集合
        """
        self.__redis.expire(key, expireTime)
        return self.__redis.smembers(key)

    def count_set(self, key, expireTime: int = 600):
        """返回集合的成员数量"""
        self.__redis.expire(key, expireTime)

        return self.__redis.scard(key)

    def is_inSet(self, key, value, expireTime):
        '''判断value是否在key集合中，返回布尔值'''

        self.__redis.expire(key, expireTime)
        return self.__redis.sismember(key, value)

    # ----------------------------------------------------------------
    def add_list(self, name: str, value: str, expireTime: int = 600):
        """
        列表List类型,向列表添加数据
        :param name: 列表名称
        :param value:
        :param expireTime: 过期时间,单位秒s
        :return:
        """
        try:
            self.__redis.lpush(name, value)
            self.__redis.expire(name, expireTime)

        except Exception as e:
            self.mylog.error("Error:向redis中添加数据失败: {}".format(e))

    def get_list(self, name: str, expireTime: int = 600):
        """
        列表List类型,获取列表数据
        :param name: 列表名称
        :param expireTime: 过期时间
        :return: 返回一个列表字符串
        """
        try:
            res = self.__redis.lrange(name, 0, -1)
            self.__redis.expire(name, expireTime)

            return res
        except Exception as e:
            self.mylog.error("Error:向redis中获取数据失败: {}".format(e))
    # ----------------------------------------------------------------

    def add_hset(self, name, key, value, expireTime: int = 600):
        """
        向哈希表name中添加key-value
        :param name:
        :param key:
        :param value:
        :param expireTime:
        :return:
        """
        try:
            self.__redis.expire(name, expireTime)
            self.__redis.hset(name, key, value)
        except Exception as e:
            self.mylog.error("向哈希表{}添加数据失败: {}".format(name, e))

    def get_hset(self, name, key, expireTime: int = 600):
        """
        获取存储在哈希表中指定字段的值
        :param name:哈希表名称
        :param key:字段
        :param expireTime:
        :return:
        """
        self.__redis.expire(name, expireTime)
        return self.__redis.hget(name, key)

    def getall_hset(self, name, expireTime: int = 600):
        """
        获取在哈希表name中指定所有字段和值
        :param name:
        :param expireTime:
        :return:
        """
        self.__redis.expire(name, expireTime)
        return self.__redis.hgetall(name)

    def getall_values_hset(self, name, expireTime: int = 600):
        """
        获取哈希表name中所有值values
        :param name:
        :param expireTime:
        :return:
        """
        self.__redis.expire(name, expireTime)
        return self.__redis.hvals(name)

    def count_hset(self, name, expireTime: int = 600):
        """
        获取哈希表name中所有key(字段)的数量
        :param name:
        :param expireTime:
        :return:
        """
        self.__redis.expire(name, expireTime)
        return self.__redis.hlen(name)

    def del_hset(self, name, *key, expireTime: int = 600):
        """
        删除指定哈希表name中的key（字段）
        :param name:
        :param key:
        :param expireTime:
        :return:
        """
        self.__redis.expire(name, expireTime)
        self.__redis.hdel(name, *key)

    def isExists_hset(self, name, key, expireTime: int = 600):
        """
        查看哈希表 name 中，指定的字段key是否存在
        :param name: 哈希表名称
        :param key: 表字段名称
        :param expireTime:
        :return: 如果哈希表含有给定字段，返回 1 。 如果哈希表不含有给定字段，或 key 不存在，返回 0
        """
        self.__redis.expire(name, expireTime)
        return self.__redis.hexists(name, key)

    # ----------------------------------------------------------------
    def flushData(self, name: str):
        """
        删除key及其数据
        :param name:
        :return:
        """
        self.__redis.delete(name)
