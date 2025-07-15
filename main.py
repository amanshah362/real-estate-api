# ---------------- main.py ----------------
import cv2
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from pyzbar.pyzbar import decode
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

try:
    from android.runnable import run_on_ui_thread
    from jnius import autoclass

    @run_on_ui_thread
    def hide_android_status_bar():
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        View = autoclass('android.view.View')
        window = PythonActivity.mActivity.getWindow()
        decorView = window.getDecorView()
        decorView.setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_FULLSCREEN |
            View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
        )
except:
    def hide_android_status_bar():
        pass

from database import create_user, verify_user, get_client_by_qr

class DarkBaseScreen(Screen):
    def on_enter(self):
        with self.canvas.before:
            Color(0.05, 0.05, 0.1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class LoginScreen(DarkBaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=40)

        layout.add_widget(MDLabel(
            text="[b]HARMAN TOWN HOUSING SCHEME[/b]",
            halign="center", markup=True, font_style="H5",
            theme_text_color="Custom", text_color=(1, 0.6, 0.2, 1)
        ))

        self.username = MDTextField(hint_text="User Name", icon_right="account", mode="rectangle")
        self.password = MDTextField(hint_text="Password", password=True, icon_right="lock", mode="rectangle")

        layout.add_widget(self.username)
        layout.add_widget(self.password)

        layout.add_widget(MDRaisedButton(text="SIGN IN", md_bg_color=(0.1, 0.8, 0.4, 1), on_release=self.login))
        layout.add_widget(MDRaisedButton(text="CREATE NEW ACCOUNT", md_bg_color=(1, 0.5, 0, 1), on_release=self.goto_signup))
        self.add_widget(layout)

    def login(self, *args):
        if verify_user(self.username.text.strip(), self.password.text.strip()):
            self.manager.current = "simulate"
        else:
            MDDialog(title="Login Failed", text="Invalid username or password").open()

    def goto_signup(self, *args):
        self.manager.current = "signup"

class SignupScreen(DarkBaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=40)

        layout.add_widget(MDLabel(
            text="[b]HARMAN TOWN - CREATE ACCOUNT[/b]",
            halign="center", markup=True, font_style="H5",
            theme_text_color="Custom", text_color=(0.3, 0.7, 1, 1)
        ))

        self.new_user = MDTextField(hint_text="User Name", icon_right="account-plus", mode="rectangle")
        self.new_pass = MDTextField(hint_text="Password", password=True, icon_right="lock", mode="rectangle")

        layout.add_widget(self.new_user)
        layout.add_widget(self.new_pass)

        layout.add_widget(MDRaisedButton(text="SIGN UP", md_bg_color=(0.2, 0.9, 0.6, 1), on_release=self.register))
        layout.add_widget(MDRaisedButton(text="BACK TO LOGIN", on_release=self.back, md_bg_color=(0.4, 0.4, 0.4, 1)))
        self.add_widget(layout)

    def register(self, *args):
        if create_user(self.new_user.text.strip(), self.new_pass.text.strip()):
            MDDialog(title="Success", text="You can now login.").open()
            self.manager.current = "login"
        else:
            MDDialog(title="Error", text="Username already exists").open()

    def back(self, *args):
        self.manager.current = "login"

class SimulateScreen(DarkBaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=40)

        layout.add_widget(MDLabel(
            text="[b]SCAN YOUR RECEIPT[/b]",
            halign="center", markup=True, font_style="H5",
            theme_text_color="Custom", text_color=(1, 0.5, 0, 1)
        ))

        scan_btn = MDRaisedButton(text="START QR SCANNER", md_bg_color=(1, 0.5, 0, 1), on_release=self.goto_camera)
        layout.add_widget(scan_btn)
        self.add_widget(layout)

    def goto_camera(self, *args):
        self.manager.current = "camera"

class CameraScreen(DarkBaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = MDBoxLayout(orientation='vertical', spacing=20, padding=20)
        self.camera_feed = Image()
        self.info_label = MDLabel(
            text="Align QR code to camera", halign="center",
            theme_text_color="Custom", text_color=(1, 0.6, 0.1, 1)
        )

        self.back_btn = MDRaisedButton(text="BACK", on_release=self.back_to_simulate, md_bg_color="#B0BEC5")

        self.layout.add_widget(self.camera_feed)
        self.layout.add_widget(self.info_label)
        self.layout.add_widget(self.back_btn)
        self.add_widget(self.layout)
        self.capture = None

    def on_enter(self):
        self.capture = cv2.VideoCapture(0)
        Clock.schedule_interval(self.update, 1.0 / 30.0)

    def on_leave(self):
        if self.capture:
            self.capture.release()
            Clock.unschedule(self.update)

    def update(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        buf = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.camera_feed.texture = texture

        decoded_objs = decode(frame)
        for obj in decoded_objs:
            qr_data = obj.data.decode("utf-8")
            if "client_login://" in qr_data:
                Clock.unschedule(self.update)
                self.capture.release()
                self.process_qr(qr_data)
                break

    def process_qr(self, qr_data):
        try:
            client_id = qr_data.split("://")[1].split("?")[0]
            pin = qr_data.split("pin=")[1]
            client = get_client_by_qr(client_id, pin)
            if client:
                self.manager.get_screen("result").set_client_info(client)
                self.manager.current = "result"
            else:
                self.info_label.text = "Client not found."
        except Exception as e:
            self.info_label.text = f"QR Error: {e}"

    def back_to_simulate(self, *args):
        self.manager.current = "simulate"

class ResultScreen(DarkBaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.client_data = {}
        layout = MDBoxLayout(orientation="vertical", spacing=20, padding=30)

        self.info_label = MDLabel(
            text="", halign="left", font_style="Body1",
            theme_text_color="Custom", text_color=(0.2, 0.9, 0.5, 1)
        )

        self.back_button = MDRaisedButton(
            text="SCAN AGAIN", on_release=self.back_to_simulate, md_bg_color=(0.4, 0.7, 0.2, 1)
        )

        layout.add_widget(self.info_label)
        layout.add_widget(self.back_button)
        self.add_widget(layout)

    def set_client_info(self, client):
        self.client_data = client

    def on_pre_enter(self, *args):
        if self.client_data:
            remaining = int(self.client_data["total_price"]) - int(self.client_data["paid_amount"])
            self.info_label.text = (
                f"[b]Client Information[/b]\n\n"
                f"Name: {self.client_data['name']}\n"
                f"Plot No: {self.client_data['plot_no']}\n"
                f"Block: {self.client_data['block']}\n"
                f"Registry Status: {self.client_data.get('registry_status', 'N/A')}\n\n"
                f"Total Price: PKR {int(self.client_data['total_price']):,}\n"
                f"Paid Amount: PKR {int(self.client_data['paid_amount']):,}\n"
                f"Remaining: PKR {remaining:,}\n"
            )
        else:
            self.info_label.text = "No client info available."

    def back_to_simulate(self, *args):
        self.manager.current = "simulate"

class MainApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        Window.clearcolor = (0.05, 0.05, 0.1, 1)
        Window.size = (360, 640)
        Window.borderless = True
        return self.build_screens()

    def on_start(self):
        hide_android_status_bar()

    def build_screens(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignupScreen(name="signup"))
        sm.add_widget(SimulateScreen(name="simulate"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(ResultScreen(name="result"))
        return sm

if __name__ == "__main__":
    MainApp().run()
