import os
import time
import threading

from kivymd.app import MDApp
from kivy.uix.popup import Popup
from kivy.clock import mainthread
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton


from core.crypto.cryptoEngine import (
    encrypt_password,
    encrypt_file,
    decrypt_file,
    derive_crypto_key,
    get_algorithm_signature
)



class EncryptionOptions(MDBoxLayout):
    LAYOUT_ICON = StringProperty("file-lock-outline")
    def __init__(self, parent_instance, **kwargs):
        super().__init__(**kwargs)


        self.parent_instance = parent_instance

        if self.parent_instance.ids['file_target_checkbox'].active:
            self.LAYOUT_ICON = "file-lock-outline"
        else:
            self.LAYOUT_ICON = "folder-lock-outline"


    def close_popup(self) -> None:
        if hasattr(self.parent_instance, "close_config_popup"):
            self.parent_instance.close_config_popup()

    def on_action(self) -> None:
        """
        Cette methode verifie s'il existe des valeurs dans les checkbox et le TextEdit pour active le bouton
        de validation
        :return
        """
        cbc_algo_checkbox = self.ids['cbc_checkbox'].active
        cfb_algo_checkbox = self.ids['cfb_checkbox'].active
        ofb_algo_checkbox = self.ids['ofb_checkbox'].active

        key_size_checbox1 = self.ids['128_checkbox'].active
        key_size_checbox2 = self.ids['192_checkbox'].active
        key_size_checbox3 = self.ids['256_checkbox'].active

        enc_key_textedit = self.ids['enc_key'].text

        if all(v is False for v in [cbc_algo_checkbox, cfb_algo_checkbox, ofb_algo_checkbox]):
            self.ids['validate_button'].disabled = True
        elif all(v is False for v in [key_size_checbox1, key_size_checbox2, key_size_checbox3]):
            self.ids['validate_button'].disabled = True
        elif enc_key_textedit is None or not str(enc_key_textedit).strip():
            self.ids['validate_button'].disabled = True
        else:
            self.ids['validate_button'].disabled = False


    def generate_encryption_key(self):
        """
        Cette methode genere une seire de lettre aléatoire qui serve de la clé de chiffrement
        :return
        """
        import secrets
        import string

        text_edit = self.ids['enc_key']

        password = ""
        text_edit.text = ""
        characters = string.ascii_letters + string.digits + string.punctuation
        for _ in range(32):
            password += ''.join(secrets.choice(characters))

        text_edit.text = password


    def validate_parameters(self):
        """
        Cette methode valide les parametres de chiffrement saisit par l'utilisateur
        :return
        """
        cbc_algo_checkbox = self.ids['cbc_checkbox'].active
        cfb_algo_checkbox = self.ids['cfb_checkbox'].active
        ofb_algo_checkbox = self.ids['ofb_checkbox'].active

        key_size_checbox1 = self.ids['128_checkbox'].active
        key_size_checbox2 = self.ids['192_checkbox'].active
        key_size_checbox3 = self.ids['256_checkbox'].active

        enc_key_textedit = self.ids['enc_key'].text

        encryption_algorithm = None
        key_size = None

        if cbc_algo_checkbox is True:
            encryption_algorithm = "AES_CBC"
        elif cfb_algo_checkbox is True:
            encryption_algorithm = "AES_CFB"
        elif ofb_algo_checkbox is True:
            encryption_algorithm = "AES_OFB"

        if key_size_checbox1 is True:
            key_size = 128
        elif key_size_checbox2 is True:
            key_size = 192
        elif key_size_checbox3 is True:
            key_size = 256

        if hasattr(self.parent_instance, "define_encryption_options"):
            self.parent_instance.define_encryption_options(
                encryption_algorithm=encryption_algorithm,
                key_size=key_size,
                encryption_key=enc_key_textedit.strip()
            )

class DecryptionOptions(MDBoxLayout):
    LAYOUT_ICON = StringProperty("file-lock-open-outline")
    def __init__(self, parent_instance, **kwargs):
        super().__init__(**kwargs)

        self.parent_instance = parent_instance

        if self.parent_instance.ids['file_target_checkbox'].active:
            self.LAYOUT_ICON = "file-lock-open-outline"
        else:
            self.LAYOUT_ICON = "folder-lock-open-outline"

    def close_popup(self):
        if hasattr(self.parent_instance, "close_config_popup"):
            self.parent_instance.close_config_popup()

    def on_textEdit(self):
        """
        Cette methode verifie s'il existe quelque chose dans le textEdit pour actvie
        le bouton de validation
        :return
        """
        textEdit = self.ids['dec_key'].text

        if textEdit is None or not str(textEdit).strip():
            self.ids['validate_button'].disabled = True
        else:
            self.ids['validate_button'].disabled = False

    def define_dec_key(self) -> None:
        """
        Cette methode definie la clé de dechiffrement
        :return
        """
        if hasattr(self.parent_instance, "define_decryption_key"):
            self.parent_instance.define_decryption_key(
                decryption_key = str(self.ids['dec_key'].text).strip()
            )


