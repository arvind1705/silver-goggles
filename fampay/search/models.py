from django.db import models

# Create your models here.

class YoutubeVideo(models.Model):
    video_id = models.CharField(max_length=50, primary_key=True)
    video_title = models.CharField(max_length=1000, db_index=True)
    video_description = models.TextField(db_index=True)
    publishing_datetime = models.DateTimeField()
    inserted_at = models.DateTimeField(auto_now_add=True)


class ThumbnailURL(models.Model):
    url = models.URLField()
    resolution_type = models.CharField(max_length=10, choices=[
        ('default', 'Default'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ], default='default')
    yt_video = models.ForeignKey(YoutubeVideo, on_delete=models.CASCADE)
