from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Video
from endo_seg import EndoSegPredictor
from pages.apps import PagesConfig as pg_config
import json

# from django.conf import settings


def handle_upload(request):
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


def handle_model(data):
    for m in pg_config.seg_models:
        m["selected"] = False
        if int(data["selectID"]) == m["id"]:
            m["selected"] = True
    return redirect("home")


# Create your views here.
def home_view(request, *args, **kwargs):

    # upload new video
    if request.method == "POST":
        type = request.POST.get("type")

        if type == "upload":
            handle_upload(request)
        else:
            data = json.loads(request.body.decode("utf-8"))
            if data["type"] == "model":
                handle_model(data)

    # TODO: add to dropdown list & select current model
    # print(pg_config.seg_models)

    # all uploaded videos
    videos = Video.objects.all()
    context = {"videos": videos, "models": pg_config.seg_models}

    # for v in videos:
    #     print(v)

    return render(request, "home.html", context)


def instructions_view(request, *args, **kwargs):
    return render(request, "instructions.html", {})


def about_view(request, *args, **kwargs):
    return render(request, "about.html", {})