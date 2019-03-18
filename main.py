# -*- coding:utf8 -*-
from config import *
from model import Recmodel
import argparse
import surprise
import random


def parse():
    parser = argparse.ArgumentParser(description="params setting for netease cloud music recommender")
    parser.add_argument('-tr', '--train', action='store_true', help='train the recommendation  system model')
    parser.add_argument('-al', '--algorithm', type=str, default='knn_baseline', choices=['knn_baseline', 'nmf', 'sdv'],
                        help='optional recommending algorithm')
    parser.add_argument('-fp', '--filepath', default=formated_file, help='surprise dataset file path')
    parser.add_argument('-te', '--test', help='evaluate the model, model path should be specified')
    parser.add_argument('-i', '--index', default=30, help='playlist index in dataset')
    # TODO, add more params
    args = parser.parse_args()

    return args

def run(args):
    return
    # TODO
if __name__=='__main__':
    args = parse()

    model =Recmodel(filepath=formated_file)
    model.buildDataSet()
    model.train()
    print('=================================================')
    index = random.randint(1, 100)
    model.evaluate(index)