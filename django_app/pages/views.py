from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .models import Video
from pages.apps import PagesConfig as pg_config
import json
from endo_seg import utils
from django.conf import settings
from django.contrib import messages


VIDEO_EXT = [".mp4", ".avi", ".mov", ".webm"]
RESULT_EXT = ".webm"


def handle_upload(request):
    title = request.POST.get("title")
    # video = request.POST.get("video")
    video = request.FILES["video"]
    if len(title) == 0:
        title = video.name

    content = Video(title=title, video=video)
    print("saving video")
    content.save()
    # messages.success(request, 'Success!')
    # return HttpResponseRedirect(request.path)
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
    return None


def get_videos():
    videos = Video.objects.all()
    results = get_results()
    model = get_selected_model()

    if model == None:
        return videos

    model_name = model["name"]
    results_for_model = [r for r in results if model_name in r]
    # update video results according to selected model
    for v in videos:
        v_name = utils.get_file_name(v.video.url)
        # v_ext = utils.get_file_ext(v.video.url)
        result_file_needed = f"{model_name}_{v_name}_indicated{RESULT_EXT}"
        # clear current result
        Video.objects.filter(video=v.video).update(result="")
        for r in results_for_model:
            r_file = utils.get_file_name(r, True)
            if result_file_needed == r_file:
                # set result
                relative_result_path = "/media/" + utils.path_to_relative_path(
                    r, settings.MEDIA_ROOT
                )
                # alternative: update database (expensive for many videos)
                # Video.objects.filter(video=v.video).update(result=relative_result_path)

                # set current result
                setattr(v, "result", relative_result_path)
                # omit saving to db as this change is temporary
                # v.save()
                break
    return videos


# Create your views here.
def home_view(request, *args, **kwargs):

    # upload new video
    if request.method == "POST":
        type = request.POST.get("type")
        print(request.POST)

        if type == "upload":
            return handle_upload(request)
        else:
            data = json.loads(request.body.decode("utf-8"))
            if data["type"] == "model":
                handle_model(data)

    # all uploaded videos
    videos = get_videos()
    print(videos)

    context = {"videos": videos, "models": pg_config.seg_models}
    return render(request, "home.html", context)


def instructions_view(request, *args, **kwargs):
    return render(request, "instructions.html", {})


def about_view(request, *args, **kwargs):
    return render(request, "about.html", {})
