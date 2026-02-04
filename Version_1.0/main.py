import os
import sys
import zlib
import bcrypt
import pickle
import base64
from io import BytesIO
import cryptographic_engine
from Cryptodome.Cipher import AES

from kivy.config import Config
from screeninfo import get_monitors


# Obtenir les dimensions de l'écran
SCREEN_WIDTH = get_monitors()[0].width
SCREEN_HEIGHT = get_monitors()[0].height

# Calculer les positions pour centrer la fenêtre
WINDOW_WIDTH = int(SCREEN_WIDTH * 0.85) # Largeur de la fenêtre souhaitée
WINDOW_HEIGHT = int(SCREEN_HEIGHT * 0.85) # Hauteur de la fenêtre souhaitée
LEFT = (SCREEN_WIDTH - WINDOW_WIDTH) // 2
TOP = (SCREEN_HEIGHT - WINDOW_HEIGHT) // 2

# Définir la position et la taille de la fenêtre
Config.set('graphics', 'position', 'custom')
Config.set('graphics', 'left', LEFT)
Config.set('graphics', 'top', TOP)
Config.set('graphics', 'width', WINDOW_WIDTH)
Config.set('graphics', 'height', WINDOW_HEIGHT)
Config.set('kivy', 'exit_on_escape', 0) # exit si la touche Esp est pressée
Config.set('graphics', 'minimum_width', 900)  # la largeur minimal de la fenêtre
Config.set('graphics', 'minimum_height', 600) # la hauteur minimal de la fenêtre


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty, BooleanProperty

from screen_manager import DynamicScreenManager



class ScreenNavigator(DynamicScreenManager):
    pass
