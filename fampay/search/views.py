
from django.db.models import Q

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
    # Fetch all YT video data sorted in descending order of published datetime.
    youtube_video_objects = YoutubeVideo.objects.all().order_by(
        '-publishing_datetime').values()
    result_page = paginator.paginate_queryset(youtube_video_objects, request)

    return paginator.get_paginated_response(result_page)


@api_view(["GET"])
def search_youtube_videos(request, *args, **kwargs):
    """GET API to search the stored video data based on title and desciption.

    @param request: http request object

    @return: json object containing search string in title or description along with current and next page data.
    """
    search_string = request.GET.get('q')

    if search_string:
        # Django ORM to filter videos by given search string and sort them based on publishing datetime.
        youtube_video_objects = YoutubeVideo.objects.filter(Q(video_title__contains=search_string) | Q(
            video_description__contains=search_string)).order_by('-publishing_datetime').values()

        paginator = PageNumberPagination()
        paginator.page_size = 5

        result_page = paginator.paginate_queryset(
            youtube_video_objects, request)
        response = paginator.get_paginated_response(result_page)
    else:
        # return message to user when query params is not passed.
        data = {"message": "Please pass query params at the end of like this /search/?q=keyword."}
        response = Response(data, status=HTTP_200_OK)

    return response
