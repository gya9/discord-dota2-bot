import os
import time
import requests
import pickle

import pandas as pd
import datetime as dt


def search_videos():
    f = open("./hero_name.txt","rb")
    hero_name = pickle.load(f)

    JST = dt.timezone(dt.timedelta(hours=+9), 'JST')

    API_KEY = 'AIzaSyCDCjl6U2Mgmu-7Jf4jDxRMj-E4c-_rCmU'

    infos = []

    # dota 2 pro
    infos_tmp = []

    CHANNEL_ID = 'UCCUR--YxwSYJ4QzuKsaAABw'

    base_url = 'https://www.googleapis.com/youtube/v3'
    url = base_url + '/search?key=%s&channelId=%s&part=snippet,id&order=date&maxResults=50'

    response = requests.get(url % (API_KEY, CHANNEL_ID))
    if response.status_code != 200:
        print('エラーで終わり')
    result = response.json()

    infos_tmp.extend([
        [item['id']['videoId'], item['snippet']['title'], item['snippet']['publishedAt']]
        for item in result['items'] if item['id']['kind'] == 'youtube#video'
    ])

    for info in infos_tmp:
        test = info[1][info[1].find(' - ')+3:]
        for hero in hero_name:
            if test.startswith(hero):
                info.insert(2,hero)

    infos.extend(infos_tmp)


    # GoFlo GameShows
    infos_tmp = []

    CHANNEL_ID = 'UCgvWpZhaN-sdnJeYVtvbb4A'

    base_url = 'https://www.googleapis.com/youtube/v3'
    url = base_url + '/search?key=%s&channelId=%s&part=snippet,id&order=date&maxResults=50'

    response = requests.get(url % (API_KEY, CHANNEL_ID))
    if response.status_code != 200:
        print('エラーで終わり')
    result = response.json()

    infos_tmp.extend([
        [item['id']['videoId'], item['snippet']['title'], item['snippet']['publishedAt']]
        for item in result['items'] if item['id']['kind'] == 'youtube#video'
    ])

    for info in infos_tmp:
        test = info[1][info[1].find('plays')+6:]
        for hero in hero_name:
            if test.startswith(hero):
                info.insert(2,hero)

    infos.extend(infos_tmp)

    df_videos = pd.DataFrame(infos, columns=['videoId', 'title', 'hero', 'publishedAt'])
    df_videos = df_videos.dropna()
    df_videos.loc[:,'publishedAt'] = pd.to_datetime(df_videos.loc[:,'publishedAt'], utc=True)
    df_videos.index = pd.DatetimeIndex(df_videos.publishedAt ,name='publishedAt').tz_convert(JST)
    df_videos.publishedAt = df_videos.index
    df_videos = df_videos.reset_index(drop=True)

    dt_now = dt.datetime.now(JST)
    dt_1hb = dt_now - dt.timedelta(hours=1)

    df_1h = df_videos.query('@dt_1hb < publishedAt < @dt_now')

    return df_1h