class CryptoWindow(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.encryption_algorithm = None
        self.encryption_key_size = None
        self.encryption_key = None

        self.decryption_key = None

        self.dialog_box = None
        self.config_popup = None
        self.running_app = MDApp.get_running_app()


    def define_encryption_options(self, encryption_algorithm, key_size, encryption_key) -> None:
        """
        Cette methode define les options de chiffrement choisit par l'utilisateur
        :param encryption_algorithm: l'algorithme de chiffrement
        :param key_size: la longeur de la clé à utilisé lors du chiffrement
        :param encryption_key: la clé de chiffrement
        """
        self.encryption_algorithm = encryption_algorithm
        self.encryption_key_size = key_size
        self.encryption_key = encryption_key

        if self.encryption_algorithm and self.encryption_key_size and self.encryption_key:
            self.close_config_popup()

    def define_decryption_key(self, decryption_key) -> None:
        """
        Cette methode definie la clé de déchiffrement
        :param decryption_key: la clé de déchiffrement
        :return
        """
        self.decryption_key = decryption_key

        if self.decryption_key is not None:
            self.close_config_popup()

    def _close_dialog_box(self, *args) -> None:
        """
        Cette methode ferme la boîte de dialogue
        :return
        """
        if self.dialog_box:
            self.dialog_box.dismiss()
            self.dialog_box = None

    def close_config_popup(self, *args) -> None:
        """
        Cette methode ferme le popup des options de configuration
        :return
        """
        if self.config_popup:
            self.config_popup.dismiss()
            self.config_popup = None

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

    def open_crypto_config_dialog(self):
        """
        Cette methode ouvre la boite de dialogue des options de configuration pour le processus de
        chiffrement/Déchiffrement
        :return
        """
        self.config_popup = Popup(
            title="",
            size_hint=(None, None),
            size=(760, 590) if self.ids['enc_operation_checkbox'].active else (520, 340),
            auto_dismiss=True,
            background_color=(0,0,0,0),
            separator_color=get_color_from_hex("FEA674"),
            pos_hint={"center_x": .5, "center_y": .5},
            content=EncryptionOptions(self) if self.ids['enc_operation_checkbox'].active else DecryptionOptions(self)
        )
        self.config_popup.open()

    @staticmethod
    def _get_child_number_in_directory(path):
        """
        Cette methode retrouve le nombre des fichiers contenus dans un dossier et met à jour la progressBar
        :param path: le chemin vers le dossier
        :return le nombre des fichiers dnas le dossize
        """
        nb = 0
        for path, dirs, files in os.walk(path):
            for _ in files:
                nb += 1
        return nb

    @staticmethod
    def _check_encryption_status(path) -> bool:
        """
        Cette methode verifie si un fichier n'est pas encore chiffrer avant de lancer une nouvelle operation
        :param path: le chemin d'access vers le fichier
        :return True si chiffré False si non
        """
        with open(path, "rb") as input_file:
            signature = input_file.read(32)

        return True if signature in get_algorithm_signature() else False

    @staticmethod
    def _get_algorithm_signature(algorithm, key_size) -> str:
        """
        Cette methode renvoie la signature d'un algoritheme
        :param: l'algorithme recherché
        :param key_size: la taille de la clé de l'algorithme
        :return: la signature de l'algorithme
        """
        match algorithm:
            case "AES_CBC":
                match key_size:
                    case 128:
                        return get_algorithm_signature()[3]
                    case 192:
                        return get_algorithm_signature()[4]
                    case 256:
                        return get_algorithm_signature()[5]
            case "AES_CFB":
                match key_size:
                    case 128:
                        return get_algorithm_signature()[0]
                    case 192:
                        return get_algorithm_signature()[1]
                    case 256:
                        return get_algorithm_signature()[2]
            case "AES_OFB":
                match key_size:
                    case 128:
                        return get_algorithm_signature()[6]
                    case 192:
                        return get_algorithm_signature()[7]
                    case 256:
                        return get_algorithm_signature()[8]

    @staticmethod
    def _extract_key_length_and_algorithm(file_path) -> tuple:
        """
        Cette methode extrait d'un fichier la longeur de la clé de chiffremnt et de l'algorithme utilisé
        avant Déchiffrement
        :return l'algo et la key_lenght
        """
        with open(file_path, 'rb') as file:
            dt = file.read(32)

        signatures = get_algorithm_signature()
        try:
            dt_index = signatures.index(dt)
            match dt_index:
                case 0: return "AES_CFB", 128
                case 1: return "AES_CFB", 192
                case 2: return "AES_CFB", 256
                case 3: return "AES_CBC", 128
                case 4: return "AES_CBC", 192
                case 5: return "AES_CBC", 256
                case 6: return "AES_OFB", 128
                case 7: return "AES_OFB", 192
                case 8: return "AES_OFB", 256
        except Exception:
            return None, None
    @mainthread
    def _update_operation_label_text(self, new_text: str, is_error: bool=False):
        """
        Cette methode met à jour l'affichage du texte du label de progression
        :param new_text: le nouveau texte à afficher
        :return
        """
        self.ids['operation_progress_label'].text = str(new_text)
        self.ids['operation_progress_label'].color = "red" if is_error else "white"

    @mainthread
    def _update_operation_progress_bar(self, new_value):
        """
        Cette methode met à jour la valeur du progressBar
        :param new_value: la nouvelle valeur du progressBar
        :return
        """
        progressbar_id = self.ids['operation_progress_bar']

        if progressbar_id.disabled is True and progressbar_id.opacity == 0:
            progressbar_id.opacity = 1
            progressbar_id.disabled = False

        progressbar_id.value = new_value

    @mainthread
    def _reset_parameters(self):
        """
        Cette methode reset les differents Etats (des boutons, label)
        :param
        """
        self.ids['launch_button_id'].disabled = False
        self.ids['operation_progress_bar'].opacity = 0
        self.ids['operation_progress_bar'].disabled = True

        self.encryption_algorithm = None
        self.encryption_key = None
        self.encryption_key_size = None
        self.decryption_key = None

    def _encrypt_file(self, file_path, encryption_key, signature):
        """
        Cette methode lance l'operation d'encryption proprementdit sur un fichier
        :param file_path: le chemin d'access vers le fichier
        :param encryption_key: la clé e chiffrement du fichier
        :param signature: la signature de l'algorithme de chiffrement utilisé
        """
        file_path = os.path.normpath(file_path)
        file_name = os.path.basename(file_path)

        if not os.path.exists(file_path):
            self._update_operation_label_text(f"Le fichier {file_name} n'existe plus")
            return

        if self._check_encryption_status(file_path):
            self._update_operation_label_text(f"Le fichier {file_name} est déjà chiffré", True)

            self.running_app.DATABASE_MANAGER.add_new_history(
                operation="Chiffrement",
                file=file_path,
                size="%.3f Mo" % (os.path.getsize(file_path) / (1024 * 1024)),
                status="Échec",
                problem="Le fichier est déjà chiffré.",
                algorithm=f"{self.encryption_algorithm}-{self.encryption_key_size}"
            )
        else:
            started_time = time.time()
            try:
                self._update_operation_label_text(f"Chiffrement du fichier {file_name} en cours...")
                derived_encryption_key = derive_crypto_key(encryption_key, self.encryption_key_size)

                self._update_operation_progress_bar(0)
                encryption_result = encrypt_file(
                    file=file_path,
                    encryption_key=derived_encryption_key,
                    encryption_algorithm=self.encryption_algorithm,
                    algo_signature=signature,
                    callback=self._update_operation_progress_bar
                )

                if not encryption_result[0]:
                    self._update_operation_label_text(f"Échec du chiffrement. Veuillez réessayer.", True)
                    try:
                        os.remove(file_path + ".bin")
                    except:
                        pass

                    self.running_app.DATABASE_MANAGER.add_new_history(
                        operation="Chiffrement",
                        file=file_path,
                        size="%.3f Mo" % (os.path.getsize(file_path) / (1024 * 1024)),
                        status="Échec",
                        problem=encryption_result[1],
                        algorithm=f"{self.encryption_algorithm}-{self.encryption_key_size}"
                    )
                else:
                    encrypted_key = encrypt_password(
                        password=encryption_key.encode('utf-8'),
                        encryption_key=self.running_app.MASTER_ACCESS_PASSWORD
                    )
                    if encrypted_key:
                        self.running_app.DATABASE_MANAGER.add_new_backup(
                            file=file_path,
                            key=encrypted_key
                        )

                    self._update_operation_label_text(f"Chiffrement du fichier {file_name} terminé")
                    self.running_app.DATABASE_MANAGER.add_new_history(
                        operation="Chiffrement",
                        file=file_path,
                        size="%.3f Mo" % (os.path.getsize(file_path) / (1024 * 1024)),
                        status="Succès",
                        duration=time.time()-started_time,
                        algorithm=f"{self.encryption_algorithm}-{self.encryption_key_size}"
                    )
            except Exception:
                self._update_operation_label_text(f"Une erreur inattendue s'est produite.", True)

    def _decrypt_file(self, file_path, decryption_key):
        """
        Cette methode lance une operation de déchiffrement sur un fichier
        :param file_path: le chemin d'access vers le fichier
        :param decryption_key: la clé de dechiffrement
        :return
        """
        file_name = os.path.basename(file_path)
        algorithm, key_lenght = self._extract_key_length_and_algorithm(file_path)

        if not algorithm or not key_lenght:
            self._update_operation_label_text(f"Le fichier {file_name} ne peut pas être déchiffré par cette application.", True)

            self.running_app.DATABASE_MANAGER.add_new_history(
                operation="Déchiffrement",
                file=file_path,
                size="%.3f Mo" % (os.path.getsize(file_path) / (1024 * 1024)),
                status="Échec",
                algorithm=f"{algorithm}-{key_lenght}",
                problem="Le logiciel ne pas en mesure d'identifier l'algorithme de chiffrement utilisé pour ce fichier"
            )
        else:
            started_time = time.time()
            try:
                self._update_operation_label_text(f"Déchiffrement du fichier {file_name} en cours...")
                decryption_key = derive_crypto_key(decryption_key, key_lenght)

                self._update_operation_progress_bar(0)
                decryption_result = decrypt_file(
                    file=file_path,
                    decryption_key=decryption_key,
                    decryption_algorithm=algorithm,
                    callback=self._update_operation_progress_bar
                )

                if not decryption_result[0]:
                    self._update_operation_label_text(decryption_result[1], True)
                    try:
                        os.remove(file_path + ".bin")
                    except:
                        pass

                    self.running_app.DATABASE_MANAGER.add_new_history(
                        operation="Déchiffrement",
                        file=file_path,
                        size="%.3f Mo" % (os.path.getsize(file_path) / (1024 * 1024)),
                        status="Échec",
                        algorithm=f"{algorithm}-{key_lenght}",
                        problem=decryption_result[1]
                    )
                else:
                    self._update_operation_label_text(f"Déchiffrement du fichier {file_name} terminé avec succès.")
                    self.running_app.DATABASE_MANAGER.add_new_history(
                        operation="Déchiffrement",
                        file=file_path,
                        size="%.3f Mo" % (os.path.getsize(file_path) / (1024 * 1024)),
                        status="Succès",
                        duration=time.time() - started_time,
                        algorithm=f"{algorithm}-{key_lenght}"
                    )

            except Exception:
                self._update_operation_label_text(f"Une erreur inattendue s'est produite.", True)

    def run_services(self, selected_path):
        """
        Cette methode lance le service de chiffrement ou de déchiffremnent sur un fichier ou un dossier
        :param selected_path: le fichier ou dossier selectionner
        :return
        """
        encryption_chekbox = self.ids['enc_operation_checkbox'].active
        file_target_checkbox = self.ids['file_target_checkbox'].active
        folder_target_checkbox = self.ids['folder_target_checkbox'].active

        if file_target_checkbox is True:
            path = selected_path[0]
            if not os.path.isfile(path):
                self._open_dialog_box(
                    title="Opération impossible",
                    content="Aucun fichier sélectionné pour cette opération."
                )
                return
        elif folder_target_checkbox is True:
            path = selected_path[1]
            if not os.path.isdir(path):
                self._open_dialog_box(
                    title="Opération impossible",
                    content="Aucun dossier sélectionné pour cette opération."
                )
                return
        else:
            self._open_dialog_box(
                title="Opération impossible",
                content="Échec de lancement. Veuillez sélectionner tous les paramètres requis."
            )
            return

        label_text = (f"Continuer avec le "
                      f"{'chiffrement' if encryption_chekbox else 'déchiffrement'} "
                      f"du {'fichier' if file_target_checkbox else 'Dossier'}: \n")
        label_text += f"{selected_path[0] if file_target_checkbox else selected_path[1]} ?"

        layout = MDBoxLayout(
            orientation="vertical",
            md_bg_color=get_color_from_hex("#2C2C2C"),
            size_hint=(1, 1),
            pos_hint={"center_x": .5, "center_y": .5},
            padding=[5, 2, 5, 2],
            spacing=5,
            radius=[0, 0, 5, 5]
        )
        popUp = Popup(
            title="",
            background_color=(0, 0, 0, 0),
            separator_color=get_color_from_hex("#FEA674"),
            size_hint=(None, None),
            size=(522.45, 180),
            auto_dismiss=False,
            pos_hint={"center_x": .5, "center_y": .5},
            content=layout
        )

        def run(target_path: str) -> None:
            """
            Cette sous methode sert de socle pour lancer un thread séparer pour ne pas bloquer
            l'interface graphique
            :param target_path: le fichier ou dossier à chiffrer
            :return
            """
            try:
                encryption_operation_chekbox = self.ids['enc_operation_checkbox'].active
                decryption_operation_checkbox = self.ids['dec_operation_checkbox'].active

                if encryption_operation_chekbox is True:
                    if not self.encryption_algorithm or not self.encryption_key or not self.encryption_key_size:
                        self._open_dialog_box(
                            title="Opération impossible",
                            content="Paramètres de chiffrement non définis."
                        )
                    else:
                        signature = self._get_algorithm_signature(self.encryption_algorithm, self.encryption_key_size)
                        if os.path.isfile(target_path):
                            self._encrypt_file(
                                file_path=target_path,
                                encryption_key=self.encryption_key,
                                signature=signature
                            )
                        else:
                            nb_total = self._get_child_number_in_directory(path=target_path)
                            nb = 0

                            for path, dirs, files in os.walk(target_path):
                                for file in files:
                                    str_path = os.path.join(path, file)
                                    self._encrypt_file(
                                        file_path=str_path,
                                        encryption_key=self.encryption_key,
                                        signature=signature
                                    )

                                    # Mis à jour du compteur
                                    nb += 1
                                    self.ids['count_target_id'].text = f"( {nb}/{nb_total} )"

                            self._update_operation_label_text(f"Chiffrement du dossier {target_path} terminé avec succès.")

                elif decryption_operation_checkbox is True:
                    if not self.decryption_key:
                        self._open_dialog_box(
                            title="Opération impossible",
                            content="Paramètres de déchiffrement non définis."
                        )
                    else:
                        if os.path.isfile(target_path):
                            self._decrypt_file(
                                file_path=target_path,
                                decryption_key=self.decryption_key
                            )
                        else:
                            nb_total = self._get_child_number_in_directory(path=target_path)
                            nb = 0

                            for path, dirs, files in os.walk(target_path):
                                for file in files:
                                    str_path = os.path.join(path, file)
                                    self._decrypt_file(
                                        file_path=str_path,
                                        decryption_key=self.decryption_key
                                    )

                                    # Mis à jour du compteur
                                    nb += 1
                                    self.ids['count_target_id'].text = f"( {nb}/{nb_total})"

                            self._update_operation_label_text(f"Déchiffrement du dossier {target_path} terminé avec succès.")
                else:
                    self._open_dialog_box(
                        title="Opération impossible",
                        content="Échec de lancement. Veuillez sélectionner tous les paramètres requis."
                    )

            except Exception:
                pass
            finally:
                self._reset_parameters()

        def start_operation(*args):
            popUp.dismiss()

            self.ids['launch_button_id'].disabled = True
            threading.Thread(target=run, args=[path], daemon=True, name="Encryption-Thread").start()



        confirmation_label = MDLabel(
            text=label_text,
            valign="center",
            halign="center",
            color=get_color_from_hex("#CCCCCC")
        )
        layout.add_widget(confirmation_label)

        box1 = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(.95, .55),
            padding=[0,0,0,5],
            pos_hint={"center_x": .5, "center_y": .5}
        )

        cancel_button = MDRaisedButton(text="Annuler", size_hint=(1,1))
        cancel_button.bind(on_release=popUp.dismiss)
        box1.add_widget(cancel_button)

        continue_button = MDRaisedButton(text="Continuer", size_hint=(1,1))
        continue_button.bind(on_release=start_operation)
        box1.add_widget(continue_button)

        layout.add_widget(box1)
        popUp.open()
