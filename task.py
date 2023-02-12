from kivy.metrics import dp
from kivy.properties import ListProperty
from kivymd.uix.button import MDRectangleFlatButton, MDIconButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.relativelayout import MDRelativeLayout


class Task(MDRelativeLayout):
    borderColor = ListProperty([0.23137254901960785, 0.8196078431372549, 0.43529411764705883, 1])

    def __init__(self, theme, name="Ololo", folder="D:\\tmp"):
        super().__init__()
        self.name = name
        self.folder = folder
        self.md_bg_color = theme.bg_darkest

        self.lblName = MDLabel(text=name,
                               font_style="H6",
                               pos_hint={"x": 0.1, "center_y": 0.8})
        self.prgBar = MDProgressBar(size_hint_x=0.95,
                                    pos_hint={"center_x": 0.5, "center_y": 0.6},
                                    size_hint_y=None,
                                    height=dp(4))
        self.prgBar.value = 50
        self.btnCancel = MDRectangleFlatButton(text="Cancel",
                                               pos=(dp(230), dp(20)),
                                               on_release=lambda x: self.error("Canceled"))
        self.add_widget(self.lblName)
        self.add_widget(self.prgBar)
        self.add_widget(self.btnCancel)

    def done(self):
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
                                      pos_hint={"right": 0.95, "center_y": 0.3}))
        self.add_widget(grd)

    def error(self, text="Error"):
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
                                      pos_hint={"right": 0.95, "center_y": 0.3}))
        self.add_widget(grd)
