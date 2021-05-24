from django.db import models

# Create your models here.


class Video(models.Model):
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to="videos/")
    # result = models.FileField()

    class Meta:
        verbose_name = "video"
        verbose_name_plural = "videos"

    def __str__(self):
        return self.title
