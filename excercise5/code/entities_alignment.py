#！/usr/bin/env python
#-*-coding:utf-8-*-



import json
import time
from excercise5.code import similarity_caculation, candidate, Index,LDA

'''
使用索引与tfidf来做知识融合
'''
def alignment_by_nameAndTFIDF(db,entity_table,threshold,name_db,key_word_db,result_file,tfidfs_entity,tfidfs_cands,cands_file):
    #从mysql数据库中获取互动百科的数据（互动百科作为待对齐数据）
    entity_data= Index.get_data(db, entity_table)
    #遍历互动百科数据（entry）id-name-attributes
    i=0
    # 使用文件记录最终匹配的结果（candidates.txt)entry-id-详细信息-id-详细信息
    alignment_entries = open(result_file, 'w', encoding='utf-8')
    tfidfs_entity = json.load(open(tfidfs_entity,encoding='utf-8'))
    tfidfs_cands = json.load(open(tfidfs_cands, encoding='utf-8'))

    cand = candidate.candidate(name_db=name_db,key_word_db=key_word_db)

    for entry in entity_data:
        #根据id (entry[0])从数据库中获取其tfidf词向量
        #有可能没有返回值
        id=entry[0]
        entity_word_tfidf=tfidfs_entity[str(id)]
        #当存在tfidf词向量时
        if(entity_word_tfidf):
            #获取候选集
            id_set = cand.get_candidate(entry=entry,word_tfidf=entity_word_tfidf,threshold=threshold,cands_file=cands_file)
            # 计算相似度，判定是否对齐
            candidates={}#用于存储所有有效的候选词向量；id-wordlist
            for id in id_set:
                #这里通过id获取的tfidf向量有可能为空
                cand_word_tfidf = tfidfs_cands[id]
                if cand_word_tfidf:
                    candidates[id]=cand_word_tfidf
            if len(candidates)!=0:
                result_id,max_similarity=similarity_caculation.txt_similarity_by_tfidf(entity_word_tfidf,candidates)
                if(max_similarity>threshold):
                    alignment_entries.write(str(entry[0])+' '+str(result_id)+' '+str(max_similarity)+'\n')

'''
使用索引与LDA来做知识融合
'''
def alignment_by_nameAndLDA(db,entity_table,threshold,name_db,key_word_db,result_file,
                            tfidfs_entity,LDA_entity,LDA_cands,cands_file,min_sim,data_name,topic_num):
    #从mysql数据库中获取互动百科的数据（互动百科作为待对齐数据）
    entity_data= Index.get_data(db, entity_table)
    #遍历互动百科数据（entry）id-name-attributes

    # 使用文件记录最终匹配的结果（candidates.txt)entry-id-详细信息-id-详细信息
    alignment_entries = open(result_file, 'w', encoding='utf-8')
    tfidfs_entity = json.load(open(tfidfs_entity,encoding='utf-8'))
    LDA_entity = json.load(open(LDA_entity,encoding='utf-8'))
    LDA_cands = json.load(open(LDA_cands, encoding='utf-8'))

    cand = candidate.candidate(name_db=name_db,key_word_db=key_word_db)

    for entry in entity_data:
        #根据id (entry[0])从数据库中获取其tfidf词向量
        #有可能没有返回值
        id=entry[0]
        entity_word_tfidf=tfidfs_entity[str(id)]
        entity_words=LDA_entity[str(id)]
        #当存在tfidf词向量时
        if(entity_word_tfidf):
            #获取候选集
            id_set = cand.get_candidate(entry=entry,word_tfidf=entity_word_tfidf,threshold=threshold,cands_file=cands_file)
            # 计算相似度，判定是否对齐
            candidates={}#用于存储所有有效的候选词向量；id-wordlist
            for id in id_set:
                cand_words= LDA_cands[id]
                if cand_words:
                    candidates[id]=cand_words
            if len(candidates)!=0:
                # result_id,max_similarity=similarity_caculation.txt_similarity_by_LDA(entity_words,candidates,topic_num)
                result_id, max_similarity = similarity_caculation.txt_similarity_by_LDA_Model(entity_words, candidates,topic_num)
                if(max_similarity>min_sim):
                    alignment_entries.write(str(entry[0])+' '+str(result_id)+' '+str(max_similarity)+'\n')


