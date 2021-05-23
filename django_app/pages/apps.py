from django.apps import AppConfig
from endo_seg import utils

MODEL_EXT = [".pth"]
CFG_EXT = [".yaml"]
MODEL_DIR = "./django_app/media/models"


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
            model = {"id": i, "name": utils.get_file_name(model_file), "model": model_file, "cfg": cfg_file}
            self.seg_models.append(model)

        print(
            "--------------------------- Startup complete! ---------------------------"
        )

