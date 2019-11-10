import os
import time
import requests

import pandas as pd


API_KEY = 'AIzaSyCDCjl6U2Mgmu-7Jf4jDxRMj-E4c-_rCmU'
CHANNEL_ID = 'UCCUR--YxwSYJ4QzuKsaAABw'

base_url = 'https://www.googleapis.com/youtube/v3'
url = base_url + '/search?key=%s&channelId=%s&part=snippet,id&order=date&maxResults=50'
infos = []

# while True:
#     time.sleep(30)
#     response = requests.get(url % (API_KEY, CHANNEL_ID))
#     if response.status_code != 200:
#         print('エラーで終わり')
#         break
#     result = response.json()
#     infos.extend([
#         [item['id']['videoId'], item['snippet']['title'], item['snippet']['description'], item['snippet']['publishedAt']]
#         for item in result['items'] if item['id']['kind'] == 'youtube#video'
#     ])

#     if 'nextPageToken' in result.keys():
#         if 'pageToken' in url:
#             url = url.split('&pageToken')[0]
#         url += f'&pageToken={result["nextPageToken"]}'
#     else:
#         print('正常終了')
#         break

response = requests.get(url % (API_KEY, CHANNEL_ID))
if response.status_code != 200:
    print('エラーで終わり')
result = response.json()
infos.extend([
    [item['id']['videoId'], item['snippet']['title'], item['snippet']['description'], item['snippet']['publishedAt']]
    for item in result['items'] if item['id']['kind'] == 'youtube#video'
])


# if 'nextPageToken' in result.keys():
#     if 'pageToken' in url:
#         url = url.split('&pageToken')[0]
#     url += f'&pageToken={result["nextPageToken"]}'
# else:
#     print('正常終了')
#     break

videos = pd.DataFrame(infos, columns=['videoId', 'title', 'description', 'publishedAt'])
videos.to_csv('videos.csv', index=None)