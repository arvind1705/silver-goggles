
from django.db.models import Q
from rest_framework import response

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from rest_framework.pagination import PageNumberPagination

from .models import YoutubeVideo


# Create your views here.
@api_view(["GET"])
def get_youtube_videos(request):
    """GET API to return the stored video data in a paginated response sorted in descending
    order of published datetime.

    @param request: http request object

    @return: json object along with current and next page data.
    """
    paginator = PageNumberPagination()
    paginator.page_size = 5
    youtube_video_objects = YoutubeVideo.objects.all().order_by('-publishing_datetime').values()
    result_page = paginator.paginate_queryset(youtube_video_objects, request)

    return paginator.get_paginated_response(result_page)


