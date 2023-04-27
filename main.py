from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivymd.toast import toast
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.scrollview import MDScrollView

from vidstream import ScreenShareClient, StreamingServer
from tkinter import * 
import threading
import socket


# local address
# local_host = socket.gethostbyname(socket.gethostname())
local_host = '127.0.0.1'
print(local_host)



class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()


class ScreenShareApp(MDApp):

    # Server scripts
    server = StreamingServer(local_host, 65432)
    
    # Client scripts
    client = ScreenShareClient(local_host, 65432)

    dialog = None

    def build(self):
        self.title = ""
        self.icon = "language-python"
        Window.size = [320, 600]
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'DeepPurple'
        return Builder.load_file('main.kv')

    def set_info_dialog(self):
            if not self.dialog:
                self.dialog = MDDialog(
                    title = "Connect To The Server",
                    radius = [20, 7, 20, 7],
                    type = "custom",
                    content_cls=MDBoxLayout(
                        MDTextField(
                            hint_text="Ip address of the target",
                            line_color_focus = "orange",
                            # hint_text_color_normal = "orange"

                        ),
                        MDTextField(
                            hint_text="Port of the target",
                            line_color_focus = "orange",
                            # hint_text_color_normal = "orange"

                        ),
                        orientation="vertical",
                        spacing="10dp",
                        size_hint_y=None,
                        height="120dp",
                    ),
                    buttons=[
                        MDFlatButton(
                            text="Cancel",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release = self.cancel_dialog,
                        ),
                        MDFlatButton(
                            text="Ok",
                            theme_text_color="Custom",
                            text_color=self.theme_cls.primary_color,
                            on_release = self.join_screen,

                        ),
                    ],
                )
            self.dialog.open()


    def cancel_dialog(self, obj):
        self.dialog.dismiss()

    def join_screen(self, obj):
        pass
        
    
    def hello(self):
        print("I'm Clicked Now")

    def show_toast(self):
        '''Displays a toast on the screen.'''
        text = "Thanks for your feedback!"
        toast(text)


    def start_server(self):
        server_thread = threading.Thread(target=self.server.start_server)
        server_thread.start()

    def start_screen_share(self):
        client_thread = threading.Thread(target=self.client.start_stream)
        client_thread.start()

    # stop screen sharing
    def stop_screen_sharing(self):
        self.client.stop_stream()

    # stop server
    def stop_server(self):
        self.server.stop_server()

if __name__ == '__main__':
    ScreenShareApp().run()