from fastapi import FastAPI
from googleapiclient.discovery import build
import requests

import config 

import datetime

app = FastAPI()


# API権限の取得
api_service_name = 'youtube'
api_version = 'v3'
DEVELOPER_KEY = config.DEVELOPER_KEY

# 時間の設定
date = datetime.datetime.now().strftime("%Y/%m/%d")

# インスタンスの作成
youtube = build(api_service_name,api_version,developerKey= DEVELOPER_KEY)

# ビデオのIDを返す
def video_ids(playlistId):
  # playlist_id = 'PLSFrP_aW8LfyEIahQGnpdvDtPUKKWxi-H'
  playlist_id = playlistId
  playlist_ids = []
  playlist = youtube.playlistItems().list(
    playlistId=playlist_id,
    part='snippet',
    fields="nextPageToken,items/snippet/resourceId/videoId",
    maxResults=50
  )

  while playlist:
    results = playlist.execute()
    items = results.get('items')
    for ids in items:
      playlist_ids.append(ids.get('snippet').get('resourceId').get('videoId'))
    playlist = youtube.playlistItems().list_next(playlist,results)
  
  params = {
      'key': DEVELOPER_KEY,
      'type': 'playlist',
      'part': 'snippet',
      'q': playlistId,
  }
  response = requests.get('https://www.googleapis.com/youtube/v3/search', params=params)
  title = response.json().get("items")[0].get("snippet").get("title")
  return list(set(playlist_ids)),title

# 50個づつリストを区切ってジェネレート
def chunk(lst,n):
  for i in range(0,len(lst),n):
    yield lst[i:i+n]

# ビデオのタイトルとIDごとに辞書にしたjsonを返す
def video_titles(playlist_ids_):
  music_dict = {
    "datetime":date,
    "playlistname":playlist_ids_[-1],
    "music_id_list":None
  }
  video_list = list(chunk(playlist_ids_[0],50))
  list_video = []
  for vide in video_list:
    video = ",".join(vide)
    r = youtube.videos().list(
      part='snippet',
      id=video,
      fields='items/snippet/title'
    )
    res = r.execute()
    for points in res.get('items'):
      _ = points.get('snippet').get('title')
      list_video.append(_)

  video_tuple = list(map(tuple,zip(playlist_ids_[0],list_video)))
  corpas = [{"video_name":data[1],"video_id":data[0]} for data in video_tuple]
  music_dict["music_id_list"]=corpas
  
  return music_dict


# @app.get("/")
# def send_playlist():
#   # return json.dumps(video_titles(video_ids()),ensure_ascii=False)
#   return video_titles(video_ids())

@app.post("/{playlistId}")
async def post_playlist(playlistId):
  return video_titles(video_ids(playlistId))

