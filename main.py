import os, sys
from kivy.resources import resource_add_path, resource_find
import re

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

from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFloatingActionButton
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.metrics import dp
from kivy.properties import BooleanProperty

from vidstream import ScreenShareClient, StreamingServer
import threading
import socket
import webbrowser
import subprocess
import urllib.parse
from kivy.clock import Clock

from kivy.uix.button import Button # For the drawer buttons


# For Database Management
from db import DatabaseManager as DBManager
from pdf import CreatePDF


class ConnectedClientsScreen(Screen):
    def __init__(self, main_app, **kwargs):
        super(ConnectedClientsScreen, self).__init__(**kwargs)
        self.main_app = main_app
        self.active_users = ["Instructor"]
        self.client_data = []
        Clock.schedule_interval(self.get_active_users, 1)

    def get_active_users(self, dt):
        """Gets the active users in the server."""
        try:
            users = self.main_app.server.get_active_users()
            # print(users)
            for user in users:
                if user not in self.active_users:
                    self.active_users.append(user)
        except:
            # toast("Server not running")
            return None

    def on_enter(self, *args):
        Clock.schedule_interval(self.update_datatable, 5)

    def on_leave(self, *args):
        Clock.unschedule(self.update_datatable)

    def update_datatable(self, *args):
        new_data = self.fetch_data()
        data = []
        for row in new_data:
            if row not in data:
                data.append(row)
        anchor_layout = MDAnchorLayout(anchor_x="center", anchor_y="center")
        layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=Window.size[1] - 100,
            padding=(20, 20, 20, 20),
        )

        label = MDLabel(
            text="Connected Users",
            halign="center",
            theme_text_color="Secondary",
            font_style="H5",
            size_hint_y=None,
            height=Window.size[1] - 550,
        )

        self.data_table = MDDataTable(
            elevation=4,
            background_color_header="#65275d",
            use_pagination=True,
            check=True,
            pagination_menu_pos="auto",
            rows_num=10,
            column_data=[
                ("S/N", dp(20)),
                ("Name", dp(50)),
                ("Status", dp(30)),
            ],
            row_data=data,
        )
        
        stop_button = MDFloatingActionButton(
            icon="stop",
            pos_hint={"center_x": 0.5},
            md_bg_color=[205 / 256, 24 / 256, 24 / 256, 1],
            on_release=self.main_app.stop_server,
        )

        back_button = MDIconButton(
            icon="arrow-left",
            pos_hint={"x": 0.05, "top": 0.95},
            on_release=self.main_app.back_home,
        )

        self.data_table.bind(on_check_press=self.on_check_press)
        layout.add_widget(label)
        layout.add_widget(self.data_table)
        anchor_layout.add_widget(layout)

        float_layout = MDFloatLayout()
        float_layout.add_widget(anchor_layout)
        float_layout.add_widget(stop_button)
        float_layout.add_widget(back_button)

        self.add_widget(float_layout)

    def on_check_press(self, instance_table, current_row):
        '''Called when the check box in the table row is checked.'''

        names = [data[1] for data in instance_table.row_data]
        if len(names) > 1:
            names.pop(0)

            pdf = CreatePDF(filename="joined_students.pdf", names=names)
            pdf.create_pdf()  

    def fetch_data(self):
        # print(self.active_users)
        for index, user in enumerate(self.active_users):
            row = (
                str(index + 1),
                user,
                (
                    "checkbox-marked-circle",
                    [39 / 256, 174 / 256, 96 / 256, 1],
                    "Online",
                ),
            )
        # if row not in self.client_data:
        self.client_data.append(row)
        # print(self.client_data)
        return self.client_data


