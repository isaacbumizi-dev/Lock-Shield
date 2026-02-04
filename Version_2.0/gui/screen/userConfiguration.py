import threading

from kivy.clock import mainthread
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.relativelayout import MDRelativeLayout

from core.utils.validators import is_any_empty, hash_content
from core.crypto.cryptoEngine import encrypt_password


class UserConfiguration(MDRelativeLayout):
    def __init__(self, **Kwargs):
        super().__init__(**Kwargs)

        self.dialog_box = None
        self.is_config_defined = False
        self.running_app = MDApp.get_running_app()


    def _close_dialog_box(self, *args) -> None:
        """
        Cette methode ferme la boîte de dialogue
        :return
        """
        if self.dialog_box:
            self.dialog_box.dismiss()
            self.dialog_box = None

        if self.is_config_defined is True:
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

    def save_user_config(self) -> None:
        """
        Cette methode permet de sauvegarder(définir) les configurations de l'utilisateur
        :param
        :return None
        """
        def save_config_on_db() -> None:
            """
            Cette fonction sert de socle pour un thread separés qui se charge du stockage de config
            :return None
            """
            prefer_color = self.ids['color_id'].text
            born_town = self.ids['town_id'].text
            first_language = self.ids['language_id'].text
            first_school = self.ids['school_id'].text
            password = self.ids['password_id'].text
            password_confirmation = self.ids['password_conf_id'].text

            if is_any_empty(
                    prefer_color,
                    born_town,
                    first_school,
                    first_language,
                    password,
                    password_confirmation
            ):
                self.is_config_defined = False
                self.running_app.hide_spinner()
                self._open_dialog_box(
                    "Échec de configuration",
                    "Tous les champs sont obligatoires. Veuillez recommencer."
                )

            else:
                if password.strip() != password_confirmation.strip():
                    self.is_config_defined = False
                    self.running_app.hide_spinner()
                    self._open_dialog_box(
                        "Échec de configuration",
                        "Les mots de passe ne correspondent pas. Veuillez réessayer."
                    )
                else:
                    try:
                        hashed_password = hash_content(password.strip())
                        hashed_prefer_color = hash_content(prefer_color.strip().lower())
                        hashed_born_town = hash_content(born_town.strip().lower())
                        hashed_first_language = hash_content(first_language.strip().lower())
                        hashed_first_school = hash_content(first_school.strip().lower())

                        # Chiffrement du mot de paase avec les réponses aux questions de sécurité
                        # Pour une eventuelle restauration en cas d'oubli du mot de pass
                        encrypion_key = f"{prefer_color.strip()}{born_town.strip()}{first_language.strip()}{first_school.strip()}"
                        encrypted_password = encrypt_password(
                            password = (password.strip()).encode('utf-8'),
                            encryption_key = encrypion_key.lower()
                        )

                        if encrypted_password is None:
                            self.is_config_defined = False
                            self._open_dialog_box(
                                "Échec de configuration",
                                "Une erreur s'est produite lors du traitement des données. Veuillez réessayer."
                            )
                        else:
                            db = self.running_app.DATABASE_MANAGER.add_new_config(
                                password=hashed_password,
                                prefer_color=hashed_prefer_color,
                                born_town=hashed_born_town,
                                first_school=hashed_first_school,
                                first_language=hashed_first_language,
                                encrypted_password=encrypted_password
                            )

                            if db is True:
                                self.is_config_defined = True
                                self._open_dialog_box(
                                    "Configuration réussie",
                                    "Paramètres de configuration définis avec succès."
                                )

                            else:
                                self.is_config_defined = False
                                self._open_dialog_box("Échec de configuration", "Échec de l'enregistrement dans la base de données.")

                    except Exception as e:
                        self.is_config_defined = False
                        self._open_dialog_box(
                            "Échec de configuration",
                            str(e)
                        )
                    finally:
                        self.running_app.hide_spinner()

        self.running_app.show_spinner()
        threading.Thread(target=save_config_on_db).start()

