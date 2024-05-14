import time
from tqdm import tqdm
from multiprocessing import Process, Queue
from time import time, localtime, strftime, sleep

import argparse
import numpy as np
import tensorflow as tf


def get_neg_samples(user, num_item, matrix, num_neg):
    ritems = []
    while (len(ritems) != num_neg):
        sitems = set(np.random.randint(0, high=num_item, size=num_neg - len(ritems)))
        for i in sitems:
            if matrix[user, i] != 1:
                ritems.append(i)
    return ritems

def batch_sampling(users, items, matrix, num_item, batch_size, batch_per_worker, num_neg, result_queue):
    """

    :param users: list of users in the training set
    :param items: list of items corresponding to the users list
    :param matrix: the user-item interaction matrix for the training set
    :param batch_size: number of examples in a batch
    :param num_neg: number of negative samples per per positive user-item pair
    :param result_queue: the output queue
    :return: None
    """
    for j in range(batch_per_worker):
        batch_user = users[j * batch_size: (j + 1) * batch_size]
        batch_item = items[j * batch_size: (j + 1) * batch_size]
        batch_user_neg = []
        batch_item_neg = []
        for u in batch_user:
            batch_user_neg += [u for s in range(num_neg)]
            batch_item_neg += get_neg_samples(u, num_item, matrix, num_neg)
        result_queue.put((batch_user, batch_item, batch_user_neg, batch_item_neg))


class BatchSampler(object):
    def __init__(self, users, items, matrix, num_item, total_batch, batch_size, num_neg, n_workers):
        idxs = np.random.permutation(len(items))
        self.users = list(users[idxs])
        self.items = list(items[idxs])
        self.mp = n_workers > 1
        self.batch_size = batch_size
        self.num_neg = num_neg
        self.bach_idx = 0

        if self.mp:
            batch_per_worker = total_batch // n_workers
            self.result_queue = Queue(maxsize=0)
            self.processors = []
            for i in range(n_workers):
                m = i * batch_per_worker * batch_size
                n = (i + 1) * batch_per_worker * batch_size
                self.processors.append(
                    Process(target=batch_sampling, args=(self.users[m:n],
                                                         self.items[m:n],
                                                         matrix,
                                                         num_item,
                                                         batch_size,
                                                         batch_per_worker,
                                                         num_neg,
                                                         self.result_queue)))
                self.processors[-1].start()
            m = n_workers * batch_per_worker * batch_size
            n = total_batch * batch_size
            self.processors.append(
                Process(target=batch_sampling, args=(self.users[m:n],
                                                     self.items[m:n],
                                                     matrix,
                                                     num_item,
                                                     batch_size,
                                                     total_batch - n_workers * batch_per_worker,
                                                     num_neg,
                                                     self.result_queue)))
            self.processors[-1].start()
        else:
            self.user_neg = []
            self.item_neg = []
            for u in tqdm(users):
                self.user_neg += [u for i in range(num_neg)]
                self.item_neg += get_neg_samples(u, num_item, matrix, num_neg)

    def next_batch(self):
        if self.mp:
            self.bach_idx += 1
            return self.result_queue.get()
        else:
            batch_user = self.users[self.bach_idx * self.batch_size: (self.bach_idx + 1) * self.batch_size]
            batch_user_neg = self.user_neg[
                             self.bach_idx * self.batch_size: (self.bach_idx + self.num_neg) * self.batch_size]
            batch_item = self.items[self.bach_idx * self.batch_size: (self.bach_idx + 1) * self.batch_size]
            batch_item_neg = self.item_neg[
                             self.bach_idx * self.batch_size: (self.bach_idx + self.num_neg) * self.batch_size]
            self.bach_idx += 1
            return (batch_user, batch_item, batch_user_neg, batch_item_neg)

    def empty(self):
        if self.mp:
            return self.result_queue.empty()
        else:
            return False

    def batch_index(self):
        return self.bach_idx

    def close(self):
        if self.mp:
            for p in self.processors:
                p.terminate()
                p.join()


