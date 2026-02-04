import threading

from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivy.clock import mainthread, Clock
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.relativelayout import MDRelativeLayout

from core.utils.validators import is_password_valid


class Authentification(MDRelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dialog_box = None
        self.running_app = MDApp.get_running_app()

    def _close_dialog_box(self, *args) -> None:
        """
        Cette methode ferme la boîte de dialogue
        :return
        """
        if self.dialog_box:
            self.dialog_box.dismiss()
            self.dialog_box = None

    @mainthread
    def _open_dialog_box(self, title: str, content: str) -> None:
        """
        Cette methode ouvre la boite de dialogue
        :param title: le titre de la bôiye
        :param content: le contenu de la boîte
        """
        if self.dialog_box:
            return

        self.dialog_box = MDDialog(
            title=title,
            text=content,
            radius=[5, 5, 5, 5],
            auto_dismiss=False,
            buttons=[
                MDRaisedButton(
                    text="Fermer",
                    theme_text_color="Custom",
                    text_color="black",
                    on_release=self._close_dialog_box
                )
            ],
        )
        self.dialog_box.open()

    @mainthread
    def go_to_main_screen(self, *args):
        self.ids['password_input'].text = ""
        self.running_app.SCREEN_MANAGER.push('mainScreen')

    def authenticate_user(self, user_password: str) -> None:
        """
        Cette methode authentifie un utilisateur
        :param user_password: le mot de passe de l'utilisateur
        :return None
        """
        if not user_password or not str(user_password).strip():
            return

        def check_password():
            hashed_password = self.running_app.DATABASE_MANAGER.get_access_password()
            if hashed_password:
                result = is_password_valid(hashed_password, user_password)
                self.running_app.hide_spinner()

                if result[0]:
                    self.running_app.MASTER_ACCESS_PASSWORD = user_password
                    Clock.schedule_once(self.go_to_main_screen, 0.1)
                else:
                    self._open_dialog_box(
                        "Échec d'authentification",
                        "Mot de passe incorrect. Veuillez réesseyez."
                    )
            else:
                self.running_app.hide_spinner()
                self._open_dialog_box(
                    "Échec d'authentification",
                    "Une erreur s'est produite lors de l'authentification. Veuillez réesseyez ultérieurement."
                )

        
        self.running_app.show_spinner()
        threading.Thread(target=check_password).start()