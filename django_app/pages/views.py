from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Video
from endo_seg import EndoSegPredictor

# from django.conf import settings
# from externals.apps.test_ing_file import *

# from django.apps import testIngF

# import EXTERNAL_APPS_PATH.test_ing_file


# Create your views here.
def home_view(request, *args, **kwargs):

    print("----------------------------------")
    print(EndoSegPredictor)
    print(request)

    # upload new video
    if request.method == "POST":

        title = request.POST.get("title")
        # video = request.POST.get("video")
        video = request.FILES["video"]

        content = Video(title=title, video=video)
        print("saving video")
        print(title)
        # print(video)
        # print(settings.MEDIA_URL)
        # print(settings.MEDIA_ROOT)
        print(video.name)
        print(video.size)
        # print(request.FILES['video'])
        content.save()
        return redirect("home")

    # all uploaded videos
    videos = Video.objects.all()
    context = {
        "videos": videos,
    }

    print("----------------------------------")
    return render(request, "home.html", context)


def instructions_view(request, *args, **kwargs):
    return render(request, "instructions.html", {})


def about_view(request, *args, **kwargs):
    return render(request, "about.html", {})