class Config:
    def __init__(self, num_user, num_item, num_rel, args):
        self.num_user = num_user
        self.num_item = num_item
        self.num_rel = num_rel
        self.dataset = args.dataset

        self.num_process = args.num_process
        self.verbose = True


class Hyperparameters:
    def __init__(self):
        self.params_paper = {
            'qmy':
                {
                    'kgecf': {'learning_rate': 0.0001, 'num_factor': 1000, 'num_neg': 8, 'margin': 0.1, 'alpha': 1.0,
                              'batch_size': 1000, 'epochs': 5000}
                }
        }

    def load_hyperparameter(self, dataset, model):
        d_name = dataset.lower()
        m_name = model.lower()

        if d_name in self.params_paper and m_name in self.params_paper[d_name]:
            params = self.params_paper[d_name][m_name]
            return params


class KGECFConfig(Config):
    def __init__(self, num_user, num_item, num_rel, args):
        params = Hyperparameters().load_hyperparameter(args.dataset, 'kgecf')
        for key, value in params.items():
            self.__dict__[key] = value

        Config.__init__(self, num_user, num_item, num_rel, args)


class KGECF():
    def __init__(self, config):
        self.name = "KGECF"
        self.config = config

    def embedding(self, u, r, i):
        pi = 3.14159265358979323846
        u_e_r = tf.nn.embedding_lookup(self.user_embeddings, u)
        u_e_i = tf.nn.embedding_lookup(self.user_embeddings_im, u)
        i_e_r = tf.nn.embedding_lookup(self.item_embeddings, i)
        i_e_i = tf.nn.embedding_lookup(self.item_embeddings_im, i)
        r_e_r = tf.nn.embedding_lookup(self.rel_embeddings, r)
        r_e_r = r_e_r / (self.embedding_range / pi)
        r_e_i = tf.sin(r_e_r)
        r_e_r = tf.cos(r_e_r)
        return u_e_r, u_e_i, r_e_r, r_e_i, i_e_r, i_e_i

    def infer(self, u, r, i):
        u_e_r, u_e_i, r_e_r, r_e_i, i_e_r, i_e_i = self.embedding(u, r, i)
        score_r = u_e_r * r_e_r - u_e_i * r_e_i - i_e_r
        score_i = u_e_r * r_e_i + u_e_i * r_e_r - i_e_i
        return -(self.config.margin - tf.reduce_sum(score_r ** 2 + score_i ** 2, axis=-1))

    def build_network(self):
        self.user_id = tf.compat.v1.placeholder(dtype=tf.int32, shape=[None], name='user_id')
        self.user_id_neg = tf.compat.v1.placeholder(dtype=tf.int32, shape=[None], name='user_id_neg')
        self.item_id = tf.compat.v1.placeholder(dtype=tf.int32, shape=[None], name='item_id')
        self.item_id_neg = tf.compat.v1.placeholder(dtype=tf.int32, shape=[None], name='item_id_neg')
        self.rel_id = tf.compat.v1.placeholder(dtype=tf.int32, shape=[None], name='rel_id')
        self.rel_id_neg = tf.compat.v1.placeholder(dtype=tf.int32, shape=[None], name='rel_id')

        # Embedding layer
        with tf.name_scope("embedding"):
            self.embedding_range = (self.config.margin + 2.0) / self.config.num_factor
            emb_initializer = tf.random_uniform_initializer(minval=-self.embedding_range, maxval=self.embedding_range)
            self.user_embeddings = tf.Variable(emb_initializer(shape=(self.config.num_user, self.config.num_factor)),
                                               name="user_embedding")
            self.user_embeddings_im = tf.Variable(emb_initializer(shape=(self.config.num_user, self.config.num_factor)),
                                                  name="user_embedding_imag")
            self.item_embeddings_im = tf.Variable(emb_initializer(shape=(self.config.num_item, self.config.num_factor)),
                                                  name="item_embedding_imag")
            self.item_embeddings = tf.Variable(emb_initializer(shape=(self.config.num_item, self.config.num_factor)),
                                               name="item_embedding")
            self.rel_embeddings = tf.Variable(emb_initializer(shape=(self.config.num_rel, self.config.num_factor)),
                                              name="rel_embedding")

        self.pred = -self.infer(self.user_id, self.rel_id, self.item_id)
        self.pred_neg = -self.infer(self.user_id_neg, self.rel_id_neg, self.item_id_neg)

        # Calculate loss
        with tf.name_scope("loss"):
            pos_preds = self.pred
            neg_preds = self.pred_neg
            pos_preds = tf.math.log_sigmoid(pos_preds)
            neg_preds = tf.reshape(neg_preds, [-1, self.config.num_neg])
            softmax = tf.stop_gradient(tf.nn.softmax(neg_preds * self.config.alpha, axis=1))
            neg_preds = tf.reduce_sum(softmax * (tf.math.log_sigmoid(-neg_preds)), axis=-1)
            self.loss = -tf.reduce_mean(neg_preds) - tf.reduce_mean(pos_preds)

        self.optimizer = tf.compat.v1.train.AdamOptimizer(self.config.learning_rate).minimize(self.loss)

        return self

    def train(self, sess, users, items, matrix, total_batch):
        t1 = time()
        mloss = []

        print("Train start:" + strftime("%Y%m%d%H%M", localtime(t1)))

        sampler = BatchSampler(users, items, matrix, self.config.num_item, total_batch, self.config.batch_size,
                               self.config.num_neg, self.config.num_process)

        # train
        with tqdm(total=total_batch) as pbar:
            while sampler.batch_index() < total_batch:
                batch_user, batch_item, batch_user_neg, batch_item_neg = sampler.next_batch()
                _, loss = sess.run((self.optimizer, self.loss),
                                   feed_dict={self.user_id: batch_user,
                                              self.item_id: batch_item,
                                              self.rel_id: np.zeros(len(batch_user)),
                                              self.rel_id_neg: np.zeros(len(batch_user_neg)),
                                              self.user_id_neg: batch_user_neg,
                                              self.item_id_neg: batch_item_neg})
                mloss.append(np.nanmean(loss))
                pbar.update(1)
        if self.config.verbose:
            print("loss= %.9f" % mloss[0])

        sampler.close()
        t2 = time()
        print("Training Time: %s seconds/epoch." % (t2 - t1))

    def predict(self, sess, user_id, item_id):
        return sess.run([self.pred],
                        feed_dict={self.user_id: user_id,
                                   self.rel_id: np.zeros(len(user_id)),
                                   self.item_id: item_id})[0]


