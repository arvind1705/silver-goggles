
import asyncio
import os
from datetime import datetime, timedelta

import django
import googleapiclient.discovery

from django.conf import settings

from decouple import config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fampay.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

settings.configure(
    DATABASES={
        'default': {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": config('DB_NAME'),
            "USER": config('DB_USER'),
            "PASSWORD": config('DB_PASSWORD'),
            "HOST": config('DB_HOST'),
            "PORT": '5432',
        }
    }, INSTALLED_APPS=[
        'fampay.search',
    ]
)

django.setup()

# from fampay.mock_data import mock_data
from fampay.search.models import ThumbnailURL, YoutubeVideo
from fampay.settings import GOOGLE_DEVELOPER_KEY

async def periodic_youtube_task():
    """Asynchronous function which runs in defined interval with predefined params to fetch
    data from Youtube API and inserts it to DB

    """
    while True:
        print('Periodic Youtube Cron Task')

        # Sleep for 1 hour. Update frequency if required. Make sure API quota is available.
        await asyncio.sleep(3)

        api_service_name = "youtube"
        api_version = "v3"
        api_access_key = GOOGLE_DEVELOPER_KEY

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