class ContentNavigationDrawer(MDScrollView):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class ClickableTextFieldRound(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()


class ClickableTextFieldPassword(MDRelativeLayout):
    text = StringProperty()
    hint_text = StringProperty()

    def get_password(self):
        return self.ids.password.text


class LoginScreen(Screen):
    pass

class RegisterScreen(Screen):
    pass

class MainScreen(Screen):
    pass

class MainApp(MDApp):
    def __init__(self, **kwargs):
        """Initialize the app"""
        super(MainApp, self).__init__(**kwargs)
        self.server_running = False
        self.is_sharing = False
        self.port = 9999
        self.address = None
        self.server = None
        self.client = None
        self.dialog = None
        self.client_dialog = None
        self.user = None
        self.user_type = None
        self.receiver = None

    def build(self):
        """Build the app"""

        self.title = ""
        Window.size = [585, 610]
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"

        # Create a screen manager
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(LoginScreen(name="login_screen"))
        self.screen_manager.add_widget(RegisterScreen(name="register_screen"))
        self.screen_manager.add_widget(MainScreen(name="main"))
        self.screen_manager.add_widget(
            ConnectedClientsScreen(main_app=self, name="connected_clients")
        )

        return self.screen_manager

    def server_dialog(self):
        """Create a dialog for starting the server"""

        if not self.dialog:
            self.dialog = MDDialog(
                title="Start Server",
                radius=[20, 7, 20, 7],
                type="custom",
                content_cls=MDBoxLayout(
                    MDTextField(
                        hint_text="Ip address of the server",
                        line_color_focus="orange",
                    ),
                    MDTextField(
                        hint_text="Port of the server",
                        line_color_focus="orange",
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
                        on_release=lambda x: self.cancel_dialog("obj", type="server"),
                    ),
                    MDFlatButton(
                        text="Start",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.run_server,
                    ),
                ],
            )
        self.dialog.open()

    def join_dialog(self):
        """Create a dialog box to join a server"""

        if not self.client_dialog:
            self.client_dialog = MDDialog(
                title="Connect To The Server",
                radius=[20, 7, 20, 7],
                type="custom",
                content_cls=MDBoxLayout(
                    MDTextField(
                        hint_text="Ip address of the target",
                        line_color_focus="orange",
                        # hint_text_color_normal = "orange"
                    ),
                    MDTextField(
                        hint_text="Port of the target",
                        line_color_focus="orange",
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
                        on_release=lambda x: self.cancel_dialog("obj", type="client"),
                    ),
                    MDFlatButton(
                        text="Connect",
                        theme_text_color="Custom",
                        text_color=self.theme_cls.primary_color,
                        on_release=self.join_screen,
                    ),
                ],
            )
        self.client_dialog.open()

    def login(self):
        """Login a user
        Parameters
        ----------
        username : str
            Username of the user
        password : str
            Password of the user
        """
        username = self.root.get_screen("login_screen").ids.username.text
        password = self.root.get_screen("login_screen").ids.password.text
       
        if username == "" or password == "":
            toast("Please fill all fields")
        else:
            dbManager = DBManager(password, username, user_type="")
            ouput = dbManager.login()

            if ouput[0]:
                self.user = password
                self.user_type = ouput[1]
                # print(self.user_type)
                toast("You have been logged in")
                self.root.current = "main"
                # print(self.user)
               
            else:
                toast("Invalid credentials")

    def register(self):
        """Register a new user
        Parameters
        ----------
        username : str
            Username of the user
        password : str
            Password of the user
        user_type : str
            Type of the user
        """
        user_type = ""
        password_pattern = r"^NIT/[A-Z]{3}/\d{4}/[A-Za-z0-9]+$"
        username = self.root.get_screen("register_screen").ids.username.text
        password = self.root.get_screen("register_screen").ids.password1.text
        confirm_password = self.root.get_screen("register_screen").ids.password2.text
        student_type = self.root.get_screen("register_screen").ids.user_type.active
        if re.match(password_pattern, password):
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
                        self.root.get_screen("register_screen").ids.username.text = ""
                        self.root.get_screen("register_screen").ids.password1.text = ""
                        self.root.get_screen("register_screen").ids.password2.text = ""

                        toast("You have been registered")
                        self.root.current = "login_screen"

                    else:
                        toast("User already exists")

                else:
                    toast("Passwords do not match")
        else:
            toast("Password should be of the form NIT/BIT/2020/qw00")

    def logout(self):
        """Logs out the user and changes the screen to login screen."""

        self.root.current = "login_screen"
        self.user = None
        self.user_type = None
        if self.server_running or self.is_sharing:
            self.stop_server(instance=None)
            self.stop_screen_sharing()
            self.root.get_screen("login_screen").ids.username.text = ""
            self.root.get_screen("login_screen").ids.password.text = ""
            toast("You have been logged out")
        else:
            self.root.get_screen("login_screen").ids.username.text = ""
            self.root.get_screen("login_screen").ids.password.text = ""
            toast("You have been logged out")

    def cancel_dialog(self, obj, type):
        """Closes the dialog box.
        Args:
        ----
            obj: The object of the button pressed.
        """
        if type == "server":
            self.dialog.dismiss()
            self.dialog = None
        else:
            self.client_dialog.dismiss()
            self.client_dialog = None

    def join_screen(self, obj):
        """Changes the screen to join screen.
        Args:
        ----
            obj: The object of the button pressed.
        Parameters:
        ----------
            ip: The ip address of the target.
            port: The port of the target.
        """
        if self.user != None:
            ip = self.client_dialog.content_cls.children[1].text
            port = self.client_dialog.content_cls.children[0].text
            if ip == "" or port == "":
                toast("Please fill all fields")
            else:
                try:
                    self.receiver = ScreenShareClient(str(ip), int(port))
                    client_thread = threading.Thread(
                        target=self.receiver.start_stream,
                        args=(
                            "receive",
                            self.user,
                        ),
                    )
                    client_thread.start()
                    self.client_dialog.dismiss()
                    self.client_dialog = None
                    toast("You have been connected to the server")
                except:
                    toast("Could not connect to the server")

    def show_toast(self):
        """Displays a toast on the screen.
        Parameters:
        ----------
            text: The text to be displayed on the toast.
        """
        text = "Thanks for your feedback!"

        toast(text)

    def back_home(self, instance):
        """Changes the screen to home screen."""
        self.root.current = "main"

    def go_to_connected_clients(self):
        """Changes the screen to connected clients."""
        if self.user != None:
            if self.server_running:
                self.root.current = "connected_clients"
            else:
                toast("Please start the server first")

    def run_server(self, obj):
        """Starts the server.
        Args:
        ----
            obj: The object of the button pressed.
        Parameters:
        ----------
            ip: The ip address of the target.
            port: The port of the target.
        """
        if self.user != None:
            self.address = self.dialog.content_cls.children[1].text
            self.port = self.dialog.content_cls.children[0].text
            if self.address == "" or self.port == "":
                toast("Please fill all fields")
            else:
                try:
                    self.server = StreamingServer(str(self.address), int(self.port))
                    server_thread = threading.Thread(target=self.server.start_server)
                    server_thread.start()
                    toast(f"Server start at {self.address}:{self.port}")
                    self.dialog.dismiss()
                    self.server_running = True
                    self.go_to_connected_clients()
                except:
                    toast("Error! not able to start server")

    def start_screen_share(self):
        """Starts the screen sharing.
        Parameters:
        ----------
            address: The ip address of the target.
            port: The port of the target.
        """
        if self.user != None:
            try:
                address = self.dialog.content_cls.children[1].text
                port = self.dialog.content_cls.children[0].text
                self.client = ScreenShareClient(str(address), int(port))
                client_thread = threading.Thread(
                    target=self.client.start_stream,
                    args=(
                        "send",
                        self.user,
                    ),
                )
                client_thread.start()
                self.is_sharing = True
                toast(f"screen share Staring")
            except:
                toast("Error! server not running")

    def stop_screen_sharing(self):
        """Stops the screen sharing."""
        self.client.stop_stream()
        self.is_sharing = False

    def stop_server(self, instance):
        """Stops the server."""
        if self.user != None:
            try:
                self.server.stop_server()
                self.server_running = False
                self.root.current = "main"
                toast("Server stopped")
            except:
                toast("Server not running")

    def invite_friends(self):
        """Invites friends to the meeting."""
        if self.user != None and self.server_running:
            message = f"Hello, we are having a meeting on ScreenShare. Please join us. Here is the link to join the meeting, Address: {self.address} Port: {self.port}"
            encoded_text = urllib.parse.quote(message)
            try:
                subprocess.Popen(
                    ["cmd", "/C", f"start whatsapp://send?text={encoded_text}"],
                    shell=True,
                )
            except FileNotFoundError:
                url = f"https://web.whatsapp.com/send?text={encoded_text}"
                webbrowser.open(url)


if __name__ == "__main__":
    MainApp().run()
    try:
        if hasattr(sys, "_MEIPASS"):
            resource_add_path(os.path.join(sys._MEIPASS))
        MainApp().run()
    except Exception as e:
        print(e)
        input("Press enter.")
