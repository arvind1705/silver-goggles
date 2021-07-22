
import django_filters
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import ListView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from fampay.mock_data import mock_data
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

    data = {"message": "Mock data inserted."}
    return Response(data, status=HTTP_200_OK)


class YoutubeVideoFilter(django_filters.FilterSet):
    class Meta:
        model = YoutubeVideo
        fields = {"video_title": ["icontains"],
                  "video_description": ["icontains"]}


class FilteredYoutubeVideoView(SingleTableMixin, FilterView):
    model = YoutubeVideo
    template_name = "video_list.html"
    filterset_class = YoutubeVideoFilter
