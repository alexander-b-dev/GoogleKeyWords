import multiprocessing

import config

if __name__ == '__main__':
    multiprocessing.freeze_support()
    import os.path

    from kivy import Config
    from kivy.core.window import Window
    from kivy.lang import Builder
    from kivy.metrics import dp
    from kivymd.app import MDApp
    from kivymd.uix.button import MDFillRoundFlatButton
    from kivymd.uix.floatlayout import MDFloatLayout
    from kivymd.uix.gridlayout import MDGridLayout
    from kivymd.uix.label import MDLabel
    from kivymd.uix.scrollview import MDScrollView

    from google.ads.googleads.client import GoogleAdsClient

    from add_task import AddTask


    class GoogleKeyWordsApp(MDApp):
        def __init__(self):
            super().__init__()
            self.theme_cls.theme_style = "Dark"
            self.theme_cls.primary_palette = "Amber"
            Builder.load_file('task.kv')
            self.customerId = config.customerId
            self.googleads_client = GoogleAdsClient.load_from_storage(path="google-ads.yaml", version="v13")
            self.tasksAdder = AddTask(self.theme_cls,
                                      self.addTaskCallback,
                                      self.googleads_client.get_service("GoogleAdsService"),
                                      self.customerId)
            self.scroll = None
            self.fillerTask = MDFloatLayout(size_hint=(None, None),
                                            size=(350, 120))
            self.tasksContainer = MDGridLayout(cols=1,
                                               size_hint_x=0.97,
                                               size_hint_y=None,
                                               pos_hint={"center_x": 0.5},
                                               spacing=dp(7))
            self.tasksContainer.bind(children=lambda x, y: self.showHideNoTasks())
            self.tasksContainer.bind(minimum_height=self.tasksContainer.setter("height"))
            self.noTasks = MDLabel(text="No tasks!",
                                   halign="center")

        def build(self):
            Window.size = (dp(350), dp(700))
            self.root = MDFloatLayout(radius=[15, 15, 15, 15],
                                      size_hint=(0.98, 0.98),
                                      pos_hint={"center_x": 0.5, "center_y": 0.5},
                                      md_bg_color=self.theme_cls.bg_dark)

            self.showHideNoTasks()
            self.scroll = MDScrollView(pos_hint={"center_x": 0.5, "top": 1},
                                       size_hint_x=None,
                                       width=dp(330))
            self.root.bind(width=lambda x, y: self.adjustGrd())
            self.tasksContainer.bind(cols=lambda x, y: self.adjustScrollWidth())
            self.scroll.add_widget(self.tasksContainer)
            self.root.add_widget(self.scroll, 1)
            self.root.add_widget(MDFillRoundFlatButton(text="+ Add",
                                                       pos_hint={"center_x": 0.5, "center_y": 0.1},
                                                       on_release=lambda x: self.addBtnCallback()),
                                 0)
            return self.root

        def adjustScrollWidth(self):
            self.scroll.width = dp(330) * self.tasksContainer.cols + dp(7) * (self.tasksContainer.cols - 1)

        def adjustGrd(self):
            if len(self.tasksContainer.children) > 0:
                cols = int(self.root.width / dp(330))
                self.tasksContainer.cols = cols if cols > 0 else 1
            self.tasksContainer.remove_widget(self.fillerTask)
            self.tasksContainer.add_widget(self.fillerTask)

        def showHideNoTasks(self):
            if len(self.tasksContainer.children) > 0:
                self.root.remove_widget(self.noTasks)
            else:
                self.root.add_widget(self.noTasks)

        def addBtnCallback(self):
            self.tasksAdder.open()

        def addTaskCallback(self, task):
            self.tasksContainer.add_widget(task)
            task.start()


    currentDir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(currentDir, "log")):
        os.mkdir(os.path.join(currentDir, "log"))
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    GoogleKeyWordsApp().run()
