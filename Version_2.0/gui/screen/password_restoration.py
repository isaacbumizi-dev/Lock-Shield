import threading

from kivymd.app import MDApp
from kivy.clock import mainthread
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.relativelayout import MDRelativeLayout

from core.utils.validators import is_any_empty, hash_content
from core.crypto.cryptoEngine import decrypt_password


class Restoration(MDRelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dialog_box = None
        self.is_password_restored = False
        self.running_app = MDApp.get_running_app()

    def _close_dialog_box(self, *args) -> None:
        """
        Cette methode ferme la boîte de dialogue
        :return
        """
        if self.dialog_box is not None:
            self.dialog_box.dismiss()
            self.dialog_box = None

        if self.is_password_restored is True:
            self.running_app.SCREEN_MANAGER.push("authentificationScreen")

    @mainthread
    def _open_dialog_box(self, title:str, content:str) -> None:
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


    def restore_password(self) -> None:
        """
        Cette methode restore le mot de passe de l'utilisateur
        :return
        """
        @mainthread
        def show_restored_password(password) -> None:
            self.is_password_restored = True
            self._open_dialog_box(
                "Restauration du mot de passe",
                f"Votre mot de passe est : {password}"
            )

        def restore() -> None:
            try:
                prefer_color = self.ids['color_id'].text
                born_town = self.ids['town_id'].text
                first_language = self.ids['language_id'].text
                first_school = self.ids['school_id'].text

                if is_any_empty(
                        prefer_color,
                        born_town,
                        first_school,
                        first_language,
                ):
                    self.is_password_restored = False
                    self.running_app.hide_spinner()
                    self._open_dialog_box(
                        "Échec de restauration",
                        "Tous les champs sont obligatoires. Veuillez recommencer."
                    )
                else:
                    encrypted_password = self.running_app.DATABASE_MANAGER.get_encrypted_password()
                    if encrypted_password:
                        decryption_key = f"{prefer_color.strip()}{born_town.strip()}{first_language.strip()}{first_school.strip()}"

                        decrypted_password = decrypt_password(
                            encrypted_password=encrypted_password,
                            decryption_key=decryption_key.lower()
                        )
                        if decrypted_password is None:
                            self.is_config_defined = False
                            self._open_dialog_box(
                                "Échec de restauration",
                                "Une ou plusieurs réponses sont incorrectes. Veuillez vérifier vos informations."
                            )
                        else:
                            show_restored_password(decrypted_password)

            except Exception as e:
                self.is_config_defined = False
                self._open_dialog_box(
                    "Échec de restauration",
                    str(e)
                )
            finally:
                self.running_app.hide_spinner()


        self.running_app.show_spinner()
        threading.Thread(target=restore).start()