def exe_for_5_datas(threshold):
    print("化学")
    alignment_by_nameAndTFIDF(db="baike_spider",entity_table="hudong_huaxue",threshold=threshold,name_db=1,
                              key_word_db=2,
                              result_file="../file/huaxue/result_"+str(threshold)+".txt",
                              tfidfs_entity="../file/huaxue/hudong_tfidf.json",
                              tfidfs_cands="../file/huaxue/baidu_tfidf.json",
                              cands_file="../file/huaxue/candidates_"+str(threshold)+".txt")

    print("计算机")
    alignment_by_nameAndTFIDF(db="baike_spider", entity_table="hudong_jisuanji", threshold=threshold, name_db=3,
                              key_word_db=4,
                              result_file="../file/jisuanji/result_"+str(threshold)+".txt",
                              tfidfs_entity="../file/jisuanji/hudong_tfidf.json",
                              tfidfs_cands="../file/jisuanji/baidu_tfidf.json",
                              cands_file="../file/jisuanji/candidates_"+str(threshold)+".txt")
    print("人物")
    alignment_by_nameAndTFIDF(db="baike_spider", entity_table="hudong_renwu", threshold=threshold, name_db=5,
                              key_word_db=6,
                              result_file="../file/renwu/result_"+str(threshold)+".txt",
                              tfidfs_entity="../file/renwu/hudong_tfidf.json",
                              tfidfs_cands="../file/renwu/baidu_tfidf.json",
                              cands_file="../file/renwu/candidates_"+str(threshold)+".txt")
    print("生物")
    alignment_by_nameAndTFIDF(db="baike_spider", entity_table="hudong_shengwu", threshold=threshold, name_db=7,
                              key_word_db=8,
                              result_file="../file/shengwu/result_"+str(threshold)+".txt",
                              tfidfs_entity="../file/shengwu/hudong_tfidf.json",
                              tfidfs_cands="../file/shengwu/baidu_tfidf.json",
                              cands_file="../file/shengwu/candidates_"+str(threshold)+".txt")
    print("语文文学")
    alignment_by_nameAndTFIDF(db="baike_spider", entity_table="hudong_yuwenwenxue", threshold=threshold, name_db=9,
                              key_word_db=10,
                              result_file="../file/yuwenwenxue/result_"+str(threshold)+".txt",
                              tfidfs_entity="../file/yuwenwenxue/hudong_tfidf.json",
                              tfidfs_cands="../file/yuwenwenxue/baidu_tfidf.json",
                              cands_file="../file/yuwenwenxue/candidates_"+str(threshold)+".txt")

def exe_for_one_data_by_LDA(data_name,threshold,min_sim,topic_num,name_db,key_word_db):
    entity_table="hudong_"+data_name
    result_file="../file/"+data_name+"/result_threshold" + str(threshold)+"_min_sim"+str(min_sim)+"_topic_num"+str(topic_num) + ".txt"
    tfidfs_entity="../file/"+data_name+"/hudong_tfidf.json"
    LDA_entity="../file/"+data_name+"/hudong_words.json"
    LDA_cands = "../file/"+data_name+"/baidu_words.json"
    cands_file = "../file/"+data_name+"/candidates_threshold" + str(threshold)+"_min_sim"+str(min_sim)+"_topic_num"+str(topic_num) + ".txt"
    # LDA.product_LDA_model(topic_num, data_name)
    alignment_by_nameAndLDA(db="baike_spider",
                            entity_table=entity_table,
                            threshold=threshold,
                            name_db=name_db,
                            key_word_db=key_word_db,
                            result_file=result_file,
                            tfidfs_entity=tfidfs_entity,
                            LDA_entity=LDA_entity,
                            LDA_cands=LDA_cands,
                            cands_file=cands_file,
                            min_sim=min_sim,
                            data_name=data_name,
                            topic_num=topic_num
                            )
def exe_for_5_datas_by_LDA(threshold,min_sim,topic_num):
    print("开始对数据集：threshold"+str(threshold)+"_min_sim"+str(min_sim)+"_topic_num"+str(topic_num) +"进行融合")
    print("化学")
    exe_for_one_data_by_LDA(data_name="huaxue",threshold=threshold,min_sim=min_sim,topic_num=topic_num,name_db=1,key_word_db=2)

    print("计算机")
    exe_for_one_data_by_LDA(data_name="jisuanji",threshold=threshold,min_sim=min_sim,topic_num=topic_num,name_db=3,key_word_db=4)

    print("人物")
    exe_for_one_data_by_LDA(data_name="renwu",threshold=threshold,min_sim=min_sim,topic_num=topic_num,name_db=5,key_word_db=6)

    print("生物")
    exe_for_one_data_by_LDA(data_name="shengwu",threshold=threshold,min_sim=min_sim,topic_num=topic_num,name_db=7,key_word_db=8)

    print("语文文学")
    exe_for_one_data_by_LDA(data_name="yuwenwenxue",threshold=threshold,min_sim=min_sim,topic_num=topic_num,name_db=9,key_word_db=10)




if __name__ == '__main__':
    threshold=0.5#构建索引与获取候选集合时使用的阙值
    min_sim=0.6#相似度的最小值
    topic_num=7
    print("化学")
    # alignment_by_nameAndTFIDF(db="baike_spider", entity_table="hudong_huaxue", threshold=threshold, name_db=1,
    #                           key_word_db=2,
    #                           result_file="../file/huaxue/result.txt",
    #                           tfidfs_entity="../file/huaxue/hudong_tfidf.json",
    #                           tfidfs_cands="../file/huaxue/baidu_tfidf.json")

    alignment_by_nameAndLDA(db="baike_spider",
                            entity_table="hudong_huaxue",
                            threshold=threshold,
                            name_db=1,
                              key_word_db=2,
                              result_file="../file/huaxue/result.txt",
                              tfidfs_entity="../file/huaxue/hudong_tfidf.json",
                            LDA_entity="../file/huaxue/hudong_words.json",
                            LDA_cands="../file/huaxue/baidu_words.json",
                            cands_file="../file/yuwenwenxue/candidates_" + str(threshold) + ".txt",
                            min_sim=min_sim,
                            topic_num=topic_num
                            )