def parse_args():
    parser = argparse.ArgumentParser(description='KGECF')
    parser.add_argument('--model', default='KGECF')
    parser.add_argument('--dataset', default='qmy')
    parser.add_argument('--num_process', type=int, default=10)
    return parser.parse_args()



def test(sess, model, user_id, n_item, n_rec=10):
    user_ids = [user_id for i in range(n_item)]
    item_ids = [i for i in range(n_item)]
    scores = model.predict(sess, user_ids, item_ids)
    neg_item_index = list(zip(item_ids, scores))
    ranked_list = sorted(neg_item_index, key=lambda tup: tup[1], reverse=True)
    ranked_list = ranked_list[:10]
    items = [item_id for item_id, score in ranked_list[:n_rec]]
    return items

def get_ans(user_id, n_rec=10):
    args = parse_args()

    n_user, n_item = 200, 650
    config = tf.compat.v1.ConfigProto()
    config.gpu_options.allow_growth = True

    with tf.compat.v1.Session(config=config) as sess:
        conf = KGECFConfig(n_user, n_item, 1, args)
        model = KGECF(conf)
        model.build_network()
        init = tf.compat.v1.global_variables_initializer()
        sess.run(init)
        saver = tf.compat.v1.train.Saver(max_to_keep=5)
        saver.restore(sess, r"D:\knowledgeGraph\programmer\app\user\KGECF-qmy-202405141402")
        item_ids = test(sess, model, user_id, n_item, n_rec=n_rec)
        return item_ids