class MainApplicationApp(App):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        BASE_DIR = sys._MEIPASS
        DATA_DIR = os.path.dirname(sys.executable)

        # Fermeture du splash screen
        import pyi_splash
        pyi_splash.close()
    else:
        BASE_DIR = DATA_DIR = os.path.dirname(os.path.abspath(__file__))

    DATA_FOLDER = os.path.join(DATA_DIR, 'data')
    MASTER_PWD_FILE = os.path.join(DATA_FOLDER, 'MASTERPASSWORD')
    SECURITY_ISSUES_FILE = os.path.join(DATA_FOLDER, 'RECOVERYQUESTIONS')
    HISTORY_FILE = os.path.join(DATA_FOLDER, 'LOGHISTORY.bin')
    BACKUP_FILE = os.path.join(DATA_FOLDER, 'BACKUP')

    DEFAULT_FONT = os.path.join(BASE_DIR, 'fonts', '12 POST ANTIQUA BOLD   07554.TTF')
    SECOND_FONT = os.path.join(BASE_DIR, 'fonts', '70214___.TTF')
    APP_ICON = os.path.join(BASE_DIR, 'images', 'profil.png')
    MENU_ICON = os.path.join(BASE_DIR, 'images', 'clipart365828.png')
    LOGOUT_ICON = os.path.join(BASE_DIR, 'images', 'logout.png')




    MASTER_PASSWORD = None
    MANAGER = ObjectProperty(None)

    is_master_password_set = False
    is_security_questions_answered_set = False
    security_questions_response = str()
    should_disable_button = BooleanProperty(True)


    POPUP = lambda x1, x2, color: Popup(
        title=str(x1),
        title_align="center",
        title_size=18,
        title_color=get_color_from_hex(color),
        background_color=get_color_from_hex("#606060"),
        size_hint=(.8, .3),
        separator_color=(1, 1, 1, 1),
        auto_dismiss=True,
        content=Label(
            text=str(x2),
            color=color,
            font_size=17,
            pos_hint={"center_x": .5, "center_y": .5}
        )
    )

    APPLICATION_NAME = "Cryptographic Software"
    APPLICATION_GITHUB_LINK = "https://github.com/isaacbumizi-dev/Cryptographic-software"

    ABOUT_APPLICATION = f"""
                    **{APPLICATION_NAME}** est un outil de cryptage des fichiers open source pour windows,
                    conçu pour garantir la sécurité de vos données personnelles. \n
                    Avec une interface conviviale et des algorithmes de cryptage robuste, {APPLICATION_NAME} vous
                    permet de protéger vos données sensibles avec une tranquillité d'esprit totale.\n
                    **Fonctionnalités clés:**\n
                    **-Cryptage des fichiers d'une manière sécurisé:** Protégez vos données avec un algorithmes de 
                    cryptage moderne et reconnus (AES).\n
                    **-Interface intuitive:** Facile à utiliser, même pour les utilisateurs novices en cryptographie\n
                    **-Vitesse de cryptage et de décryptage rapide:** Cryptez et décrypter vos fichiers rapidement
                    et efficacement, sanc compromis sur la sécurité.\n
                    **-Protection par mot de passe:** Protégez vos fichiers avec un mot de passe fort pout une 
                    sécurité accrue.\n
                    {APPLICATION_NAME} est un projet open source. Le code source est disponible sur github, permettant
                    aux utilisateurs de contribuer au développement et d'améliorer l'application.\n
                    **Découvrer {APPLICATION_NAME} et contribuez à sa croissance!**
                    {APPLICATION_GITHUB_LINK}
                    
                    L'utilisation de cette application est gratuite et destinée à un usage personnel uniquement. 
                    Toute utilisation commerciale est interdite.\n
                    **Cette application a été conçue et développée par** Isaac_ Bumizi_ avec la participation de: \n
                    1. AKILIMALI_ MATERANYA_ Nestor_\n
                    2. BAHATI_ MIRINDI_ Chrispin_\n
                    3. BYADUNIA_ EMMANUEL_ Jean-Luc_\n  
                    4. MWENDANGA_ BABU_ Victor_\n
                        """

    def build(self):
        self.title = self.APPLICATION_NAME
        self.icon = self.APP_ICON
        self.MANAGER = ScreenNavigator()

        return self.MANAGER

    def get_masterPassWord(self):
        return self.MASTER_PASSWORD

    def on_start(self):
        try:
            os.mkdir(self.DATA_FOLDER) if not os.path.exists(self.DATA_FOLDER) else None
            os.open(self.HISTORY_FILE, os.O_CREAT) if not os.path.exists(self.HISTORY_FILE) else None
            os.open(self.BACKUP_FILE, os.O_CREAT) if not os.path.exists(self.BACKUP_FILE) else None
            os.open(self.MASTER_PWD_FILE, os.O_CREAT) if not os.path.exists(self.MASTER_PWD_FILE) else None
            os.open(self.SECURITY_ISSUES_FILE, os.O_CREAT) if not os.path.exists(self.SECURITY_ISSUES_FILE) else None

            os.system('attrib +h {}'.format(self.DATA_FOLDER))
            with open(self.BACKUP_FILE, 'rb') as f:
                pass
        except PermissionError:
            Popup(
                title=str("Erreur au démarage"),
                title_align="center",
                title_size=18,
                title_color=get_color_from_hex("#C94F4F"),
                background_color=get_color_from_hex("#606060"),
                size_hint=(1, 1),
                separator_color=(1, 1, 1, 1),
                auto_dismiss=False,
                content=Label(
                    text="L'application que vous essayez de lancer nécessite des privilèges d'administrateur pour accèder "
                         "à certaines ressources du système. \n"
                         "Veuillez vous connecter en tant qu'administrateur ou contacter votre administrateur"
                         "système pour obtenir de l'aide.",
                    color=get_color_from_hex("#C94F4F"),
                    font_size=16,
                    valign="center",
                    halign="center"
                )
            ).open()
        except Exception:
            self.stop()
        else:
            self.check_user_exist()

    def check_user_exist(self):
        """
        Cette methode permet de vérifier s'il existe ne fichier où est stocké le mot de passe de sécurité
        """
        pwd_data = None
        issues_data = None
        try:
            with open(self.MASTER_PWD_FILE, "rb") as pw_file:
                pwd_pickle_object = pickle.Unpickler(pw_file)
                pwd_data = pwd_pickle_object.load()
        except EOFError:
            self.MANAGER.push("createUserScreen")

        try:
            with open(self.SECURITY_ISSUES_FILE, "rb") as sec_file:
                pickle_object = pickle.Unpickler(sec_file)
                issues_data = pickle_object.load()
        except EOFError:
            self.MANAGER.push("createUserScreen")

        if not pwd_data or not issues_data:
            self.MANAGER.push("createUserScreen")
        else:
            self.MANAGER.push("authentificationScreen")


    def define_masterPassword(self, arg1, arg2):
        """
        Cette methode permet de definir le mot de passe maitre
        """
        def hash_pwd(password):
            sel = bcrypt.gensalt()
            hach = bcrypt.hashpw(password.encode(), sel)
            return hach

        def define_paswd(*args):
            try:
                with open(self.MASTER_PWD_FILE, "wb") as pw_file:
                    pickle_object = pickle.Pickler(pw_file)
                    pickle_object.dump(hash_pwd(arg2))
            except Exception as e:
                MainApplicationApp.POPUP("Erreur", str(e), "#C94F4F").open()
                try: os.remove(self.MASTER_PWD_FILE)
                except: pass
            else:
                self.MASTER_PASSWORD = arg2
                self.is_master_password_set = True
                MainApplicationApp.POPUP("", "Mot de passe defini avec succès.", "#1F753A").open()

                if self.is_security_questions_answered_set == self.is_master_password_set == True:
                    self.should_disable_button = False

        self.is_master_password_set = False
        if not arg1 or not arg2:
            MainApplicationApp.POPUP("Valeur incorrect",
                                     "Veuillez saisir un mot de passe et confirmer votre mot de passe", "#C94F4F").open()
        elif arg1 != arg2:
            MainApplicationApp.POPUP("Valeur incorrect",
                                     "Les mots de passe saisis ne sont pas identique. "
                                     "Veuillez saisir le même mot de passe dans les deux champs.", "#C94F4F").open()
        else:
            layout = BoxLayout(orientation="vertical", padding=[5, 2, 5, 2])
            layout.add_widget(Label(
                    text="Veuillez garder votre mot de passe en sécurité. \n"
                         "Quiconque a accès à ce mot de passe peut accéder à l'application et voir toutes vos sauvegardes.\n"
                         "Noter votre mot de passe quelque part et garde le dans un endroit où vous pouvez le recuperer \n"
                         "en cas d'oublie du mot de passe.\n"
                         "Vous pouvez restaurer le mot de passe, mais vous ne pouvez pas récuperer les sauvegardes une fois le mot de passe perdue",
                    color=get_color_from_hex("#C94F4F"),
                    font_size=15,
                    halign='center',
                    valign='center',
                    pos_hint={"center_x": .5, "center_y": .5}
                ))

            popUp = Popup(
                title=str('Attention !'),
                title_align="center",
                title_size=18,
                title_color=get_color_from_hex("#C94F4F"),
                background_color=get_color_from_hex("#606060"),
                size_hint=(.8, .4),
                separator_color=(1, 1, 1, 1),
                auto_dismiss=False,
                content=layout
            )
            bouton = Button(text="OK", size_hint=(1, .2))
            bouton.bind(on_release=popUp.dismiss)
            bouton.bind(on_release=define_paswd)
            layout.add_widget(bouton)
            popUp.open()



    def define_security_issues(self, answers):
        """
        Cette methode permet de définir les questions des sécurité
        """
        def hash_sc(q):
            sel = bcrypt.gensalt()
            hach = bcrypt.hashpw(q.encode(), sel)
            return hach

        self.is_security_questions_answered_set = False
        if not answers[0] or not answers[1] or not answers[2] or not answers[3]:
            MainApplicationApp.POPUP("Valeur incorrect",
                                     "Veuillez remplir tout les champs et réessayez",
                                     "#C94F4F").open()
        else:
            ans1 = hash_sc(answers[0].lower())
            ans2 = hash_sc(answers[1].lower())
            ans3 = hash_sc(answers[2].lower())
            ans4 = hash_sc(answers[3].lower())

            try:
                with open(self.SECURITY_ISSUES_FILE, "wb") as sc_file:
                    pick = pickle.Pickler(sc_file)
                    pick.dump({
                        "Quel est votre couleur préférée ?": ans1,
                        "Quel est le nom de votre ville natale ?": ans2,
                        "Quel est votre sport préféré ?": ans3,
                        "Quel est le nom de la première école que vous avez frequenté ?": ans4
                    })
            except Exception as e:
                MainApplicationApp.POPUP("Erreur", str(e), "#C94F4F").open()
                try: os.remove(self.SECURITY_ISSUES_FILE)
                except: pass
            else:
                self.is_security_questions_answered_set = True
                self.security_questions_response = str((answers[0]+answers[1]+answers[2]+answers[3]).lower())
                MainApplicationApp.POPUP("", "Questions de sécurité definient avec succès.", "#1F753A").open()


            if self.is_security_questions_answered_set == self.is_master_password_set == True:
                self.should_disable_button = False

    def encrypt_and_save_master_password(self):
        """
        Cette methode permet de chiffrer le mot de passe d'authentification et de le stocker dans un fichier
        """
        try:
            compressed_text = zlib.compress(self.MASTER_PASSWORD.encode())

            session_key = cryptographic_engine.derive_cryptographic_key(self.security_questions_response, 256)
            cipher_aes = AES.new(session_key, AES.MODE_EAX)
            cipher_text, tag = cipher_aes.encrypt_and_digest(compressed_text)

            msg_payload = cipher_aes.nonce + tag +cipher_text
            encrypted = base64.encodebytes(msg_payload)

            with open(self.MASTER_PWD_FILE, "ab") as pw_file:
                pickle_object = pickle.Pickler(pw_file)
                pickle_object.dump(encrypted)
        except:
            pass
        else:
            self.security_questions_response = str()


    def isPasswordValid(self, password):
        """
        Cette methode permet de vérifier la validité du mot de passe saisit par l'utilisateur
        """
        passwd = str(password.text)
        password.text = ""
        try:
            pwd = None
            with open(self.MASTER_PWD_FILE, "rb") as pw_file:
                pickle_object = pickle.Unpickler(pw_file)
                pwd = pickle_object.load()

            if bcrypt.checkpw(passwd.encode('utf-8'), pwd):
                self.MANAGER.push("mainScreen")
                self.MASTER_PASSWORD = passwd
            else:
                MainApplicationApp.POPUP("Mot de passe incorrect",
                                         "Le mot de passe que vous avez saisit est incorrect, veuillez réesseyez",
                                     "#C94F4F").open()
        except Exception:
            self.check_user_exist()

    def restore_password(self, arg):
        popUp = lambda title, message_text, color: Popup(
                title=title,
                title_align="center",
                title_color=get_color_from_hex(color),
                title_size=18,
                background_color=get_color_from_hex("#606060"),
                separator_color=get_color_from_hex("#463C4B"),
                size_hint=(.6, .2),
                auto_dismiss=True,
                content=Label(
                    text=message_text,
                    color=get_color_from_hex(color),
                    font_size=17,
                    pos_hint={"center_x": .5, "center_y": .5}
                )
            )

        isAllAnswersTrue = False
        with open(self.SECURITY_ISSUES_FILE, "rb") as file:
            pickle_object = pickle.Unpickler(file)
            data = pickle_object.load()

            for i, dt in enumerate(data.items()):
                if bcrypt.checkpw((arg[i].lower()).encode('utf-8'), dt[1]):
                    isAllAnswersTrue = True
                    self.security_questions_response += str(arg[i].lower())
                else:
                    isAllAnswersTrue = False
                    self.security_questions_response = str()
                    break

        if isAllAnswersTrue:
            try:
                backUp_encrypted_key = None
                with open(self.MASTER_PWD_FILE, 'rb') as file:
                    pick = pickle.Unpickler(file)
                    while True:
                        try:backUp_encrypted_key = pick.load()
                        except EOFError: break

                encrypted_bytes = BytesIO(base64.decodebytes(backUp_encrypted_key))

                nonce = encrypted_bytes.read(16)
                tag = encrypted_bytes.read(16)
                cipher_text = encrypted_bytes.read()

                session_key = cryptographic_engine.derive_cryptographic_key(self.security_questions_response, 256)
                cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
                decrypted = cipher_aes.decrypt_and_verify(cipher_text, tag)
                plaintext = zlib.decompress(decrypted)

                popUp("Restauration",
                      f"Le mot de passe d'authentification est : {plaintext.decode()}",
                      "FFFFFF").open()

            except Exception as e:
                popUp("Erreur", str(e), "#C94F4F").open()
        else:
            popUp("Erreur",
                  "Une ou plusieurs réponse aux question sont fausses, veuillez réesseyez",
                  "#C94F4F").open()


if __name__ == "__main__":
    MainApplicationApp().run()
