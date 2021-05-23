from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Video
from endo_seg import EndoSegPredictor
from pages.apps import PagesConfig as pg_config

# from django.conf import settings


# Create your views here.
def home_view(request, *args, **kwargs):

    # upload new video
    if request.method == "POST":

        title = request.POST.get("title")
        # video = request.POST.get("video")
        video = request.FILES["video"]
        if len(title) == 0:
            title = video.name

        content = Video(title=title, video=video)
        print("saving video")
        # print(title)
        # print(video.name)
        # print(video.size)
        # print(request.FILES['video'])
        content.save()
        return redirect("home")

    # TODO: add to dropdown list & select current model
    print(pg_config.seg_models)

    # all uploaded videos
    videos = Video.objects.all()
    context = {
        "videos": videos,
    }

    return render(request, "home.html", context)


def instructions_view(request, *args, **kwargs):
    return render(request, "instructions.html", {})


def about_view(request, *args, **kwargs):
    return render(request, "about.html", {})