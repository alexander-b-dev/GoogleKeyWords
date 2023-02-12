import os
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.card import MDSeparator
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField

from task import Task


class AddTask(Popup):

    def __init__(self, theme, callback):
        super().__init__()
        self.theme = theme
        self.tmpSize = (dp(350), dp(700))
        self.title = "Add task"
        self.callback = callback
        self.separator_color = theme.primary_color
        self.fileManager = MDFileManager(preview=False,
                                         selector="folder",
                                         select_path=self.folderSelected)
        self.fileManager.exit_manager = lambda x: self.fileManager.close()
        settingsPanel = BoxLayout(orientation="vertical",
                                  size_hint=(0.98, 0.98),
                                  pos_hint={"center_x": 0.5, "center_y": 0.5},
                                  size_hint_x=None,
                                  width=dp(350))
        self.txtName = MDTextField(hint_text="Name of search",
                                   helper_text="This is also a filename",
                                   helper_text_mode="on_focus"
                                   )

        settingsPanel.add_widget(self.txtName)

        self.txtPath = MDTextField(hint_text="Folder to save")
        pathBox = MDBoxLayout(orientation="horizontal",
                              spacing=dp(5),
                              padding=0)
        pathBox.add_widget(self.txtPath)
        pathBox.add_widget(MDIconButton(icon="folder-open",
                                        on_release=lambda x: self.fileManager.show(os.path.expanduser("~"))))
        pathBox.size_hint_y = None
        pathBox.height = self.txtPath.height + dp(15)
        settingsPanel.add_widget(pathBox)

        self.txtLanguage = MDTextField(hint_text="Language")
        settingsPanel.add_widget(self.txtLanguage)

        self.txtCountry = MDTextField(hint_text="Country")
        settingsPanel.add_widget(self.txtCountry)

        self.txtPeriod = MDTextField(hint_text="Period")
        self.txtPeriod.on_touch_down = self.openMenu
        self.periodMenu = MDDropdownMenu(
            caller=self.txtPeriod,
            items=[{"text": "Full", "viewclass": "OneLineListItem", "on_release": lambda: self.setPeriod(48)},
                   {"text": "Month", "viewclass": "OneLineListItem", "on_release": lambda: self.setPeriod(1)},
                   {"text": "Year", "viewclass": "OneLineListItem", "on_release": lambda: self.setPeriod(12)},
                   {"text": "2 years", "viewclass": "OneLineListItem", "on_release": lambda: self.setPeriod(24)}],
            width_mult=4
        )
        settingsPanel.add_widget(self.txtPeriod)

        grd = MDGridLayout(cols=2)
        self.inclNSFW = MDSwitch()
        self.inclPartners = MDSwitch()
        grd.add_widget(MDLabel(text="Include search partners"))
        grd.add_widget(self.inclPartners)
        grd.add_widget(MDLabel(text="18+"))
        grd.add_widget(self.inclNSFW)
        grd.size_hint_y = None
        grd.height = self.inclPartners.width * 2 + dp(30)
        grd.padding = [0, 0, dp(15), 0]
        settingsPanel.add_widget(grd)
        settingsPanel.add_widget(MDRelativeLayout())

        root = BoxLayout(orientation="horizontal",
                         spacing=dp(7),
                         size_hint=(1, 0.98),
                         pos_hint={"center_y": 0.5})
        root.add_widget(settingsPanel)
        root.add_widget(MDSeparator(orientation="vertical"))
        scroll = MDScrollView(size_hint=(0.98, 0.99))
        self.txtKeyWords = MDTextField(multiline=True,
                                       hint_text="Key words",
                                       pos_hint={"top": 1},
                                       size_hint_y=None
                                       )
        self.txtKeyWords.height = self.txtKeyWords.minimum_height
        scroll.add_widget(self.txtKeyWords)
        root.add_widget(scroll)
        mainCont = MDBoxLayout(orientation="vertical")
        mainCont.add_widget(root)
        mainCont.add_widget(MDSeparator(orientation="horizontal"))

        tmp = MDRelativeLayout(size_hint=(None, None),
                               height=dp(50),
                               width=dp(150),
                               pos_hint={"right": 0.95, "center_y": 0.5})
        tmp.add_widget(MDRectangleFlatButton(text="Cancel",
                                             pos=(dp(10), dp(5)),
                                             on_release=self.dismiss))
        tmp.add_widget(MDRaisedButton(text="Add",
                                      pos=(dp(100), dp(5)),
                                      on_release=lambda x: self.returnTask()))

        mainCont.add_widget(tmp)
        self.add_widget(mainCont)

    def on_open(self):
        self.txtName.required = True
        self.txtPath.required = True
        self.txtLanguage.required = True
        self.txtCountry.required = True
        self.txtPeriod.required = True
        if Window.width < dp(700):
            self.tmpSize = Window.size
            Window.size = (dp(700), Window.size[1])

    def periodFocus(self, arg):
        self.txtPeriod.focus = True

    def folderSelected(self, folder):
        self.txtPath.text = folder
        self.fileManager.close()

    def setPeriod(self, period):
        txt = "%s - %s" % ((datetime.now() - relativedelta(months=period)).strftime("%m.%Y"),
                           datetime.now().strftime("%m.%Y"))
        self.txtPeriod.text = txt
        self.txtPeriod.error = False
        self.periodMenu.dismiss()

    def openMenu(self, touch):
        if self.txtPeriod.collide_point(*touch.pos):
            self.periodMenu.open()
            Clock.schedule_once(self.periodFocus, 0.2)

    def on_dismiss(self):
        if Window.width <= 700:
            Window.size = self.tmpSize

    def checkData(self):
        error = False
        if self.txtName.text == "" or re.match(r'[<>\:"/\\|?*]', self.txtName.text):
            self.txtName.error = True
            error = True
        if not os.path.exists(self.txtPath.text):
            self.txtPath.error = True
            error = True
        if not re.match(r'^\d{2}\.\d{2} ?- ?\d{2}\.\d{2}$', self.txtPeriod):
            self.txtPeriod.error = True
            error = True
        if self.txtKeyWords.text == "":
            self.txtKeyWords.error = True
            error = True
        if error:
            return

    def returnTask(self):
        self.callback(Task(self.theme))
        self.dismiss()
