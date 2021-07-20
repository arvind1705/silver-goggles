
import asyncio
import os
from datetime import datetime, timedelta

import django
import googleapiclient.discovery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fampay.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

django.setup()

from fampay.search.models import ThumbnailURL, YoutubeVideo
from fampay.settings import DEVELOPER_KEY


async def periodic_youtube_task():
    while True:
        print('Periodic Youtube Cron Task')

        # Sleep for 1 hour. Update frequency if required. Make sure API quota is available.
        await asyncio.sleep(3600)

        api_service_name = "youtube"
        api_version = "v3"
        api_access_key = DEVELOPER_KEY

        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=api_access_key)

        # Fetching latest information which wasn't fetched earlier.
        published_time = datetime.now() - timedelta(hours=1)

        # Youtube api client to search for predefined params
        request = youtube.search().list(
            part="id, snippet",
            publishedAfter=published_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            maxResults=200,
            order="date",
            q="Playstation 5",
            regionCode="IN",
            relevanceLanguage="en",
            type="video"
        )
        response = request.execute()

        # Insert video data in to tables
        for video in response.get('items'):
            video_snippet = video['snippet']
            video_thumbnails = video_snippet['thumbnails']
            youtube_video, created = YoutubeVideo.objects.get_or_create(video_id=video['id']['videoId'], video_title=video_snippet['title'],
                                                                        video_description=video_snippet['description'], publishing_datetime=video_snippet['publishedAt'])
            youtube_video.save()
            
            # thumbnail is updated only if video information is inserted.
            if created:
                for res_type, thumnail_data in video_thumbnails.items():
                    _ = ThumbnailURL(
                        url=thumnail_data['url'], resolution_type=res_type, yt_video=youtube_video).save()


loop = asyncio.get_event_loop()
task = loop.create_task(periodic_youtube_task())

try:
    loop.run_until_complete(task)
except asyncio.CancelledError:
    pass
