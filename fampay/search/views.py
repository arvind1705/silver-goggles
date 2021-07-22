
import os
from datetime import datetime, timedelta

import django
import googleapiclient
import googleapiclient.discovery
from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from fampay.mock_data import mock_data
from fampay.settings import GOOGLE_DEVELOPER_KEY
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from .models import ThumbnailURL, YoutubeVideo

search_param = openapi.Parameter(
    'q', openapi.IN_QUERY, description="Search Param", type=openapi.TYPE_STRING)

# Create your views here.


@swagger_auto_schema(
    operation_description="GET Youtube Video information", methods=['get'], responses={200: 'Return the stored video data in a paginated response sorted in descending order of published datetime.'})
@api_view(["GET"])
def get_youtube_videos(request):
    """GET API to return the stored video data in a paginated response sorted in descending
    order of published datetime.

    @param request: http request object

    @return: json object along with current and next page data.
    """
    paginator = PageNumberPagination()
    paginator.page_size = 5
    # Fetch all YT video data sorted in descending order of published datetime.
    youtube_video_objects = YoutubeVideo.objects.all().order_by(
        '-publishing_datetime').values()
    result_page = paginator.paginate_queryset(youtube_video_objects, request)

    return paginator.get_paginated_response(result_page)


@swagger_auto_schema(
    operation_description="API to search the stored video data based on title and desciption.", methods=['get'], manual_parameters=[search_param],
    responses={200: 'Youtube video information containing search string in title or description along with current and next page data.'})
@api_view(["GET"])
def search_youtube_videos(request, *args, **kwargs):
    """GET API to search the stored video data based on title and desciption.

    @param request: http request object

    @return: json object containing search string in title or description along with current and next page data.
    """
    search_string = request.GET.get('q')

    if search_string:
        # Django ORM to filter videos by given search string and sort them based on publishing datetime.
        youtube_video_objects = YoutubeVideo.objects.filter(Q(video_title__icontains=search_string) | Q(
            video_description__icontains=search_string)).order_by('-publishing_datetime').values()

        paginator = PageNumberPagination()
        paginator.page_size = 5

        result_page = paginator.paginate_queryset(
            youtube_video_objects, request)
        response = paginator.get_paginated_response(result_page)
    else:
        # return message to user when query params is not passed.
        data = {
            "message": "Please pass query params at the end of like this /search/?q=keyword."}
        response = Response(data, status=HTTP_200_OK)

    return response


@swagger_auto_schema(
    operation_description="API to insert mock data.", methods=['get'], responses={200: 'Inserts mock data to database'})
@api_view(["GET"])
def insert_mock_data(request, *args, **kwargs):
    """GET API to insert mock data.

    @param request: http request object

    @return: json response message.
    """
    response = mock_data
    insert_data_to_models(response)

    data = {"message": "Mock data inserted."}
    return Response(data, status=HTTP_200_OK)


def insert_data_to_models(response):
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


@swagger_auto_schema(
    operation_description="API to insert mock data.", methods=['get'], responses={200: 'Inserts mock data to database'})
@api_view(["GET"])
def get_data_from_yt(request, *args, **kwargs):
    """GET API to fetch data from YT and insert to DB.

    @param request: http request object

    @return: json response message.
    """
    api_service_name = "youtube"
    api_version = "v3"
    api_access_key = GOOGLE_DEVELOPER_KEY
    try:
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
        insert_data_to_models(response)
        response_message = 'Fetched data from YT and inserted successfully'

    except googleapiclient.errors.HttpError as e:
        print('Please provide valid API Key. Hit /api/mock_data to insert mockdata incase you do not have api key')
        response_message = 'Please provide valid API Key. Hit /api/mock_data to insert mockdata incase you do not have api key'
    return Response({'message': response_message}, status=HTTP_200_OK)
