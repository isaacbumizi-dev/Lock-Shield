from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.relativelayout import MDRelativeLayout
from kivy.properties import StringProperty, NumericProperty, ObjectProperty

from core.utils.validators import is_password_valid
from core.crypto.cryptoEngine import decrypt_password


class RestorationViewClass(MDBoxLayout):
    id = NumericProperty(None)
    num = StringProperty(None)
    date = StringProperty(None)
    hash = StringProperty(None)
    file_name = StringProperty(None)
    parent_instance = ObjectProperty(None)


class RestorationWindow(MDRelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.running_app = MDApp.get_running_app()

        Clock.schedule_once(self.add_data, 0.5)


    def add_data(self, *args):
        """
        Cette methode ajouterr les données sur la fêetre
        :return
        """
        try:
            self.ids['restauration_viewclass_id'].data = []
            backup_content = self.running_app.DATABASE_MANAGER.get_backup()

            if not backup_content:
                self.ids['restauration_viewclass_id'].data.append({
                    "viewclass": "MDLabel",
                    "text": "Aucune sauvegarde disponible",
                    "valign": "center",
                    "halign": "center"
                })
                return

            for index, data in enumerate(backup_content):
                self.ids['restauration_viewclass_id'].data.append({
                    "viewclass": "RestorationViewClass",
                    "num": str(index + 1),
                    "id": data.get('id'),
                    "hash": data.get('key').decode('utf-8'),
                    "date": data.get('date'),
                    "file_name": data.get('file'),
                    "parent_instance": self
                })

        except Exception as e:
            self.ids['restauration_viewclass_id'].data = []
            self.ids['restauration_viewclass_id'].data.append({
                "viewclass": "MDLabel",
                "text": str(e),
                "valign": "center",
                "halign": "center"
            })

    def restaure_encryption_key(self, key_id):
        """
        Cette methode permet de restaurer une clé de chiffrement d'un fichier
        :param key_id: l'id de la clé dans la base des données
        :return
        """
        dialog = lambda title, content: MDDialog(
            title=str(title),
            text=str(content),
            radius=[5,5,5,5],
            auto_dismiss=True
        ).open()

        def _authenticate_user(*args):
            if self.authentication_dialog_box:
                self.authentication_dialog_box.dismiss()

            hashed_password = self.running_app.DATABASE_MANAGER.get_access_password()
            if hashed_password:
                result = is_password_valid(hashed_password, self.text_input.text)
                if result[0]:
                    backup_key = self.running_app.DATABASE_MANAGER.get_backup_key(key_id)
                    if backup_key:
                        decrypted_key = decrypt_password(backup_key[0], self.text_input.text)
                        try:
                            import pyperclip
                            pyperclip.copy(decrypted_key)
                            dialog("Restauration réussie", f"Clé restaurée: {decrypted_key}\n\n La clé à été copiée dans le presse papier")
                        except Exception:
                            dialog("Restauration réussie", f"La clé de chiffrement est : {decrypted_key}")
                    else:
                        dialog("Erreur de restauration", "Une erreur est survenue lors de la restauration. Veuillez réessayer ultérieurement.")
                else:
                    dialog("Échec d'authentification", "Le mot de passe saisi est invalide.")
            else:
                dialog("Échec d'authentification", "Une erreur est survenue lors de l'authentification. Veuillez réessayer ultérieurement.")

        layout = MDRelativeLayout(
            padding=[5, 2, 5, 2],
            md_bg_color=get_color_from_hex("#2C2C2C"),
            radius=[5, ]
        )

        self.authentication_dialog_box = Popup(
            title="",
            background_color=(0, 0, 0, 0),
            separator_color=(0, 0, 0, 0),
            size_hint=(None, None),
            size=(522.45, 258.6),
            auto_dismiss=True,
            content=layout
        )
        self.text_input = MDTextField(
            multiline=False,
            size_hint_x=.9,
            password=True,
            mode="rectangle",
            radius=[3, ],
            hint_text="Mot de passe",
            pos_hint={"center_x": .5, "center_y": .50},
            on_text_validate=_authenticate_user
        )

        layout.add_widget(self.text_input)
        button = MDRaisedButton(
            text="Valider",
            size_hint=(.8, .2),
            pos_hint={"center_x": .5, "center_y": .20}
        )
        button.bind(on_release=_authenticate_user)
        layout.add_widget(button)
        self.authentication_dialog_box.open()


    def erase_backup(self):
        """
        Cette methode supprimer la sauvegarde des clés de chiffrement
        :return
        """
        if len(self.ids['restauration_viewclass_id'].data) == 0:
            return

        dialog_box = None

        def _close_dialog_box(*args):
            if dialog_box:
                dialog_box.dismiss()

        def _erase_backup():
            _close_dialog_box()
            erase_result = self.running_app.DATABASE_MANAGER.erase_back()
            if erase_result:
                self.add_data()

        def _authenticate_user(*args):
            if self.authentication_dialog_box:
                self.authentication_dialog_box.dismiss()

            hashed_password = self.running_app.DATABASE_MANAGER.get_access_password()
            if hashed_password:
                result = is_password_valid(hashed_password, self.text_input.text)
                if result[0]:
                    _erase_backup()
                else:
                    MDDialog(
                        title="Erreur de suppression",
                        text="Le mot de passe saisi est invalide.",
                        radius=[5,5,5,5],
                        auto_dismiss=True
                    ).open()

            else:
                MDDialog(
                    title="Échec d'authentification",
                    text="Une erreur est survenue lors de l'authentification. Veuillez réessayer ultérieurement.",
                    radius=[5, 5, 5, 5],
                    auto_dismiss=True
                ).open()

        def _confirm_user_identity(*args):
            _close_dialog_box()

            layout = MDRelativeLayout(
                padding=[5, 2, 5, 2],
                md_bg_color=get_color_from_hex("#2C2C2C"),
                radius=[5,]
            )

            self.authentication_dialog_box = Popup(
                title="",
                background_color=(0,0,0,0),
                separator_color=(0,0,0,0),
                size_hint=(None, None),
                size= (522.45, 258.6),
                auto_dismiss=True,
                content=layout
            )
            self.text_input = MDTextField(
                multiline=False,
                size_hint_x= .9,
                password=True,
                mode="rectangle",
                radius=[3, ],
                hint_text="Mot de passe",
                pos_hint={"center_x": .5, "center_y": .50},
                on_text_validate=_authenticate_user
            )

            layout.add_widget(self.text_input)
            button = MDRaisedButton(
                text="Valider",
                size_hint= (.8, .2),
                pos_hint={"center_x": .5, "center_y": .20}
            )
            button.bind(on_release=_authenticate_user)
            layout.add_widget(button)
            self.authentication_dialog_box.open()


        dialog_box = MDDialog(
            title="Confirmation de suppression",
            text="Voulez-vous supprimer la sauvegarde des clés de chiffrement ?",
            radius=[5, 5, 5, 5],
            auto_dismiss=False,
            buttons=[
                MDRaisedButton(
                    text="Non",
                    theme_text_color="Custom",
                    text_color="black",
                    on_release=_close_dialog_box
                ),
                MDRaisedButton(
                    text="Oui",
                    theme_text_color="Custom",
                    text_color="black",
                    on_release=_confirm_user_identity
                )
            ],
        )
        dialog_box.open()