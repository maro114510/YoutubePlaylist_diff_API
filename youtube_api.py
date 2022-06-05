from googleapiclient.discovery import build

from youtuber.config import DEVELOPER_KEY

import datetime

# API権限の取得
api_service_name = 'youtube'
api_version = 'v3'
DEVELOPER_KEY = DEVELOPER_KEY
# 時間の設定
date = datetime.datetime.now().strftime("%Y/%m/%d")

# インスタンスの作成
youtube = build(api_service_name,api_version,developerKey= DEVELOPER_KEY)

# ビデオのIDを返す
def video_ids():
  playlist_id = 'PLSFrP_aW8LfyEIahQGnpdvDtPUKKWxi-H'
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
  
  return list(set(playlist_ids))

# 50個づつリストを区切ってイミュレート
def chunk(lst,n):
  for i in range(0,len(lst),n):
    yield lst[i:i+n]

# ビデオのタイトルとIDごとに辞書にしたjsonを返す
def video_titles(playlist_ids_):
  music_dict = {
    "datetime":date,
    "music_id_list":None
  }
  video_list = list(chunk(playlist_ids_,50))
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
  video_tuple = list(map(tuple,zip(playlist_ids_,list_video)))
  corpas = [{"video_name":data[1],"video_id":data[0]} for data in video_tuple]
  music_dict["music_id_list"]=corpas
  
  return music_dict



if __name__=='__main__':
    print(video_titles(video_ids()))