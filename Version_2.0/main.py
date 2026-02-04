from kivy.config import Config
from screeninfo import get_monitors


# Obtenir les dimensions de l'écran
SCREEN_WIDTH = get_monitors()[0].width
SCREEN_HEIGHT = get_monitors()[0].height

# Calculer les positions pour centrer la fenêtre
WINDOW_WIDTH = int(SCREEN_WIDTH * 0.85)
WINDOW_HEIGHT = int(SCREEN_HEIGHT * 0.85)
LEFT = (SCREEN_WIDTH - WINDOW_WIDTH) // 2
TOP = (SCREEN_HEIGHT - WINDOW_HEIGHT) // 2

# Définir la position et la taille de la fenêtre
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', LEFT)
Config.set('graphics', 'top', TOP)
Config.set('graphics', 'width', WINDOW_WIDTH)
Config.set('graphics', 'height', WINDOW_HEIGHT)
Config.set('kivy', 'exit_on_escape', 0)
Config.set('graphics', 'minimum_width', 1161)
Config.set('graphics', 'minimum_height', 652)


import os
import sys

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import ObjectProperty


from gui.components.spinner import CustomSpinner
from gui.components.screenManager import DynamicScreenManager
from core.database.database import DatabaseManager

class ScreenNavigator(DynamicScreenManager):
    pass


class MainApplicationApp(MDApp):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        BASE_DIR = sys._MEIPASS
        EXC_DIR = os.path.dirname(sys.executable)

        # Fermeture du splash screen
        import pyi_splash
        pyi_splash.close()
    else:
        BASE_DIR = EXC_DIR = os.path.dirname(os.path.abspath(__file__))
    
    DATA_STORGAGE = os.path.join(EXC_DIR, 'data')

    APP_ICON = os.path.join(BASE_DIR, 'assets', 'images', 'profil.png')

    SCREEN_MANAGER = ObjectProperty(None)
    APPLICATION_NAME = "Lock Shield - Gestionnaire de Sécurité"

    MASTER_ACCESS_PASSWORD = None
    DATABASE_MANAGER = DatabaseManager(db_path=DATA_STORGAGE)

    SPINNER_POPUP = Popup(
        title=str(),
        size_hint=(None, None),
        size=(100, 100),
        background_color=(0,0,0,0),
        separator_color=(0,0,0,0),
        auto_dismiss=False
    )

    ABOUT_CONTENT = """
    A PROPOS DE LOCK SHIELD - VERSION 2.0
    
    Application de sécurité complète pour le chiffrement et la protection de vos fichiers sensibles.
    
    CARACTERISTIQUES PRINCIPALES
    . Chiffrement AES 256-bit sécurisé
    . Gestionnaire de fichiers intégré
    . Historique détaillé des opérations
    . Sauvegarde automatique des clés
    . Export PDF de l'historique des opérations
    
    TECHNOLOGIES UTILISEES
    Python - Kivy - KivyMD - SQLite - Cryptographie AES
    
    DEVELOPPE PAR
    Isaac Bumizi
    Passionné de l'informatique et de la cybersécurité
    
    SUPPORT TECHNIQUE
    Email: isaac.bumizi.officiel@gmail.com
    GitHub: https://github.com/isaacbumizi-dev
    Repository GitHub: https://github.com/isaacbumizi-dev/Lock-Shield.git
    
    Licence MIT - Open Source
    © 2026 Lock Shield - Tous droits réservés
    """
    def build(self):
        self.title = self.APPLICATION_NAME
        self.icon = self.APP_ICON

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        self.theme_cls.primary_hue = "800"

        self.load_all_kv_files(path_to_directory="gui/style/")

        self.SCREEN_MANAGER = ScreenNavigator()
        return self.SCREEN_MANAGER


    def on_start(self):
        os.makedirs(self.DATA_STORGAGE, exist_ok=True)
        self.DATABASE_MANAGER.initialize_database()

        if self.DATABASE_MANAGER.is_configuration_exist():
            self.SCREEN_MANAGER.push("authentificationScreen")
        else:
            self.SCREEN_MANAGER.push("userConfigScreen")

    def load_all_kv_files(self, path_to_directory: str) -> None:
        Builder.load_file(os.path.join(path_to_directory, "userconfiguration.kv"))
        Builder.load_file(os.path.join(path_to_directory, "authentication.kv"))
        Builder.load_file(os.path.join(path_to_directory, "passwordrestoration.kv"))
        Builder.load_file(os.path.join(path_to_directory, "cryptowindow.kv"))
        Builder.load_file(os.path.join(path_to_directory, "history.kv"))
        Builder.load_file(os.path.join(path_to_directory, "restoration.kv"))



    def show_spinner(self):
        self.hide_spinner()

        content = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            padding=10,
            size_hint=(None, None),
            size=(100, 100)
        )
        content.add_widget(CustomSpinner())
        self.SPINNER_POPUP.content = content
        self.SPINNER_POPUP.open()

    def hide_spinner(self):
        if self.SPINNER_POPUP is not None:
            self.SPINNER_POPUP.dismiss()



if __name__ == "__main__":
    MainApplicationApp().run()
