import datetime
import sys
import os
import argparse
import requests

from mutagen.easyid3 import EasyID3
import youtube_dl
import pydub

opts_song = {
    'format': 'bestaudio/best',
    'default-search': 'ytsearch',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': 'song.%(ext)s'
    }

ydl = youtube_dl.YoutubeDL(opts_song)

parser = argparse.ArgumentParser()
parser.add_argument('--url', help='url to be downloaded')
parser.add_argument('--meta', help='path to metadata file')
parser.add_argument('--local', help='path to local mp3 to cut up')
parser.add_argument('--cover', help='path to image for cover art')
args = parser.parse_args()


def parse_timestamp(data):
    times = [0]*(3-len(data)) + data    #golfing it
    times = [int(x) for x in times]
    if times:
        return times
    else:
        raise ValueError("Timestamp not in correct format. (HH:MM:SS)")

def sanitise(text):
    return "".join(e for e in text if e.isalnum())


if not args.meta:
    raise argparse.error("Must include metadata file")

metadata = []

with open(args.meta, "r", encoding='utf8') as metadata_file:
    for num, content in enumerate(metadata_file):
        line = content.strip("\r\n")
        if num == 0:
            album_name = line
        elif num == 1:
            artist_name = line
        else:
            try:
                timestamp, title = line.split("-", 1)
                parse_timestamp(timestamp.split(":"))
                metadata.append([timestamp, title])
            except ValueError:
                print("Metadata file in wrong format (HH:MM:SS-Title)")
                sys.exit(1)


if args.url and args.local:
    raise argparse.error("Only include one source")

elif args.url:
    ydl.download([args.url])
    info = ydl.extract_info(args.url, download=False)
   
    video = "song.mp3"
    video_title = sanitise(info['title'])
    thumbnail_data = requests.get(info["thumbnail"]).content
    with open('{}.jpg'.format(video_title), 'wb') as handler:
        handler.write(thumbnail_data)
    if not args.cover:
        thumbnail_path = '{}.jpg'.format(video_title)
   
elif args.local:
    video = args.local
    video_title = os.path.splitext(args.local)[0]
    thumbnail_path = args.cover
    
else:
   raise argparse.error("Give a source file with either --url <url> or --local <path/to/file.mp3>")

if not os.path.exists(video_title):
    os.makedirs(video_title)


video = pydub.AudioSegment.from_mp3("song.mp3")

for x, data in enumerate(metadata):
    hr,mins,sec = parse_timestamp(data[0].split(":"))
    start = datetime.timedelta(hours=hr, minutes=mins, seconds=sec)
    try:
        hr,mins,sec = parse_timestamp(metadata[x+1][0].split(":"))
        end = datetime.timedelta(hours=hr, minutes=mins, seconds=sec)
        song = video[(start.seconds*1000):(end.seconds*1000)]
    except IndexError:
        song = video[(start.seconds*1000):]
    song_path = "{}/{}.mp3".format(video_title, sanitise(data[1]))
    if thumbnail_path:
        song.export(song_path, format="mp3", cover=thumbnail_path)
    else:
        song.export(song_path, format="mp3")
    tag_audio = EasyID3(song_path)
    tag_audio["title"] = data[1]
    tag_audio["album"] = album_name
    tag_audio["artist"] = artist_name
    tag_audio["tracknumber"] = str(x+1)
    tag_audio.save()


os.remove("song.mp3")
os.remove(thumbnail_path)
print("done")
