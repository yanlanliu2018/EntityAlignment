#！/usr/bin/env python
#-*-coding:utf-8-*-
import re

import redis

class candidate():
    def __init__(self,name_db,key_word_db):
        '''
        针对不同索引，获取redis数据库的连接，
        将数据库设置为只读模式
        '''
        redisDbParams = {
            'host': '127.0.0.1',
            'port': 6379,
            'db': name_db,
            'encoding': 'utf-8',
            'decode_responses': True
        }
        # 获取name索引库的连接
        index_by_name = redis.Redis(**redisDbParams)
        self.name_redis = index_by_name

        redisDbParams = {
            'host': '127.0.0.1',
            'port': 6379,
            'db': key_word_db,
            'encoding': 'utf-8',
            'decode_responses': True  # 为了避免返回值出现’b',eg:{b'61758'}
        }
        # 获取关键字索引库的连接
        index_by_keyword = redis.Redis(**redisDbParams)
        self.keyword_redis=index_by_keyword

    '''
    # 根据实体的名称以及各个别名分别获取候选集{ids}
    # 返回所有候选集的并集
    # 输入：待对齐实体，从数据库中获取的一条记录,索引数据库r，注意：这里我们不会
    # 输出：一个id集合(set)，也就是候选集
    '''
    def get_candidate_by_name(self,entry):
        name = entry[1]
        attribute = entry[2]
        # 使用set（ids）存储最终结果集合
        ids_set=set()
        # 将词条名的id挂载,使用‘['进行切分，因为在互动百科中词条名有[]备注
        # 根据词条名查询ids，并将其并入ids_set
        name = re.split('[（[]',name)[0]
        ids = self.name_redis.smembers(str(name))
        ids_set=ids_set.union(ids)
        # 将属性中的别名、外文名等与id一起挂载
        attributes = attribute.split(';')
        for attr in attributes:
            list = attr.split(':')
            # 如果属性名以”名“结尾，将其加入索引
            if (len(list) > 1 and (list[0].endswith('名') or list[0].endswith('称'))):
                name_list = re.split('[,，、/（《》）]', list[1])
                for key_name in name_list:
                    if (key_name == ""): continue
                    ids = self.name_redis.smembers(key_name)
                    ids_set = ids_set.union(ids)
        return ids_set


    '''
    # 根据实体中的前缀关键词分别获取候选集{ids}
    # 返回所有候选集的并集
    # 输入：待对齐实体的wprd_tfidf向量，文本相似度阙值（threshold）
    # 输出：一个id集合，也就是候选集
    '''
    def get_candidate_by_keyword(self,word_tfidf,threshold):
        # 使用set（ids）存储最终结果集合
        ids_set = set()
        # 计算待对齐实体的前缀值
        pre_num= self.get_keyword_num_byCos(threshold, word_tfidf)
        for i in range(0,pre_num):
            keyword=word_tfidf[i][0]
            ids = self.keyword_redis.smembers(keyword)
            ids_set=ids_set.union(ids)
        return ids_set

    def get_keyword_num_byCos(self,threshold, word_tfidf):
        thre = 0
        for word in word_tfidf:
            thre += word[1] * word[1]
        thre = thre * threshold * threshold
        count = 0
        num = len(word_tfidf) - 1
        while num >= 0 and count < thre:
            count += word_tfidf[num][1] * word_tfidf[num][1]
            num -= 1
        # if(num<0):num=0
        # else:num+=1
        return num + 1

    '''
    将所有候选集合的交集作为最后结果返回
    '''
    def get_candidate(self,entry,word_tfidf,threshold):
        idsByName = self.get_candidate_by_name(entry)
        idsByKeyword = self.get_candidate_by_keyword(word_tfidf,threshold)
        ids_set=idsByName.intersection(idsByKeyword)
        return ids_set