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
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDSeparator
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.textfield import MDTextField

from languages import languages
from task import Task


class AddTask(Popup):

    def __init__(self, theme, callback, googleGeoService, googleCustomerId):
        super().__init__()
        self.updRegionMenuEvent = None
        self.error = False
        self.theme = theme
        self.googleGeoService = googleGeoService
        self.googleCustomerId = googleCustomerId
        self.googleQuery = """
        SELECT
         geo_target_constant.id,
         geo_target_constant.name,
         geo_target_constant.canonical_name
        FROM geo_target_constant
        WHERE geo_target_constant.name LIKE "%s%%"
        ORDER BY geo_target_constant.name
        """
        self.tmpSize = (dp(350), dp(700))
        self.title = "Add task"
        self.callback = callback
        self.selectedRegions = dict()
        self.separator_color = theme.primary_color

        self.fileManager = MDFileManager(preview=False,
                                         selector="folder",
                                         select_path=self.folderSelected)
        self.fileManager.exit_manager = lambda x: self.fileManager.close()

        tmpButton1 = MDFlatButton(text="CANCEL")
        tmpButton2 = MDFlatButton(text="REWRITE", on_release=lambda x: self.rewriteFile())
        self.dialog = MDDialog(text="File already exists. Rewrite it?",
                               buttons=[tmpButton1, tmpButton2])
        tmpButton1.on_release = self.dialog.dismiss

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
        self.txtLanguage.bind(text=self.txtLangTextChange)
        settingsPanel.add_widget(self.txtLanguage)

        self.languageMenu = MDDropdownMenu(
            caller=self.txtLanguage,
            width_mult=4
        )

        for lang in languages.keys():
            self.languageMenu.items.append({"text": lang,
                                            "viewclass": "OneLineListItem",
                                            "on_release": lambda x=lang: self.setLang(x)})
        self.languageMenu.max_height = dp(200)

        self.txtRegion = MDTextField(hint_text="Region")
        self.txtRegion.bind(text=self.txtRegionTextChange)
        settingsPanel.add_widget(self.txtRegion)

        self.regionMenu = MDDropdownMenu(
            caller=self.txtRegion,
            width_mult=4
        )
        self.regionMenu.max_height = dp(200)

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
        self.periodMenu.max_height = dp(200)
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
                                       size_hint_y=None)
        self.txtKeyWords.bind(focus=self.formatKeyWords)
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
                                      on_release=lambda x: self.checkData()))

        mainCont.add_widget(tmp)
        self.add_widget(mainCont)

    def on_open(self):
        self.txtName.text = ""
        self.txtKeyWords.text = ""
        self.txtName.required = True
        self.txtPath.required = True
        self.txtLanguage.required = True
        self.txtRegion.required = True
        self.txtPeriod.required = True
        if Window.width < dp(700):
            self.tmpSize = Window.size
            Window.size = (dp(700), Window.size[1])

    def setFocus(self, ctrl):
        ctrl.focus = True

    def updateSelectedRegions(self):
        regionsInBox = []
        for reg in self.txtRegion.text.split(","):
            tmp = reg.strip(" ")
            if tmp and not tmp.isspace():
                regionsInBox.append(tmp)

        for region in list(self.selectedRegions.keys()):
            if region not in regionsInBox:
                del self.selectedRegions[region]

    def checkRegionsDict(self):
        regionsInBox = []
        for reg in self.txtRegion.text.split(","):
            tmp = reg.strip(" ")
            if tmp and not tmp.isspace():
                regionsInBox.append(tmp)

        return len(regionsInBox) == len(self.selectedRegions.keys())

    def setRegion(self, txt, regionId):
        self.selectedRegions.update({txt: regionId})
        self.txtRegion.unbind(text=self.txtRegionTextChange)
        self.txtRegion.text = ", ".join(self.selectedRegions.keys()).strip(", ")
        self.txtRegion.bind(text=self.txtRegionTextChange)
        self.regionMenu.dismiss()

    def updateRegionMenu(self, instance, value):
        self.updateSelectedRegions()
        currentWord = value[:instance.cursor_col].count(",")
        tmp = [word.strip(" ") for word in value.split(",")]
        if len(tmp) >= currentWord:
            queryKey = tmp[currentWord]
            if queryKey:
                self.regionMenu.dismiss()
                self.regionMenu.items = []
                rows = self.googleGeoService.search(customer_id=self.googleCustomerId,
                                                    query=self.googleQuery % queryKey)
                for row in rows.results:
                    self.regionMenu.items.append({"text": row.geo_target_constant.canonical_name,
                                                  "viewclass": "OneLineListItem",
                                                  "on_release": lambda x=row.geo_target_constant.name,
                                                                       y=row.geo_target_constant.id: self.setRegion(x,
                                                                                                                    y)})
                self.regionMenu.open()

    def txtRegionTextChange(self, instance, value: str):
        if self.updRegionMenuEvent:
            if not self.updRegionMenuEvent.is_triggered:
                self.updRegionMenuEvent.cancel()
        self.updRegionMenuEvent = Clock.schedule_once(lambda x: self.updateRegionMenu(instance, value), 1)

    def setLang(self, lang):
        self.txtLanguage.unbind(text=self.txtLangTextChange)
        self.txtLanguage.text = lang
        self.txtLanguage.bind(text=self.txtLangTextChange)
        self.languageMenu.dismiss()

    def txtLangTextChange(self, instance, value: str):
        self.languageMenu.dismiss()
        self.languageMenu.items = []
        for lang in languages.keys():
            if lang.lower().startswith(value.lower()):
                self.languageMenu.items.append({"text": lang,
                                                "viewclass": "OneLineListItem",
                                                "on_release": lambda x=lang: self.setLang(x)})
        self.languageMenu.open()

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
        if self.txtLanguage.collide_point(*touch.pos):
            self.languageMenu.open()
            Clock.schedule_once(lambda x: self.setFocus(self.txtLanguage), 0.2)
        if self.txtPeriod.collide_point(*touch.pos):
            self.periodMenu.open()
            Clock.schedule_once(lambda x: self.setFocus(self.txtPeriod), 0.2)

    def formatKeyWords(self, ctr, touch):
        if not self.txtKeyWords.focus:
            txt = ""
            for row in self.txtKeyWords.text.split("\n"):
                if row and not row.isspace():
                    txt += "%s\n" % row.strip(" ")
            self.txtKeyWords.text = txt[:-1]

    def on_dismiss(self):
        if Window.width <= 700:
            Window.size = self.tmpSize

    def checkData(self):
        self.error = False
        if self.txtName.text == "" or re.match(r'[<>:"/\\|?*]', self.txtName.text):
            self.txtName.error = True
            self.error = True
        if not os.path.exists(self.txtPath.text):
            self.txtPath.error = True
            self.error = True
        if self.txtLanguage.text not in languages.keys():
            self.txtLanguage.error = True
            self.error = True
        if len(self.selectedRegions.keys()) == 0 or not self.checkRegionsDict():
            self.txtRegion.error = True
            self.error = True
        if not re.match(r'^\d{2}\.\d{4} ?- ?\d{2}\.\d{4}$', self.txtPeriod.text):
            self.txtPeriod.error = True
            self.error = True
        else:
            periodFrom, periodTo = self.txtPeriod.text.split("-")
            startMonth, startYear = tuple(map(int, periodFrom.split(".")))
            endMonth, endYear = tuple(map(int, periodTo.split(".")))
            if startYear > endYear:
                self.txtPeriod.error = True
                self.error = True
            elif startYear == endYear:
                if startMonth > endMonth:
                    self.txtPeriod.error = True
                    self.error = True
        if self.txtKeyWords.text == "":
            self.txtKeyWords.error = True
            self.error = True
        if self.error:
            return
        if os.path.exists(os.path.join(self.txtPath.text, self.txtName.text + ".xlsx")):
            self.dialog.open()
        else:
            self.returnTask()

    def rewriteFile(self):
        self.dialog.dismiss()
        os.remove(os.path.join(self.txtPath.text, self.txtName.text + ".xlsx"))
        self.returnTask()

    def returnTask(self):
        periodFrom = self.txtPeriod.text.split("-")[0].strip(" ")
        periodTo = self.txtPeriod.text.split("-")[1].strip(" ")
        self.callback(Task(self.theme,
                           self.googleCustomerId,
                           self.txtName.text,
                           self.txtPath.text,
                           languages[self.txtLanguage.text],
                           tuple(self.selectedRegions.values()),
                           periodFrom,
                           periodTo,
                           self.inclPartners.active,
                           self.inclNSFW.active,
                           self.txtKeyWords.text.split("\n")))
        self.dismiss()
