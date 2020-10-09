from bert_serving.client import BertClient
import numpy as np

DEV_BERT_SERVER_IP="121.40.185.170"

class BertSupport:
    def __init__(self, use_timeout = True):
        if use_timeout:
            # Bert客户端请求BertServer服务，参数ip为服务地址
            self.bc = BertClient(ip =DEV_BERT_SERVER_IP, timeout=15000, check_version=False)
        else:
            self.bc = BertClient(ip=DEV_BERT_SERVER_IP, check_version=False)

    def compute_cosine(self, word1, word2):
        # 使用bert对该对文本进行encode成向量
        a = self.bc.encode([word1, word2])
        vector_a = np.mat(a[0])
        vector_b = np.mat(a[1])
        num = float(vector_a * vector_b.T)
        denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
        # 计算向量余弦
        cos = num / denom
        # 计算相似度
        sim = 0.5 + 0.5 * cos
        return sim


    def compute_distance(self, word1, word2):
        a = self.bc.encode([word1, word2])
        distance = a[0] - a[1]
        distance_sum = np.sum(distance)
        return np.abs(distance_sum)

    def close(self):
        self.bc.close()

if __name__ == '__main__':
    # 传入两个文本进行相似度计算
    print(BertSupport().compute_cosine("英文名", "外文名"))



