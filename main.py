from kivy import Config
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel
from add_task import AddTask


class GoogleKeyWordsApp(MDApp):
    def __init__(self):
        super().__init__()
        Builder.load_file('task.kv')
        self.tasksAdder = None
        self.tasksContainer = MDGridLayout(cols=1,
                                           size_hint_x=0.97,
                                           pos_hint={"center_x": 0.5},
                                           spacing=dp(7))
        self.tasksContainer.bind(children=lambda x, y: self.showHideNoTasks())
        self.noTasks = MDLabel(text="No tasks!",
                               halign="center")

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        Window.size = (dp(350), dp(700))
        self.root = MDFloatLayout(radius=[15, 15, 15, 15],
                                  size_hint=(0.98, 0.98),
                                  pos_hint={"center_x": 0.5, "center_y": 0.5},
                                  md_bg_color=self.theme_cls.bg_dark)

        self.showHideNoTasks()
        self.root.add_widget(self.tasksContainer)
        self.root.add_widget(MDFillRoundFlatButton(text="+ Add",
                                                   pos_hint={"center_x": 0.5, "center_y": 0.1},
                                                   on_release=lambda x: self.addBtnCallback()),
                             1)
        return self.root

    def showHideNoTasks(self):
        if len(self.tasksContainer.children) > 0:
            self.root.remove_widget(self.noTasks)
        else:
            self.root.add_widget(self.noTasks)

    def addBtnCallback(self):
        self.tasksAdder = AddTask(self.theme_cls, self.addTaskCallback)
        self.tasksAdder.open()

    def addTaskCallback(self, task):
        self.tasksContainer.add_widget(task)


if __name__ == '__main__':
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    GoogleKeyWordsApp().run()
