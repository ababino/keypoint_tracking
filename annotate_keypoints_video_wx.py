"""Keypoint Annotation GUI.

Example:
    python video.mp4 --skip 20

Author: Andres Babino <ababino@gmail.com>
"""
import argparse
import csv
import logging
import wx
from skvideo.io import vreader, ffprobe, FFmpegReader


def array_to_wx(image):
    height, width = image.shape[:-1]
    buffer = image.tostring()
    bitmap = wx.Bitmap.FromBuffer(width, height, buffer)
    return bitmap

class Panel(wx.Panel):
    def __init__(self, parent, video):
        super(Panel, self).__init__(parent, -1)
        self.video = video
        self.parent = parent
        self.SetSize(SIZE)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.pos = None
        self.frame_n = None
        self.play = False
        self.exit = False
        self.annotation = {}
        self.Bind(wx.EVT_MOTION, self.store_pos)
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyPress)
        self.update()

    def update(self):
        if self.play:
            self.Refresh()
            self.Update()
            self.annotation[self.frame_n] = self.pos
            if self.pos:
                with open(output_file_name, 'a') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'frame': self.frame_n, 'x': self.pos['x'], 'y': self.pos['y']})
                logging.debug('frame %s: x=%s, y=%s', self.frame_n, self.pos['x'], self.pos['y'])
        if not self.exit:
            wx.CallLater(1, self.update)

    def create_bitmap(self):
        try:
            self.frame_n, frame = self.video.__next__()
        except StopIteration:
            pass
        bitmap = array_to_wx(frame)
        return bitmap

    def on_paint(self, event):
        bitmap = self.create_bitmap()
        dc = wx.AutoBufferedPaintDC(self)
        dc.DrawBitmap(bitmap, 0, 0)

    def store_pos(self, event):
        pos = event.GetPosition()
        self.pos = {'x': pos[0], 'y': pos[1]}

    def onKeyPress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_SPACE:
            self.play = not(self.play)
        if keycode == wx.WXK_ESCAPE:
            self.exit = not(self.exit)
            logging.debug('escacpe %s', self.exit)
            self.Close()
            self.parent.Close()


class Frame(wx.Frame):
    def __init__(self, video):
        style = wx.DEFAULT_FRAME_STYLE & ~wx.RESIZE_BORDER & ~wx.MAXIMIZE_BOX
        super(Frame, self).__init__(None, -1, 'Camera Viewer', style=style,
                                    size=(10,10))
        panel = Panel(self, video)
        self.Fit()


def main(video):
    app = wx.App()
    frame = Frame(video)
    frame.Center()
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("file_path", help="path to the video.")
    parser.add_argument("--skip", type=float, default=0,
                        help="seconds to skip at the begining of the video. Default 0.")
    parser.add_argument("--ouput", type=str, default='output.csv',
                        help="Name of the output file. Default output.csv.")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG)
    file_path = args.file_path
    output_file_name = args.ouput
    with open(output_file_name, 'w') as csvfile:
        fieldnames = ['frame', 'x', 'y']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    metadata = ffprobe(file_path)['video']
    fr = float(metadata['@r_frame_rate'].split('/')[0])/float(metadata['@r_frame_rate'].split('/')[1])
    nframes = float(metadata['@duration_ts'])
    time_length = float(metadata['@duration'])
    frame_shape = (int(metadata['@height']), int(metadata['@width']), 3)
    skip = args.skip
    SIZE = frame_shape[:-1][::-1]


    secs = skip/fr
    video = enumerate(FFmpegReader(file_path, inputdict={'-ss': str(secs)}), skip)

    main(video)
