#！/usr/bin/env python
#-*-coding:utf-8-*-
from collections import defaultdict

import pymysql

mysqlDbparams = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'baidu_baike',
        'charset': 'utf8'  # mysql中的编码就是utf8
    }
conn_baidu = pymysql.connect(**mysqlDbparams)
cursor_baidu = conn_baidu.cursor()

#获取互动百科库的连接
mysqlDbparams_hudong = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '123456',
        'database': 'hudong_baike',
        'charset': 'utf8'  # mysql中的编码就是utf8
    }
conn_hudong = pymysql.connect(**mysqlDbparams_hudong)
cursor_hudong = conn_hudong.cursor()

def get_result_detail(in_file,out_file):
    input_file = open(in_file,'r',encoding='utf-8')
    output_file = open(out_file,'w',encoding='utf-8')
    output_file.write("百度词条 互动词条 相似度\n")
    for line in input_file:
        list = line.split(" ")
        sql_baidu = 'select * from baidu_spider where id=%s'
        sql_hudong = 'select * from hudong_spider where id=%s'
        cursor_baidu.execute(sql_baidu,list[0])
        output_file.write(str(cursor_baidu.fetchone())+'\n')
        cursor_hudong.execute(sql_hudong,list[1])
        output_file.write(str(cursor_hudong.fetchone())+'\n')
        output_file.write(list[2]+'\r\n')
    input_file.close()
    output_file.close()


def get_recallAndAccuracy_by_result(leibie):
    # result_detail_file = "../file/"+leibie+"/resultForMinSim"+"/result_detail.txt"
    base_path="_threshold0.4_min_sim_topic_num4"
    result_detail_file = "../file/" + leibie+"/result_detail" +base_path+".txt"

    file_for_result_detail = open(result_detail_file,'w',encoding="utf-8")
    file_for_result_detail.write("threshold accurate recall F-score aveCandNum CandNumCount row\n")

    annotions_file="../file/"+leibie+"/annotion_ids.txt"
    file_for_annotion = open(annotions_file,'r',encoding='utf-8')
    id_dic = defaultdict(str)
    #avalible_count:记录可以找到匹配对的个数
    avalible_count=0
    for line in file_for_annotion:
        ids_list = line.split(" ")
        ids_list[1]=ids_list[1].replace('\n','')
        id_dic[ids_list[0]]=ids_list[1]
        if(ids_list[1]!="-1"):
            avalible_count=avalible_count+1

    for i in range(1, 2):
        # i = (i / 10)
        base_path="_threshold"+str(0.6)+"_min_sim0.4_topic_num4"

        # result_file = "../file/"+leibie+"/resultForMinSim"+"/result_threshold0.4_min_sim"+str(i)+"_topic_num8.txt"
        result_file = "../file/"+leibie+"/result"+base_path+".txt"
        file_for_result = open(result_file,'r',encoding='utf-8')
        #right_count:记录正确匹配的个数
        right_count = 0
        #count：记录系统找出的匹配个数
        count=0
        for line in file_for_result:
            count = count+1
            list = line.split(" ")
            if(id_dic[list[0]]==list[1]):
                right_count=right_count+1

        # 计算准确度
        accuracy = round(right_count/count,3)
        #计算召回率
        recall = round(right_count/avalible_count,3)
        #计算综合指标F值F=2*accuracy*recall/(accuracy+recall)
        F = round(2*accuracy*recall/(accuracy+recall),3)

        #关于候选集合的评价
        #平均候选集的大小，也就是平均每个候选集合有多少个元素
        # cands_file = "../file/"+leibie+"/resultForMinSim"+"/candidates_threshold0.4_min_sim"+str(i)+"_topic_num8.txt"
        cands_file = "../file/"+leibie+"/candidates"+base_path+".txt"
        file_for_cands = open(cands_file,'r',encoding="utf-8")
        row = 0#记录总共多少行
        cand_count=0 #记录所有候选集合的个数的总和
        for line in file_for_cands:
            list = line.split(" ")
            row=row+1
            cand_count= cand_count+int(list[1])
        average_cand_num = round(cand_count/count,3)

        s = str(i)+" "+str(accuracy)+" "+str(recall)+" "+str(F)+" "+str(average_cand_num)+" "+str(cand_count)+" "+str(row)+"\n"
        file_for_result_detail.write(s)
    file_for_result_detail.close()
    file_for_result.close()
    file_for_cands.close()
    file_for_annotion.close()


if __name__=='__main__':
    get_recallAndAccuracy_by_result("huaxue")

    get_recallAndAccuracy_by_result("jisuanji")

    get_recallAndAccuracy_by_result("renwu")

    get_recallAndAccuracy_by_result("shengwu")

    get_recallAndAccuracy_by_result("yuwenwenxue")