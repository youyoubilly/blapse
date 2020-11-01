import bcam
from bcam.utils import bgr8_to_jpeg

import ipywidgets.widgets as widgets
import traitlets
import cv2
import os
import time
import threading

from ipywidgets import Button, HBox, VBox

class BLapse():
    def __init__(self, width_dp=544, height_dp=306):
        self.image_widget = widgets.Image(format='jpeg', width=width_dp, height=height_dp)
        self.panel = WidgetPanel()
        self.snap_dir = "images"
        self.pic_id = "X"
        self.panel.textbox_path.value = self.snap_dir
    
    def cam(self, width_cap, height_cap, fps, flip):
        camera = bcam.config().resolution(width_cap, height_cap).fps(fps).flip(flip).build()
        camera.start()
        camera_link = traitlets.dlink((camera, 'value'), (self.image_widget, 'value'), transform=bgr8_to_jpeg)
        return self.image_widget
    
    def play(self, width_cap=1280, height_cap=720, fps=2, flip=0):
        cam = self.cam(width_cap=width_cap, height_cap=height_cap, fps=fps, flip=flip)
        dp = VBox([cam, self.panel.show_widgets()])
        self._setting()
        self.main()
        return dp
    
    def save_snap(self):
        try:
            os.makedirs(self.snap_dir)
        except FileExistsError:
            pass
        localtime = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        image_path = os.path.join(self.snap_dir, localtime + self.pic_id + '.jpg')
        with open(image_path, 'wb') as f:
            f.write(self.image_widget.value)
        self.panel.textbox_count.value = len(os.listdir(self.snap_dir)) - 1
#         self.panel.textbox_left.value = self.panel.textbox_total.value - self.panel.textbox_count.value
        self.panel.textbox_status.value = "{}\n{}".format(self.panel.textbox_status.value, localtime)
        
    def _setting(self): #config for actions
        self.panel.button_snapshot.on_click(lambda x: self.save_snap())
    
    def run(self):
        time.sleep(self.panel.textbox_delay.value)
        while True:
            while self.panel.button_on.value == True:
                self.panel.button_on.button_style='danger'
                self.panel.button_on.description="Lapse ON"
                self.save_snap()
#                 print(self.panel.button_on)
                time.sleep(self.panel.textbox_interval.value)
            self.panel.button_on.button_style='warning'
            self.panel.button_on.description="Lapse OFF"
            print(".", end="")
            time.sleep(1)
        
    def main(self):
        x = threading.Thread(target=self.run, args=())
        x.start()
    
class WidgetPanel():
    def __init__(self, button_list=None):
        self.button_layout = widgets.Layout(width='180px', height='40px', align_self='center')
        self.inttext_layout = widgets.Layout(width='180px')
        self.button_on =  widgets.ToggleButton(description="Lapse ON", layout=self.button_layout, button_style='warning', value=False)
        self.button_snapshot =  Button(description="SnapShot", layout=self.button_layout, button_style='info')
        self.textbox_status = widgets.Textarea(value='', description='Status:', layout=widgets.Layout(width='548px'))
        self.textbox_path = widgets.Text(value='/home/bbot/images', description='Saving Path:', layout=widgets.Layout(width='548px'))
        self.textbox_interval = widgets.IntText(value='5', description='Interval(sec):', layout=self.inttext_layout)
        self.textbox_delay = widgets.IntText(value='3', description='Initial Delay:', layout=self.inttext_layout)
#         self.textbox_total = widgets.IntText(value='3', description='Total Shots:', layout=self.inttext_layout)
        self.textbox_count = widgets.IntText(value='0', description='Shots Done:', layout=self.inttext_layout)
#         self.textbox_left = widgets.IntText(value='0', description='Shots Left:', layout=self.inttext_layout)
        
    def show_widgets(self):
        row1 = HBox([self.textbox_interval, self.textbox_delay, self.textbox_count])
        row2 = HBox([self.button_snapshot, self.button_on])
#         row3 = HBox([self.textbox_count])
        return VBox([row1, row2, self.textbox_path, self.textbox_status])