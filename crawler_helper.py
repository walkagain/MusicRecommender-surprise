# -*- coding:utf8 -*-
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import csv
import json
import sys

from config import start_url, playlist_urls, json_file, subscribe_playlist_urls, all_playlist_urls

def get_webdriver(browser_type='firefox', executable_path=None):
    '''
    :param browser_type: browser, only firefox and chrome optional
    :param executable_path: browser executable file path
    :return: a web driver object
    '''

    if browser_type=='chrome':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        return webdriver.Chrome(chrome_options=chrome_options, executable_path=executable_path \
            if executable_path else 'chromedriver')
    else:
        firefox_options = webdriver.FirefoxOptions()
        firefox_options.add_argument('--headless')
        return webdriver.Firefox(firefox_options=firefox_options, executable_path=executable_path \
            if executable_path else 'geckodriver')


def get_playlist_urls_by_playCount(driver, start_url, out_file=playlist_urls, play_num=400):
    '''
    :param driver: webdriver for firefox or chrome
    :param start_url: start page to crawl
    :param play_num: played times of a playlist in ten thousands
    :return: None
    '''

    # prepare csv file to store urls
    csv_file = open(out_file, 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(['歌单名', '播放量', '链接地址'])

    url = start_url
    while url != 'javascript:void(0)':
        driver.get(url)
        driver.switch_to.frame('contentFrame')
        data = driver.find_element_by_id('m-pl-container').find_elements_by_tag_name('li')

        for i in range(len(data)):
            nb = data[i].find_element_by_class_name('nb').text
            if '万' in nb and int(nb.split('万')[0]) >= play_num:
                msk = data[i].find_element_by_css_selector('a.msk')

                # solve "gbk codec can't encode character '\xa0'" error
                title = msk.get_attribute('title').encode('gbk', 'ignore').decode('gbk', 'ignore')
                writer.writerow([title, nb, msk.get_attribute('href')])

        # next page url
        url = driver.find_element_by_css_selector('a.zbtn.znxt').get_attribute('href')
    csv_file.close()

def get_all_playlist_urls(driver, start_url, out_file=all_playlist_urls):
    '''
    :param driver:webdriver for firefox or chrome
    :param start_url:start page to crawl
    :param out_file: file to store playlist urls
    :return: None
    '''
    csv_file = open(out_file, 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(['歌单名', '播放量' '链接地址'])

    url = start_url
    while url != 'javascript:void(0)':
        driver.get(url)
        # print(url)
        driver.switch_to.frame('contentFrame')
        data = driver.find_element_by_id('m-pl-container').find_elements_by_tag_name('li')
        for i in range(len(data)):
            msk = data[i].find_element_by_css_selector('a.msk')
            sub_url = msk.get_attribute('href')

            # solve "gbk codec can't encode character '\xa0'" error
            title = msk.get_attribute('title').replace(',', '. ').encode('gbk', 'ignore').decode('gbk', 'ignore')
            nb = data[i].find_element_by_class_name('nb').text
            writer.writerow([title, nb, sub_url])

        # next page url
        url = driver.find_element_by_css_selector('a.zbtn.znxt').get_attribute('href')

    csv_file.close()

def get_playlist_urls_by_subcribedCount(driver, urls_file=all_playlist_urls, out_file=subscribe_playlist_urls, subscribed_count=400):
    '''
    :param driver: webdriver for firefox or chrome
    :param start_url: start page to crawl
    :param subscribed_count: subscribed count  of a playlist in ten thousands
    :return: None
    '''
    csv_file = open(out_file, 'w', newline='')
    writer = csv.writer(csv_file)
    writer.writerow(['歌单名', '收藏量', '链接地址'])

    lines = open(urls_file, 'r')
    # skip first line
    next(lines)
    for line in lines:
        title, nb, url = line.strip('\n').split(',')
        # print("title:{}, nb:{}, url:{}".format(title, nb, url))
        try:
            driver.get(url)
        except:
            continue

        driver.switch_to.frame('contentFrame')
        subCount = driver.find_element_by_xpath("//*[@id=\"m-playlist\"]").\
            find_element_by_xpath("//*[@id=\"content-operation\"]").\
            find_element_by_xpath('//a[3]/i').text.strip('()')

        if '万' in subCount and int(subCount.split('万')[0]) >= subscribed_count:
            writer.writerow([title, subCount, url])
    csv_file.close()

def parse_playlist_info(driver, playlist_url):
    '''
    :param driver: selenium webdriver
    :param playlist_url: playlist url to crawl
    :return: playlist info in dict
    '''

    result = {}
    result['id'] = playlist_url.split('=')[-1].replace('\n', '')

    driver.get(playlist_url)
    driver.switch_to.frame("contentFrame")
    data = driver.find_element_by_xpath("//*[@id=\"m-playlist\"]")
    playlistInfo = data.find_element_by_class_name("m-info.f-cb")
    result['name'] = playlistInfo.find_element_by_class_name('f-ff2.f-brk').text
    userInfo = playlistInfo.find_element_by_class_name('user.f-cb').find_element_by_css_selector('a.s-fc7')
    result['userName'] = userInfo.text
    result['userUrl'] = userInfo.get_attribute('href')
    result['userId'] = result['userUrl'].split('=')[-1]
    result['create_time'] = playlistInfo.find_element_by_class_name('user.f-cb').\
        find_element_by_class_name('time.s-fc4').text.split(' ')[0]

    operInfo = data.find_element_by_xpath("//*[@id=\"content-operation\"]")
    result['subscribedCount'] = operInfo.find_element_by_xpath('//a[3]/i').text.strip('()')

    result['shareCount'] = operInfo.find_element_by_css_selector('a.u-btni.u-btni-share').text.strip('()')
    result['commentCount'] = operInfo.find_element_by_css_selector('a.u-btni.u-btni-cmmt').text.strip('()')
    # some playlist without tags
    try:
        tags = data.find_element_by_class_name('tags.f-cb').find_elements_by_class_name('u-tag')
    except:
        tags = ""
    tagsList = []
    for tag in tags:
        tagsList.append(tag.text)
    result['tags'] = tagsList
    # it seems that some pages without this element
    try:
        result['description'] = data.find_element_by_id('album-desc-more').text.replace("介绍：", '').strip()
    except:
        result['description'] = ""

    songtb = data.find_element_by_class_name('n-songtb')
    result['trackCount'] = songtb.find_element_by_id('playlist-track-count').text
    result['playCount'] = songtb.find_element_by_id('play-count').text

    # print(result)
    # TODO, parse song info
    playlist_songs = songtb.find_element_by_class_name('m-table')
    song_rows = playlist_songs.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')

    tracks = []
    for row in song_rows:
        songInfo = {}
        # cols = row.find_elements_by_tag_name('td')

        # url, id, name, duration, artist, album
        songInfo['url'] = row.find_element_by_xpath('//td[2]/div/div/div/span/a').get_attribute('href')
        songInfo['id'] = songInfo['url'].split('=')[-1]
        songInfo['name'] = row.find_element_by_xpath('//td[2]/div/div/div/span/a/b').get_attribute('title')
        songInfo['duration'] = row.find_element_by_xpath('//td[3]/span').text

        artists = []
        artist = {}
        artist['name'] = row.find_element_by_xpath('//td[4]/div/span').get_attribute('title')
        artist['url'] = row.find_element_by_xpath('//td[4]/div/span/a').get_attribute('href')
        artist['id'] = artist['url'].split('=')[-1]
        artists.append(artist)
        songInfo['artists'] = artists

        album = {}
        album['name'] = row.find_element_by_xpath('//td[5]/div/a').get_attribute('title')
        album['url'] = row.find_element_by_xpath('//td[5]/div/a').get_attribute('href')
        album['id'] = album['url'].split('=')[-1]
        album['artists'] = artists
        songInfo['album'] = album
        tracks.append(songInfo)

    result["tracks"] = tracks
    return result

def get_playlist_detail(driver, playlist_urls_file, out_file):
    '''
    :param driver: selenium webdriver
    :param playlist_urls_file: file path of playlist urls
    :param out_file: file to store json data
    :return: None
    '''

    f = open(out_file, 'w')
    lines = open(playlist_urls_file)
    # skip first line
    next(lines)

    playlist = {}
    for line in lines:
        url = line.split(',')[2]
        playlist['result'] = parse_playlist_info(driver, url)
        string_data = json.dumps(playlist) + '\n'
        f.write(string_data)
    f.close()

if __name__ == '__main__':
    driver = get_webdriver()
    get_playlist_urls_by_playCount(driver, start_url, playlist_urls, 400)
    get_playlist_detail(driver, playlist_urls, json_file)

    # get_all_playlist_urls(driver, start_url, all_playlist_urls)
    # get_playlist_urls_by_subcribedCount(driver, all_playlist_urls, subscribe_playlist_urls, 10)