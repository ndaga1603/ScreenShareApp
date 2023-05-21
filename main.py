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
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.responsivelayout import MDResponsiveLayout

from vidstream import ScreenShareClient, StreamingServer
import threading
import socket

# For Database Management
from db import DatabaseManager as DBManager


class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()

class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class MainScreen(Screen):
    pass

# class HomeScreen(Screen):
#     pass


# class FeedbackScreen(Screen):
#     pass


# class HelpScreen(Screen):
#     pass


# class RunningServerScreen(Screen):
#     pass

class MainApp(MDApp):
    # address address
    # address = socket.gethostbyname(socket.gethostname())
    port = 65432
    address = '127.0.0.1'

    # Server scripts
    server = StreamingServer(address, port)
    
    # Client scripts
    client = ScreenShareClient(address, port)

    dialog = None


    def build(self):
        self.title = ""
        Window.size = [320, 600]
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'DeepPurple'

        # Create a screen manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(LoginScreen(name='login_screen'))
        screen_manager.add_widget(RegisterScreen(name='register_screen'))
        screen_manager.add_widget(MainScreen(name='main'))
        # screen_manager.add_widget(HomeScreen(name='home'))
        # screen_manager.add_widget(FeedbackScreen(name='feedback'))
        # screen_manager.add_widget(HelpScreen(name='help'))
        # screen_manager.add_widget(RunningServerScreen(name='server_running'))

        return screen_manager
  

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

    def login(self):
        username = self.root.get_screen('login_screen').ids.username.text
        password = self.root.get_screen('login_screen').ids.password.text


        if username == "" or password == "":
            toast("Please fill all fields")
        else:
            dbManager = DBManager(password, username, user_type="")
            ouput = dbManager.login()

            if ouput:
               
                toast("You have been logged in")
                self.root.current = 'main'
            
            else:
                toast("Invalid credentials")
        
    def register(self):
        user_type = ""
        username = self.root.get_screen('register_screen').ids.username.text
        password = self.root.get_screen('register_screen').ids.password1.text
        confirm_password = self.root.get_screen('register_screen').ids.password2.text
        student_type = self.root.get_screen('register_screen').ids.user_type.active
        if student_type:
            user_type = "Student"
        else:
            user_type = "Teacher"
   
        if username == "" or password == "" or confirm_password == "":
            toast("Please fill all fields")
        else:
            if password == confirm_password:
                dbManager = DBManager(password, username, user_type)
                input = dbManager.register()

                if input:
                    self.root.get_screen('register_screen').ids.username.text = ""
                    self.root.get_screen('register_screen').ids.password1.text = ""
                    self.root.get_screen('register_screen').ids.password2.text = ""
                 

                    toast("You have been registered")
                    self.root.current = 'login_screen'
                
                else:
                    toast("User already exists")
    
            else:
                toast("Passwords do not match")

    def logout(self):
        self.root.current = 'login_screen'
        self.root.get_screen('login_screen').ids.username.text = ""
        self.root.get_screen('login_screen').ids.password.text = ""
        toast("You have been logged out")

    def cancel_dialog(self, obj):
        self.dialog.dismiss()

    def join_screen(self, obj):
        client_thread = threading.Thread(target=self.client.start_stream, args=("receive",))
        client_thread.start()
        self.dialog.dismiss()
        toast("You have been connected to the server")
    

    def show_toast(self):
        '''Displays a toast on the screen.'''
        text = "Thanks for your feedback!"
        toast(text)

    def start_server(self):
        server_thread = threading.Thread(target=self.server.start_server)
        server_thread.start()
        toast(f'Server start at {self.server}')

    def start_screen_share(self):
        client_thread = threading.Thread(target=self.client.start_stream, args=("send",))
        client_thread.start()
        toast(f'Starting screen share at {self.client}')
        # manager = ContentNavigationDrawer()
   
    # stop screen sharing
    def stop_screen_sharing(self):
        self.client.stop_stream()

    # stop server
    def stop_server(self):
        self.server.stop_server()


    def invite_friends(self):
        # TODO craeting WhatsApp invitation mechanism
        pass
if __name__ == '__main__':
    MainApp().run()
