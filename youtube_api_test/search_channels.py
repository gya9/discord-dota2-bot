import os
from easydict import EasyDict as edict
from apiclient.discovery import build
from apiclient.errors import HttpError

API_KEY = 'AIzaSyCDCjl6U2Mgmu-7Jf4jDxRMj-E4c-_rCmU'

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)

opt = edict()
opt.q = 'dota2 pro'
opt.max_results = 25

search_response = youtube.search().list(
    q=opt.q,
    part="id,snippet",
    maxResults=opt.max_results
).execute()

channels = []

for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#channel":
        channels.append("%s (%s)" % (search_result["snippet"]["title"],
                                   search_result["id"]["channelId"]))

print("Channels:\n", "\n".join(channels), "\n")