import ipywidgets.widgets as widgets
import traitlets
import cv2
import os
import time
import threading

from ipywidgets import Button, HBox, VBox

from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess
import os

clearCommand = ["--folder", "/store_00010001/DCIM/100EOS5D", \
                "--delete-all-files", "-R"]
triggerCommand = ["--trigger-capture"]
downloadCommand = ["--get-all-files"]

picID = "Eos5D"
folder_name = picID
save_location = os.environ['HOME'] + "/Pictures/" + folder_name

# Kill the gphoto process that starts whenever we turn on the camera or reboot the raspberry pi
def killGphoto2Process():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Search for the process we want to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            # Kill that process!
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)
            
def createSaveFolder():
    try:
        os.makedirs(save_location)
    except:
        print("Failed to create new directory.")
    os.chdir(save_location)

def captureImages():
    gp(triggerCommand)
    sleep(3)
    gp(downloadCommand)
    gp(clearCommand)
    sleep(0.02)
    renameFiles(picID)

def renameFiles(ID):
    shot_time = datetime.now().strftime("%Y%m%d_%H%M%S_")
    for filename in os.listdir("."):
        if len(filename) < 13:
            os.rename(filename, (shot_time + ID + ".JPG"))

class Bgphoto():
    def __init__(self):
        killGphoto2Process()
        createSaveFolder()
        self.wp = WidgetPanel()
        self._setting()
        self.switch_status = 0
        self.snap_dir = save_location
        self.wp.textbox_count.value = len(os.listdir(self.snap_dir)) - 1
    
    def switch_on(self):
        if self.switch_status == 0:
            self.switch_status = 1
            self._lapse_standby()
            self._lapse_run()

    def switch_off(self):
        if self.switch_status == 1:
            self.wp.button_status.button_style=''
            self.wp.button_status.description="Lapse Status: OFF"
            self.switch_status = 0
            self.wp.textbox_time.value = 0

    def time_count_down(self, t):
        self.wp.textbox_time.value=t
        for i in range (0, t+1):
            self.wp.textbox_time.value=t-i
            time.sleep(1)
            if self.switch_status == 0:
                break
            
    def _setting(self):
        self.wp.button_on.on_click(lambda x: self.switch_on())
        self.wp.button_off.on_click(lambda x: self.switch_off())
        self.wp.button_snapshot.on_click(lambda x: captureImages())
        
    def play(self):
        return self.wp.show_widgets()
    
    def _run(self):
        while self.switch_status == 1:
            print("Shot")
            self.shot()
            self.time_count_down(t=self.wp.textbox_interval.value)

    def _lapse_run(self):
        self.wp.button_status.button_style='danger'
        self.wp.button_status.description="Lapse Status: ON"
        x = threading.Thread(target=self._run, args=())
        x.start()
    
    def _lapse_standby(self):
        self.wp.button_status.button_style='warning'
        self.wp.button_status.description="Lapse Status: Standby"
        self.time_count_down(t=self.wp.textbox_delay.value)
        
    def shot(self):
        captureImages()
        self.wp.textbox_count.value = len(os.listdir(self.snap_dir)) - 1
        pass

class WidgetPanel():
    def __init__(self, button_list=None):
        self.button_layout = widgets.Layout(width='180px', height='30px', align_self='center')
        self.inttext_layout = widgets.Layout(width='180px')
        self.button_on =  Button(description="ON", layout=widgets.Layout(width='90px'), button_style='danger')
        self.button_off =  Button(description="OFF", layout=widgets.Layout(width='90px'), button_style='')
        self.button_status = Button(description="Lapse Status", layout=self.button_layout, button_style='')
        self.button_snapshot =  Button(description="SnapShot", layout=self.button_layout, button_style='info')
        self.textbox_status = widgets.Textarea(value='', description='Status:', layout=widgets.Layout(width='548px'))
        self.textbox_path = widgets.Text(value='/home/bbot/images', description='Saving Path:', layout=widgets.Layout(width='548px'))
        self.textbox_time = widgets.IntText(value='0', description='TimeToShot:', layout=self.inttext_layout)
        self.textbox_interval = widgets.IntText(value='5', description='Interval(sec):', layout=self.inttext_layout)
        self.textbox_delay = widgets.IntText(value='3', description='Initial Delay:', layout=self.inttext_layout)
        self.textbox_total = widgets.IntText(value='3', description='Total Shots:', layout=self.inttext_layout)
        self.textbox_count = widgets.IntText(value='0', description='Shots Count:', layout=self.inttext_layout)
        self.textbox_left = widgets.IntText(value='0', description='Shots Left:', layout=self.inttext_layout)
        
    def show_widgets(self):
        row1 = HBox([self.textbox_interval, self.textbox_delay, self.textbox_time])
        row2 = HBox([self.button_snapshot, self.button_status, self.button_on, self.button_off])
        row3 = HBox([self.textbox_count, self.textbox_left, self.textbox_total])
        return VBox([row1, row2, row3, self.textbox_path, self.textbox_status])