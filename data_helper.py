# -*- coding:utf8 -*-
import _pickle as pickle
from config import *
import json
import os

def is_null(s):
    return len(s.split(',')) > 2

class DataConvertHelper():
    def __init__(self) -> None:

        self.playlist_id2name = pickle.load(open(playlist_file, 'rb'), encoding='utf8')
        self.playlist_name2id = {}
        for playlist_id in self.playlist_id2name:
            self.playlist_name2id[self.playlist_id2name[playlist_id]] = playlist_id
        print('完成歌单列表名字和id之间的映射关系')

        self.song_id2name = pickle.load(open(songs_file, 'rb'), encoding='utf8')
        song_name2id = {}
        for song_id in self.song_id2name:
            song_name2id[self.song_id2name[song_id]] = song_id
        print('完成歌曲名和id之间的映射关系')

    def get_name_by_index(self, index):
        return list(self.playlist_name2id.keys())[index]

    def get_name_by_rid(self, rid):
        return self.playlist_id2name[rid]

    def get_rid_by_name(self, name):
        return self.playlist_name2id[name]

    def get_song_name_by_iid(self, iid):
        return self.song_id2name[iid]

class FileHelper(object):
    def __init__(self, json_file, txt_file, formated_txt):
        self.json_file = json_file
        self.txt_file = txt_file
        self.formated_txt = formated_txt

    # txt文件转换成pkl文件
    def txt2pkl(self, in_file, out_playlist, out_song):
        if in_file is None:
            in_file = self.txt_file
        if not os.path.exists(in_file):
            raise FileNotFoundError('{} not found'.format(in_file))

        playlist_dict = {}
        song_dict = {}
        if not os.path.exists(self.txt_file):
            raise FileNotFoundError("{} not exist".format(self.txt_file))

        def parse_playlist_get_info(in_line, playlist_dict, song_dict):
            contents = in_line.strip().split('\t')
            name, tags, playlist_id, subscribed_count = contents[0].split('##')
            playlist_dict[playlist_id] = name
            for song in contents[1:]:
                try:
                    song_id, song_name, artist = song.split(':::')
                    song_dict[song_id] = song_name + '\t' + artist

                except Exception as e:
                    print('song format error')

        for line in open(in_file):
            parse_playlist_get_info(line, playlist_dict, song_dict)
            pickle.dump(playlist_dict, open(out_playlist, 'wb'))
            pickle.dump(song_dict, open(out_song, 'wb'))

    # json格式的文件转换成普通文本文件
    def json2txt(self, in_file = None, out_file = None):
        if in_file is None:
            in_file = self.json_file
        if out_file is None:
            out_file = self.txt_file
        if not os.path.exists(in_file):
            raise FileNotFoundError('{} not found'.format(in_file))
        out = open(out_file, 'w')

        def parse_song_line(line):
            data = json.loads(line)
            name = data['result']['name']
            tags = ','.join(data['result']['tags'])
            subscribed_count = data['result']['subscribedCount']
            # some data in '万', so just go on
            if '万' not in subscribed_count and int(subscribed_count) < 100:
                return False
            playlist_id = data['result']['id']
            song_info = ''
            songs = data['result']['tracks']
            for song in songs:
                try:
                    song_info += '\t' + ':::'.join(
                        [str(song['id']), song['name'], song['artists'][0]['name']])
                except Exception as e:
                    continue

            return name + '##' + tags + '##' + str(playlist_id) + '##' + str(subscribed_count) + song_info

        for line in open(in_file):
            result = parse_song_line(line)
            if result:
                out.write(result.strip().encode('gbk', 'ignore').decode('gbk', 'ignore')+"\n")
        out.close()

    # 普通文本文件转换成surprise特定的数据格式 user item rating timestamp
    def txt2surprise_txt(self, in_file = None, out_file = None):
        if in_file is None:
            in_file = self.txt_file
        if out_file is None:
            out_file = self.formated_txt

        if not os.path.exists(in_file):
            raise FileNotFoundError('{} not found'.format(in_file))

        out_f = open(out_file, 'w')

        def process_song_info(song_info):
            try:
                song_id, name, artist = song_info.split(':::')
                return ','.join([song_id, '1.0', '1300000'])
            except Exception as e:
                return ''

        def process_playlist_line(in_line):
            try:
                contents = in_line.strip().split('\t')
                name, tags, playlist_id, subscribed_count = contents[0].split('##')
                songs_info = map(lambda x: playlist_id + ',' + process_song_info(x), contents[1:])
                songs_info = filter(is_null, songs_info)
                return '\n'.join(songs_info)
            except Exception as e:
                print(e)
                return False

        for line in open(in_file):
            result = process_playlist_line(line)
            if result:
                out_f.write(result.strip() + '\n')
        out_f.close()

if __name__=='__main__':
    fileHelper = FileHelper(json_file, txt_file, formated_file)
    fileHelper.json2txt()
    fileHelper.txt2surprise_txt(txt_file, formated_file)
    fileHelper.txt2pkl(txt_file, playlist_file, songs_file)