# Keypoint Tracking
Command-line tool to display videos and record the position of the mouse.

## Install
Install [anaconda](https://www.anaconda.com/products/individual), download this repository and go to the new folder.

Inside the new folder create the new environment:
```bash
conda env create -f environment.yml
```

Activate the new environment:
```bash
conda activate kp_ann_gui
```

## Use

```bash
python annotate_keypoints_video_wx.py path_to_file
```

Replace `path_to_file` with the path of the file you want to analyze.

Once the video is playing, you can use the `Space` key to pause/play the video, and `Esc` to exit the program.
The output is saved in `output.csv`

You can specify the name of the output file with the `--output` argument
