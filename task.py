import logging
import os.path
import subprocess
from multiprocessing import Process, Queue

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.relativelayout import MDRelativeLayout

import pylightxl

from key_words_getter import getData


class Task(MDRelativeLayout):
    borderColor = ListProperty([0.23137254901960785, 0.8196078431372549, 0.43529411764705883, 1])

    def __init__(self, theme, googleCustomerID, name, folder, language, regions, periodFrom, periodTo,
                 inclPartners, inclNSFW, keyWords):
        super().__init__()
        self.event = None
        self.name = name
        self.folder = folder

        self.logger = logging.getLogger("%s_log" % self.name)
        self.logger.setLevel(logging.INFO)
        self.logFile = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log", "%s.log" % self.name)
        fh = logging.FileHandler(self.logFile, "w")
        fh.setLevel(logging.INFO)
        frm = logging.Formatter("%(asctime)s >>> %(levelname)s: %(message)s")
        fh.setFormatter(frm)
        self.logger.addHandler(fh)

        self.client = None
        self.requestObject = None

        self.process = None
        self.queue = Queue()
        self.taskArgs = (self.queue, googleCustomerID, language, regions, periodFrom, periodTo,
                         inclPartners, inclNSFW, keyWords)
        self.logger.info("Task created with params: %s", str((language, regions, periodFrom, periodTo,
                         inclPartners, inclNSFW, keyWords)))
        self.keyWords = keyWords
        self.keyWordCount = len(keyWords)
        self.doneData = []
        self.md_bg_color = theme.bg_darkest

        self.lblName = MDLabel(text=name,
                               font_style="H6",
                               pos_hint={"x": 0.1, "center_y": 0.8})
        self.prgBar = MDProgressBar(size_hint_x=0.95,
                                    pos_hint={"center_x": 0.5, "center_y": 0.6},
                                    size_hint_y=None,
                                    height=dp(4))
        self.prgBar.value = 0
        self.btnCancel = MDRectangleFlatButton(text="Cancel",
                                               pos=(dp(230), dp(20)),
                                               on_release=lambda x: self.cancel())
        self.add_widget(self.lblName)
        self.add_widget(self.prgBar)
        self.add_widget(self.btnCancel)

    def guiDone(self):
        self.clear_widgets()
        self.borderColor = [0.23137254901960785, 0.8196078431372549, 0.43529411764705883, 1]
        grd = MDRelativeLayout(size_hint=(0.98, 0.98),
                               pos_hint={"center_x": 0.5, "center_y": 0.5})
        grd.add_widget(MDLabel(text=self.name,
                               font_style="H6",
                               theme_text_color="Custom",
                               text_color="3bd16f",
                               pos_hint={"x": 0.05, "center_y": 0.8}))
        grd.add_widget(MDIconButton(icon="close",
                                    pos_hint={"x": 0.8, "center_y": 0.8},
                                    on_release=lambda x: self.parent.remove_widget(self)))
        grd.add_widget(MDLabel(text=self.folder,
                               pos_hint={"x": 0.05, "center_y": 0.3},
                               text_color=[59, 209, 111]))
        grd.add_widget(MDRaisedButton(text="Open",
                                      md_bg_color="3bd16f",
                                      pos_hint={"right": 0.95, "center_y": 0.3},
                                      on_release=lambda x: os.startfile(os.path.join(self.folder, "%s.%s" % (self.name, "xlsx")))))
        self.add_widget(grd)

    def guiError(self, text="Error"):
        self.clear_widgets()
        self.borderColor = [1.0, 0, 0, 1]
        grd = MDRelativeLayout(size_hint=(0.98, 0.98),
                               pos_hint={"center_x": 0.5, "center_y": 0.5})
        grd.add_widget(MDLabel(text=self.name,
                               font_style="H6",
                               theme_text_color="Custom",
                               text_color="red",
                               pos_hint={"x": 0.05, "center_y": 0.8}))
        grd.add_widget(MDIconButton(icon="close",
                                    pos_hint={"x": 0.8, "center_y": 0.8},
                                    on_release=lambda x: self.parent.remove_widget(self)))
        grd.add_widget(MDLabel(text=text,
                               pos_hint={"x": 0.05, "center_y": 0.3},
                               text_color=[59, 209, 111]))
        grd.add_widget(MDRaisedButton(text="View log",
                                      md_bg_color="red",
                                      pos_hint={"right": 0.95, "center_y": 0.3},
                                      on_release=lambda x: subprocess.Popen(["notepad.exe", self.logFile])))
        self.add_widget(grd)

    def start(self):
        self.process = Process(target=getData, args=self.taskArgs, daemon=True)
        self.process.start()
        self.logger.info("Task started")
        self.event = Clock.schedule_once(lambda x: self.checkProgress(), 2)

    def checkProgress(self):
        if self.queue.empty():
            print("empty")
            self.event = Clock.schedule_once(lambda x: self.checkProgress(), 2)
            return

        while not self.queue.empty():
            result = self.queue.get()
            if result != "done":
                if result == "language":
                    self.prgBar.value = 1
                    self.logger.info("Successfully setted language")
                elif result == "locations":
                    self.prgBar.value = 2
                    self.logger.info("Successfully setted regions")
                elif isinstance(result, list):
                    self.doneData.append(result)
                    self.prgBar.value = (len(self.doneData) / self.keyWordCount) * 98
                    self.logger.info("Successfully got data for keyword: %s\n%s" %
                                     (self.keyWords[len(self.doneData) - 1], str(result)))
                else:
                    self.error(result)
                    return
            else:
                self.done()
                return

        self.event = Clock.schedule_once(lambda x: self.checkProgress(), 2)

    def done(self):
        xlFile = pylightxl.Database()
        for count, res in enumerate(self.doneData, start=0):
            sheetName = self.keyWords[count]
            xlFile.add_ws(ws=sheetName)
            for rowNum, idea in enumerate(res, start=1):
                xlFile.ws(ws=sheetName).update_index(row=rowNum, col=1, val=idea[0])
                xlFile.ws(ws=sheetName).update_index(row=rowNum, col=2, val=idea[1])
        pylightxl.writexl(db=xlFile, fn=os.path.join(self.folder, "%s.%s" % (self.name, "xlsx")))
        self.logger.info("File saved: %s" % os.path.join(self.folder, "%s.%s" % (self.name, "xlsx")))
        self.guiDone()

    def cancel(self):
        self.event.cancel()
        self.process.terminate()
        self.guiError("Canceled")

    def error(self, ex):
        self.logger.error(ex)
        self.guiError()
