# EndometriosisSegmentationTool

Tool for segmenting endometrial implants in laparoscopic surgery videos.

### Installation

**Pre-requisites**

- [Python 3.8.2](https://www.python.org/downloads/release/python-382/)

  Install on system or optionally create and activate virtual environment:

  - via [Anaconda](https://anaconda.org/)

    ```
    conda create --name EndometriosisSegmentationTool python=3.8.2
    conda activate EndometriosisSegmentationTool

    ```

  - via [Python](https://www.python.org/)

    ```
    python -m venv /path/to/virtual/envs/EndometriosisSegmentationTool
    source /path/to/virtual/envs/EndometriosisSegmentationTool/bin/activate
    ```

- [CUDA 10.2](https://developer.nvidia.com/cuda-10.2-download-archive) for capable [Nvidia GPUs](https://developer.nvidia.com/cuda-gpus) (optional)
  Follow installation instructions for your particular OS.
- [PyTorch>=1.6.0 and TorchVision>=0.7.0](https://pytorch.org/get-started/previous-versions/) (optionally for CUDA 10.1)
  - using conda:
    ```
    conda install pytorch==1.6.0 torchvision==0.7.0 cudatoolkit=10.2 -c pytorch
    ```
  - using pip:
    ```
    python -m pip install torch==1.6.0 torchvision==0.7.0
    ```
- [Detectron2 v0.4](https://github.com/facebookresearch/detectron2/releases/tag/v0.4)
  use pre-built files (Linux only) or extract to any folder and build:
  ```
  python -m pip install -e detectron2-0.4
  ```
  **Hint**: Although Windows 10 is not officially supported, building should work anyways. If problems occur, please refer to [https://github.com/conansherry/detectron2/issues/2](https://github.com/conansherry/detectron2/issues/2).
- Required Python packages
  ```
  python -m pip install -r requirements.txt
  ```

### Usage
```
python demo.py -h
```
```
usage: demo.py [-h] -i IN -m MODEL [-o OUT]

optional arguments:
  -h, --help            show this help message and exit
  -i IN, --in IN        path to video or input folder containing videos
  -m MODEL, --model MODEL
                        path to input model or root folder containing multiple model subfolders with their
                        respectie config.yaml files
  -o OUT, --out OUT     path to output folder (default: [IN_PATH]_out)
```

