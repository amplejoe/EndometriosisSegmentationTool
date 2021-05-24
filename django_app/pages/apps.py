from django.apps import AppConfig
from endo_seg.EndoSegPredictor import EndoSegPredictor
from endo_seg import utils
import threading
import time
import random
import tqdm
from django.conf import settings

MODEL_DIR = "./django_app/media/models"
VIDEO_EXT = [".mp4", ".avi", ".mov"]
MODEL_EXT = [".pth"]
CFG_EXT = [".yaml"]


def segmentation_process(id):
    print(f"seg_process {id}: start")
    results_root = utils.join_paths(settings.MEDIA_ROOT, "results")
    videos_root = utils.join_paths(settings.MEDIA_ROOT, "videos")
    models_root = utils.join_paths(settings.MEDIA_ROOT, "models")
    while True:
        time.sleep(2)
        videos = utils.get_files(videos_root, *VIDEO_EXT)
        models = utils.get_files(models_root, *MODEL_EXT)

        ep = EndoSegPredictor(
            videos=videos,
            models=models,
            video_root=videos_root,
            output_root=results_root,
        )
        if ep.is_work_needed():
            ep.run_predictions(print_info=False, confirm_overwrite = False)
            tqdm.write(f"seg_process {id}: processing finished!")


class PagesConfig(AppConfig):
    name = "pages"
    verbose_name = "Endometriosis Segmentation Tool"
    seg_models = []
    cur_model = 0

    # executed once and first in the application
    def ready(self):
        # get models and cfgs
        model_dirs = utils.get_subdirs(MODEL_DIR)
        for i, md in enumerate(model_dirs):
            model_file = utils.get_files(md, *MODEL_EXT)
            cfg_file = utils.get_files(md, *CFG_EXT)
            if len(model_file) < 1 or len(cfg_file) < 1:
                continue
            model_file = model_file[0]
            cfg_file = cfg_file[0]
            selected = False
            if i == 0:
                selected = True
            model = {
                "id": i,
                "name": utils.get_file_name(model_file),
                "model": model_file,
                "cfg": cfg_file,
                "selected": selected,
            }
            self.seg_models.append(model)

        id = random.randint(1, 100)
        t = threading.Thread(target=segmentation_process, args=(id,), kwargs={})
        t.setDaemon(True)
        t.start()

        print(
            "--------------------------- Startup complete! ---------------------------"
        )
