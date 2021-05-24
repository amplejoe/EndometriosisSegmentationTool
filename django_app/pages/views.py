from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Video
from pages.apps import PagesConfig as pg_config
import json
from endo_seg import utils
from django.conf import settings


VIDEO_EXT = [".mp4", ".avi", ".mov"]


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
    # return render(request, 'home.html', {})
    # return redirect("home")


def get_results():
    results_root = utils.join_paths(settings.MEDIA_ROOT, "results")
    vids = utils.get_files(results_root, *VIDEO_EXT)
    return [v for v in vids if "_indicated" in v]


def get_selected_model():
    for m in pg_config.seg_models:
        if m["selected"]:
            return m


def refresh_model():
    videos = Video.objects.all()
    results = get_results()
    model = get_selected_model()
    model_name = model["name"]
    results_for_model = [r for r in results if model_name in r]
    for v in videos:
        v_name = utils.get_file_name(v.video.url)
        v_ext = utils.get_file_ext(v.video.url)
        result_file_needed = f"{model_name}_{v_name}_indicated{v_ext}"
        for r in results_for_model:
            r_file = utils.get_file_name(r, True)
            if result_file_needed == r_file:
                # set result
                relative_result_path = "/media/" + utils.path_to_relative_path(
                    r, settings.MEDIA_ROOT
                )
                Video.objects.filter(video=v.video).update(result=relative_result_path)
                # alternative
                # setattr(v, "result", relative_result_path)
                # v.save()
                break


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

    # set result models according to selection
    refresh_model()

    # all uploaded videos
    videos = Video.objects.all()

    context = {"videos": videos, "models": pg_config.seg_models}

    print("should render!!")
    return render(request, "home.html", context)


def instructions_view(request, *args, **kwargs):
    return render(request, "instructions.html", {})


def about_view(request, *args, **kwargs):
    return render(request, "about.html", {})