# -*- coding:utf8 -*-
from __future__ import division,absolute_import, print_function, unicode_literals
import os

import surprise
from surprise import KNNBaseline, NMF, Reader
from surprise import Dataset

from data_helper import DataConvertHelper
from config import model_dir

pred_type_list = ['playlist', 'user']

class Recmodel(object):
    def __init__(self, algo='knn_baseline', filepath=None):
        if not os.path.exists(filepath):
            raise FileNotFoundError("{} not exist".format(filepath))
        self.filepath = filepath
        if algo == 'nmf':
            self.algo = NMF()
            self.model_name = 'nmf'
        else:
            self.algo = KNNBaseline()
            self.model_name = 'knn_baseline'

        self.convertor = DataConvertHelper()

    def buildDataSet(self):
        reader = Reader(line_format='user item rating timestamp', sep=',')
        music_data = Dataset.load_from_file(file_path=self.filepath, reader=reader)
        self.trainset = music_data.build_full_trainset()

    def train(self):
        print("begin training...")
        self.algo.fit(self.trainset)

    def evaluate(self, index):
        current_playlist_name = self.convertor.get_name_by_index(index)
        print('当前歌单:{}'.format(current_playlist_name))

        current_playlist_rid = self.convertor.get_rid_by_name(current_playlist_name)
        print("当前歌单rid: {}".format(current_playlist_rid))

        playlist_inner_id = self.algo.trainset.to_inner_uid(current_playlist_rid)
        print('歌单inid', playlist_inner_id)

        playlist_neighbors_inner_ids = self.algo.get_neighbors(playlist_inner_id, k=10)
        playlist_neighbors_rids = (self.algo.trainset.to_raw_uid(inner_id) for inner_id in playlist_neighbors_inner_ids)
        playlist_neighbors_names = (self.convertor.get_name_by_rid(rid) for rid in playlist_neighbors_rids)

        print('歌单 《', current_playlist_name, '》 最接近的10个歌单为:')
        for playlist_name in playlist_neighbors_names:
            print(playlist_name, self.algo.trainset.to_inner_uid(self.convertor.get_rid_by_name(playlist_name)))
