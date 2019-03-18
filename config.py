# -*- coding:utf8 -*-

# 文件路径
data_dir = './data'
model_dir = './model'
json_file = data_dir + '/playlistdetail.all.json'
txt_file = data_dir + '/netease_music_playlist.txt'

playlist_file = data_dir + '/popular_playlist.pkl'
songs_file = data_dir + '/popular_song.pkl'

formated_file = data_dir + '/popular_music_surprise_format.txt'


# 网易云音乐歌单起始页面url
start_url = 'http://music.163.com/#/discover/playlist/?cat=%E5%85%A8%E9%83%A8&limit=35&offset=0'
playlist_urls = data_dir + '/playlist_filtered_by_playcount.csv'
subscribe_playlist_urls = data_dir + '/playlist_filtered_by_subcount.csv'
all_playlist_urls = data_dir + '/all_plsylist.csv'