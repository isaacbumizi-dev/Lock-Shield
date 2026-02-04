import os
import sys
import time
import pickle
import bcrypt
import threading


import fileChooser
import cryptographic_engine


from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from Cryptodome.Cipher import AES
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty
from kivy.uix.relativelayout import RelativeLayout



Builder.load_string("""
#: import Factory kivy.factory.Factory
#: import CustomFileChooser fileChooser

#: set line_color (0.122, 0.627, 0.333, .8)
#: set text_color "#1F753A"

#: set screen_text0 "Sélectionner le fichier ou le dossier à "
#: set screen_text1 " le fichier spécifié"
#: set screen_text2 " le dossier en entier"
#: set screen_text3 "Démarrer le "

<Main_Window_Widget>:
    orientation: "vertical"
    BoxLayout:
        orientation: "horizontal"
        size_hint: 1, .06
        padding: [5, 0, 5, 0]
        spacing: 5
        ActionView:
            size_hint: .04, 1
            pos_hint: {"center_x": .5, "center_y": .5}
            ActionPrevious:
                app_icon: ''
                on_release: app.MANAGER.pop()

        Label:
            text: "Lock Shield"
            text_size: self.size
            halign: "center"
            valign: "center"
            bold: True
            font_size: "20dp"
            color: text_color
            canvas.before:
                Color:
                    rgba: get_color_from_hex("#1E1F22")
                Rectangle:
                    size: self.size
                    pos: self.pos
        Widget:
            size_hint: .06, 1
            
        
            
    BoxLayout:
        orientation: "vertical"
        spacing: 3
        padding: [0, 5, 0, 5]
        canvas.before:
            Color:
                rgba: line_color
            Line:
                points: (2,2, 2,self.height-1, self.width-2,self.height-1, self.width-2,2, 2,2)

        Label:
            text: screen_text0 + "chiffrer" if root.CURRENT_SCREEN == "encryption_screen" else screen_text0 + "déchiffrer"
            text_size: self.size
            halign: "center"
            valign: "center"
            color: text_color
            bold: True
            size_hint: 1, .08
            pos_hint: {"center_y": .5}

        BoxLayout:
            size_hint: 1, .7
            padding: [5, 0, 5, 2]
            CustomFileChooser:
                id: filechooser_id

        BoxLayout:
            padding: [20, 3, 20, 0]
            size_hint: 1, .04
            canvas.before:
                Color:
                    rgba: get_color_from_hex("#1E1F22")
                Line:
                    width: 1.05
                    points: (self.x+50,self.y + self.height/2, self.width-50, self.y + self.height/2)


        BoxLayout:
            orientation: "horizontal"
            size_hint: 1, .1
            padding: [7, 0, 7, 0]

            Label:
                text: "Chiffrez" + screen_text1 if root.CURRENT_SCREEN == "encryption_screen" else "Déchiffrez" + screen_text1
                text_size: self.size
                halign: "right"
                valign: "center"
                bold: True
                color: text_color
            CheckBox:
                #active: True
                value: "file"
                group: "cryptogroup"
                size_hint: .5, 1
                on_active: root.set_selection_mode(self) if self.active else ""
            Label:
                text: "Chiffrez" + screen_text2 if root.CURRENT_SCREEN == "encryption_screen" else "Déchiffrer" + screen_text2
                text_size: self.size
                halign: "right"
                valign: "center"
                bold: True
                color: text_color
            CheckBox:
                value: "folder"
                group: "cryptogroup"
                size_hint: .5, 1
                on_active: root.set_selection_mode(self) if self.active else ""


        BoxLayout:
            orientation: "vertical"
            size_hint: 1, .8
            padding: [10, 10, 10, 5]
            CustomFillButton:
                text: "Options de Configuration"
                size_hint: .8, .5
                pos_hint: {"center_x": .5}
                background_color: get_color_from_hex("#18391E")
                on_release:
                    root.show_encryption_config() if root.CURRENT_SCREEN == "encryption_screen" else\
                    root.show_decryption_config()

            BoxLayout:
                orientation: "vertical"
                spacing: 3
                padding: [0, 20, 0, 0]
                RelativeLayout:
                    Label:
                        id: label_id
                        text: ""
                        pos_hint: {"center_x": .5}
                    Label:
                        id: progress_id
                        text: ""
                        size_hint: .08, 1
                        pos_hint: {"center_x": .98}

                ProgressBar:
                    id: progressBar_id
                    min: 0
                    opacity: 0
                    disabled: True
                    size_hint: .8, 1
                    pos_hint: {"center_x": .5, "center_y": .5}


            CustomFillButton:
                text: screen_text3 + "chiffrement" if root.CURRENT_SCREEN == "encryption_screen" else screen_text3 + "Déchiffrement"
                size_hint: .4, .5
                pos_hint: {"center_x": .5}
                background_color: get_color_from_hex("#D3510D")
                on_release:                    
                    root.start_encryption_process(self, filechooser_id.get_selected_path()) if root.CURRENT_SCREEN == "encryption_screen"\
                    else root.start_decryption_process(self, filechooser_id.get_selected_path())
                    
                            
<EncryptionSetup>
    orientation: "vertical"
    spacing: 5

    BoxLayout:
        spacing: 5
        padding: [2, 5, 2, 2]
        size_hint: 1, .8
        BoxLayout:
            orientation: "vertical"
            spacing: 3
            Label:
                text: "Algorithme de chiffrement à utilisé"
                text_size: self.size
                halign: "center"
                valign: "center"
                color: text_color
                size_hint: 1, .1
                font_size: 16
            GridLayout:
                canvas.before:
                    Color:
                        rgba: get_color_from_hex("#1E1F22")
                    Line:
                        width: 1
                        rectangle: (self.x, self.y, self.width, self.height)

                cols: 2
                row: 3
                size_hint: 1, 1
                padding: [20, 0, 20, 0]
                Label:
                    text: "Algorithme: AES Mode: CBC"
                    text_size: self.size
                    halign: "left"
                    valign: "center"
                CheckBox:
                    value: "AES-CBC"
                    active: True
                    group: "algorithm"
                    size_hint: .5, 1
                    on_active: root.select_encryption_algorithm(self) if self.active == True else ""
                Label:
                    text: "Algorithme: AES Mode: CFB"
                    text_size: self.size
                    halign: "left"
                    valign: "center"
                CheckBox:
                    value: "AES-CFB"
                    group: "algorithm"
                    size_hint: .5, 1
                    on_active: root.select_encryption_algorithm(self) if self.active == True else ""
                Label:
                    text: "Algorithme: AES Mode: OFB"
                    text_size: self.size
                    halign: "left"
                    valign: "center"
                CheckBox:
                    value: "AES-OFB"
                    group: "algorithm"
                    size_hint: .5, 1
                    on_active: root.select_encryption_algorithm(self) if self.active == True else ""
        BoxLayout:
            orientation: "vertical"
            spacing: 3
            Label:
                text: "Longeur de la clé de chiffrement"
                text_size: self.size
                halign: "center"
                valign: "center"
                color: text_color
                size_hint: 1, .1
                font_size: 16
            GridLayout:
                canvas.before:
                    Color:
                        rgba: get_color_from_hex("#1E1F22")
                    Line:
                        width: 1
                        rectangle: (self.x, self.y, self.width, self.height)

                cols: 2
                row: 3
                size_hint: 1, 1
                padding: [20, 0, 20, 0]
                Label:
                    text: "Clé de 128 bits"
                    text_size: self.size
                    halign: "center"
                    valign: "center"
                CheckBox:
                    value: "128"
                    active: True
                    group: "key"
                    size_hint: .5, 1
                    on_active: root.select_key_size(self) if self.active == True else ""
                Label:
                    text: "Clé de 192 bits"
                    text_size: self.size
                    halign: "center"
                    valign: "center"
                CheckBox:
                    value: "192"
                    group: "key"
                    size_hint: .5, 1
                    on_active: root.select_key_size(self) if self.active == True else ""
                Label:
                    text: "Clé de 256 bits"
                    text_size: self.size
                    halign: "center"
                    valign: "center"
                CheckBox:
                    value: "256"
                    group: "key"
                    size_hint: .5, 1
                    on_active: root.select_key_size(self) if self.active == True else ""

    BoxLayout:
        spacing: 3
        orientation: "vertical"
        BoxLayout:
            padding: [20, 3, 20, 0]
            size_hint: 1, .04
            canvas.before:
                Color:
                    rgba: get_color_from_hex("#1E1F22")
                Line:
                    width: 1.05
                    points: (self.x+50,self.y + self.height/2, self.width-50, self.y + self.height/2)
        BoxLayout:
            orientation: "vertical"
            spacing: 3
            BoxLayout:
                orientation: "vertical"
                padding: [10, 5, 10, 10]
                spacing: 3

                BoxLayout:
                    Label:
                        text: "Valeur de la clé :"
                        text_size: self.size
                        halign: "center"
                        valign: "center"
                        color: text_color
                        size_hint: .3, 1
                    TextInput:
                        id: key_input
                        multiline: False
                        password: True
                        size_hint: 1, .5
                        pos_hint: {"center_x": .5, "center_y": .5}

                BoxLayout:
                    orientation: "horizontal"
                    size_hint: 1, .2
                    padding: [400, 0, 10, 0]
                    CheckBox:
                        active: False
                        size_hint: .1, 1
                        on_active: key_input.password = False if self.active else True
                        pos_hint: {"center_x": .2, "center_y": .5}
                    Label:
                        text: "Afficher la clé de chiffrement"
                        text_size: self.size
                        halign: "left"
                        valign: "center"
                        theme_text_color: text_color
                        color: text_color

            BoxLayout:
                orientation: "vertical"
                padding: [10, 5, 10, 10]
                canvas.before:
                    Color:
                        rgba: get_color_from_hex("#1E1F22")
                    Line:
                        width: 1
                        rectangle: (self.x, self.y, self.width, self.height)
                Label:
                    text: "Génerer automatique la clé de chiffrement"
                    text_size: self.size
                    halign: "center"
                    valign: "center"
                    color: text_color
                BoxLayout:
                    orientation: "horizontal"
                    spacing: 5
                    Label:
                        text: "Longeur de la clé :"
                        text_size: self.size
                        halign: "center"
                        valign: "center"
                        color: text_color
                    TextInput:
                        canvas.before:
                            Color:
                                rgba: (0, 0, 0, 1)
                            Line:
                                width: 1
                                rectangle: (self.x, self.y, self.width, self.height)
                        id: generate_key
                        multiline: False
                        input_filter: 'int'
                        hint_text: "Valeur superieur à 7 et inferieur ou égal à 256"
                        on_text_validate: root.generate_rawEncryption_key(self, key_input) if self.text else ""

                    CustomFillButton:
                        text: "Génerer"
                        pos_hint: {"center_x": .5}
                        background_color: get_color_from_hex("#D3510D")
                        on_release: root.generate_rawEncryption_key(generate_key, key_input) if generate_key.text else ""

        BoxLayout:
            size_hint: 1, .15
            spacing: 5
            CustomFillButton:
                text: "Annuler"
                background_color: get_color_from_hex("#56925C")
                on_release:
                    root.reset_config()
                    self.parent.parent.parent.parent.parent.parent.dismiss()
            CustomFillButton:
                text: "Ok"
                background_color: get_color_from_hex("#56925C")
                on_release:
                    root.validate_config(key_input.text)
                    self.parent.parent.parent.parent.parent.parent.dismiss()
                    
                    
<DecryptionSetup>:
    orientation: "vertical"
    BoxLayout:
        orientation: "vertical"
        padding: [10, 5, 10, 10]
        spacing: 3

        BoxLayout:
            Label:
                text: "Valeur de la clé :"
                text_size: self.size
                halign: "center"
                valign: "center"
                color: text_color
                size_hint: .3, 1
            TextInput:
                id: key_input_dec
                multiline: False
                password: True
                size_hint: 1, .5
                pos_hint: {"center_x": .5, "center_y": .5}

        BoxLayout:
            orientation: "horizontal"
            size_hint: 1, .2
            padding: [400, 0, 10, 0]
            CheckBox:
                active: False
                size_hint: .1, 1
                on_active: key_input_dec.password = False if self.active else True
                pos_hint: {"center_x": .2, "center_y": .5}
            Label:
                text: "Afficher la clé de déchiffrement"
                text_size: self.size
                halign: "left"
                valign: "center"
                theme_text_color: text_color
                color: text_color

    BoxLayout:
        size_hint: 1, .2
        spacing: 5
        CustomFillButton:
            text: "Annuler"
            background_color: get_color_from_hex("#56925C")
            on_release:
                root.reset_config()
                self.parent.parent.parent.parent.parent.dismiss()
        CustomFillButton:
            text: "Ok"
            background_color: get_color_from_hex("#56925C")
            on_release:
                root.validate_config(key_input_dec.text)
                self.parent.parent.parent.parent.parent.dismiss()


<CustomFillButton@Button>:
    canvas.before:
        Color:
            rgba: 0, 0, 0, 0
        Line:
            width: 1
            rectangle: (self.x, self.y, self.width, self.height)
    background_color: 1, 1, 1, .15
    color: get_color_from_hex("#FFFFFF")
    font_size: "17dp"
    size_hint: 1, 1
    
    
<ParameterPopUp@Popup>:  
    title: "Menu"
    title_align: "center"
    title_color: get_color_from_hex("#FFFFFF")
    title_size: 17
    background_color: get_color_from_hex("#606060")
    separator_color: get_color_from_hex("#463C4B")
    size_hint: (.7, .25)
    
    BoxLayout:
        padding: 3, 5, 3, 5
        spacing: 5
        CustomFillButton:
            text: "Historique"
            font_size: "15dp"
            background_color: get_color_from_hex("#555A6E")
            on_release: 
                root.dismiss()           
                Factory.HistoryPopUp().open()
        
        CustomFillButton:
            text: "Sauvegarde et Restauration"
            font_size: "15dp"
            background_color: get_color_from_hex("#555A6E")
            on_release:
                root.dismiss()
                Factory.BackupAndRestore_PopUp().open()

            
        CustomFillButton:
            text: "A propos"
            font_size: "15dp"
            background_color: get_color_from_hex("#555A6E")
            on_release: 
                root.dismiss() 
                Factory.About_popUp().open()
            
            
<About_popUp@Popup>:
    title: "A propos"
    title_align: "center"
    title_color: get_color_from_hex("#FFFFFF")
    title_size: 17
    background_color: get_color_from_hex("#606060")
    separator_color: get_color_from_hex("#463C4B")
    size_hint: (.5, .85)
    auto_dismiss: True
    
    RstDocument:
        text: app.ABOUT_APPLICATION
        do_scroll_x: False



            
<HistoryPopUp@Popup>:
    title: "Historique des opérations"
    title_align: "center"
    title_color: get_color_from_hex("#FFFFFF")
    title_size: 17
    background_color: get_color_from_hex("#606060")
    separator_color: get_color_from_hex("#463C4B")
    size_hint: (.7, 1)
    auto_dismiss: False
    
    HistoryWindow:


<HistoryWindow_ViewClass>:
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        padding: [5, 5, 5, 3]
        text: str(root.label_text)
          
<HistoryWindow>:
    BoxLayout:
        orientation: "vertical"
        spacing: 7
        padding: [3, 10, 3, 3]
        BoxLayout:
            size_hint: 1, .07
            CustomFillButton:
                text: "Effacer l'historique"
                font_size: "12dp"
                background_color: get_color_from_hex("#463C4B")
                on_release: root.confirm_delete_history()
            CustomFillButton:
                text: "Exporter vers Pdf"
                font_size: "12dp"
                background_color: get_color_from_hex("#463C4B")
                on_release: root.export_history_to_pdf()
                
        RecycleView:
            id: history_id
            key_viewclass: 'viewclass'
            key_size: 'height'
            bar_color: get_color_from_hex("#9F9F9F")
            scroll_type: ['bars', 'content']
            bar_width: 8
            RecycleBoxLayout:
                padding: [1, 0, 1, 0]
                default_size: None, dp(23)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
        
        CustomFillButton:
            text: 'Quitter'
            font_size: "15dp"
            size_hint: 1, .08
            background_color: get_color_from_hex("#56925C")
            on_release: root.parent.parent.parent.dismiss()
    

                    
                                  
<BackupAndRestore_PopUp@Popup> 
    title: "Sauvegarde et Restauration"
    title_align: "center"
    title_color: get_color_from_hex("#FFFFFF")
    title_size: 17
    background_color: get_color_from_hex("#606060")
    separator_color: get_color_from_hex("#463C4B")
    size_hint: (1, 1)
    auto_dismiss: False
        
    KeyVault:

<KeyVault>:
    BoxLayout:
        orientation: "vertical"
        padding: [2, 2, 5, 2]
        BoxLayout:
            size_hint: 1, .1
            orientation: "horizontal"
            padding: [10, 0, 0, 0]
            canvas.before:
                Color:
                    rgba: 1, 1, 1, .03
                Rectangle:
                    size: self.size
                    pos: self.pos
            Widget:
                size_hint: .05, 1
            Label:
                text: "Date du chiffrement"
                text_size: self.size
                valign: "center"
                haling: "left"
                size_hint: .55, 1
            Label:
                text: "Fichier"
                text_size: self.size
                valign: "center"
                haling: "left"
                size_hint: 1, 1
            CustomFillButton:
                size_hint: .3, .8
                text: "Supprimer la sauvegarde"
                font_size: "14dp"
                pos_hint: {"center_x": .5, "center_y": .5}
                background_color: get_color_from_hex("#C94F4F")
                on_release: root.delete_backup()
                    
        RecycleView:
            id: restoring_id
            key_viewclass: 'viewclass'
            key_size: 'height'
            bar_color: get_color_from_hex("#9F9F9F")
            scroll_type: ['bars', 'content']
            bar_width: 8
            RecycleBoxLayout:
                padding: [1, 5, 8, 5]
                default_size: None, dp(50)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
        
        CustomFillButton:
            text: 'Quitter'
            font_size: "15dp"
            size_hint: 1, .06
            background_color: get_color_from_hex("#56925C")
            on_release: root.parent.parent.parent.dismiss()
    
            
            
<KeyVault_ViewClass>:
    orientation: "horizontal"
    padding: [1, 5, 1, 5]
    spacing: 4
    canvas.before:
        Color:
            rgba: 1, 1, 1, .06
        Line:
            points: (self.x,self.y, self.width,self.y)
    
    Label:
        id: num_id
        text: str(root.num)
        text_size: self.size
        halign: "left"
        valign: "center"
        size_hint: .05, 1
    Label:
        text: str(root.date)
        text_size: self.size
        halign: "left"
        valign: "center"
        size_hint: .5, 1
    Label:
        text: str(root.file_name)
        text_size: self.size
        halign: "left"
        valign: "center"
        size_hint: 1, 1
    Button:
        canvas.before:
            Color:
                rgba: 1, 1, 1, .3
            Line:
                rectangle: (self.x, self.y, self.width, self.height)         
        text: "Restaurer"
        size_hint: .2, 1
        background_color: 1, 1, 1, .03
        pos_hint: {"center_x": .5, "center_y": .5}
        on_release: 
            root.parent.parent.parent.parent.restore_encryption_key(num_id.text)
""")



if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


DATA_FOLDER = os.path.join(BASE_DIR, 'data')
MASTER_PWD_FILE = os.path.join(DATA_FOLDER, 'MASTERPASSWORD')
HISTORY_FILE = os.path.join(DATA_FOLDER, 'LOGHISTORY.bin')
BACKUP_FILE = os.path.join(DATA_FOLDER, 'BACKUP')


MASTER_PASSWORD = ""

TARGET_PATH = "" # Le chemin vers le fichier ou dossier à chiffré
RAW_ENCRYPTION_KEY = "" # La valeur de la clé de chiffrement entrer par l'utilisateur
RAW_DECRYPTION_KEY = "" # La valeur de la clé de déchiffrement entrer par l'utilisateur
ENCRYPTION_KEY_SIZE = 128 # La longeur de la clé de chiffrement
ENCRYPTION_ALGORITHM = "AES-CBC" # L'algorithme de chiffrement à utilisé



def reset_encryption_configuration():
    global ENCRYPTION_ALGORITHM
    global ENCRYPTION_KEY_SIZE
    global RAW_ENCRYPTION_KEY

    ENCRYPTION_ALGORITHM = "AES-CBC"
    ENCRYPTION_KEY_SIZE = 128
    RAW_ENCRYPTION_KEY = ""

def reset_decryption_configuration():
    global RAW_DECRYPTION_KEY

    RAW_DECRYPTION_KEY = ""


class Main_Window_Widget(BoxLayout):
    CURRENT_SCREEN = StringProperty(None)
    CURRENT_SELECTION_MODE = StringProperty("file")

    def __init__(self, **kwargs):
        super(Main_Window_Widget, self).__init__(**kwargs)
        self.run_update_progress = False

        Clock.schedule_interval(self.update_progress, 0.3)

    def update_progress(self, *args):
        if self.run_update_progress:
            self.ids["progress_id"].text = str(cryptographic_engine.get_progress_percent()) + " %"

    def set_current_screen_name(self, screen_name):
        self.CURRENT_SCREEN = screen_name

    @staticmethod
    def set_masterPassWord(pw_d):
        global MASTER_PASSWORD
        MASTER_PASSWORD = pw_d

    def set_selection_mode(self, value):
        """
        Cette methode permet de changer la valeur de la variable CURRENT_SELECTION_MODE
        :param value: File ort Folder
        :return:
        """
        self.CURRENT_SELECTION_MODE = str(value.value)
    @staticmethod
    def update_history(state,
                       date,
                       operation,
                       target,
                       file_size,
                       algo="AES-CBC",
                       duration = None,
                       failure_cause=None):
        """
        Cette methode permet d'enregistrer l'historique de l'opération courante
        :param state: Succès/Echec
        :param date: la fate de l'opération
        :param operation: chiffrement/Déchiffrement
        :param target: Fichier/Dossier chiffré/Déchiffré
        :param algo: l'algorithme de chiffrement/déchiffrement utilisé
        :param file_size: la taille du fichier
        :param duration: le temps effectué lors de l'opération
        :param failure_cause: cause de l'échec si opération à échouée
        :return:
        """
        def save_data(data):
            try:
                with open(HISTORY_FILE, "ab") as htr_file:
                    htr_file.write(data.encode('utf-8'))
            except:
                pass

        if state == "Succès":
            pw_d = f"""
Date: {date}
        Opération: {operation}
        Fichier: {target}
        Taille: {file_size}
        Status: {state}
        Duré de l'opération: {duration} Sécondes
        Algorithme de chiffrement/Déchiffrement: {algo} bits\n
            """
            save_data(pw_d)

        elif state == "Echec":
            pw_d = f"""
Date: {date}
         Opération: {operation}
         Fichier: {target}
         Taille: {file_size}
         Status: {state}
         Cause: {failure_cause}\n
            """
            save_data(pw_d)


    @staticmethod
    def save_encryption_key(pwd, file):
        """
        Cette methode permet de sauvegarder les clés de chiffrement pour une eventuel récuperation en
        cas de perte ou d'oubli de celui-ci par l'utilisateur
        """
        def encrypt_key(key):
            """
            Cette fonction permet de chiffré la clé pour un stockage sécurisé
            """
            cipher = AES.new(cryptographic_engine.derive_cryptographic_key(MASTER_PASSWORD, 128), AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(key.encode())
            msg_payload = cipher.nonce + tag + ciphertext
            return msg_payload

        try:
            data = [file,  time.strftime("%A %d %B %Y %H:%M:%S"), encrypt_key(pwd)]
            with open(BACKUP_FILE, "ab") as hs_file:
                pickle_object = pickle.Pickler(hs_file)
                pickle_object.dump(data)
        except Exception:
            pass


    @staticmethod
    def show_configuration(size_hint, content):
        """
        cette methode permet d'ouvrir la fenêtre de configuration pour l'operation de chiffrement/déchiffrement
        """
        Popup(
            title="Options de Configuration",
            title_align="center",
            title_color=get_color_from_hex("#1F753A"),
            title_size=18,
            background_color=get_color_from_hex("#606060"),
            separator_color=get_color_from_hex("#1F753A"),
            size_hint=size_hint,
            auto_dismiss=False,
            content=content
        ).open()

    def show_error(self, content):
        """
        Cette methode permet d'ouvrir une fenêtre et d'afficher un message d'erreur, s'il y a une erreur
        """
        Popup(
            title="Erreur",
            title_align="center",
            title_color=get_color_from_hex("#C94F4F"),
            title_size=18,
            background_color=get_color_from_hex("#606060"),
            separator_color=get_color_from_hex("#606060"),
            size_hint=(.7, .3),
            auto_dismiss=True,
            content=Label(
                text=content,
                text_size=self.size,
                valign="center",
                halign="center",
                font_size=17,
                color="#C94F4F"
            )
        ).open()
    def show_encryption_config(self):
        """
        Cette methode permet d'ouvrir la fenêtre de configuration pour le chiffrement
        :return:
        """
        self.show_configuration((.9, .9), EncryptionSetup())

    def show_decryption_config(self):
       """
       Cette methode permet d'ouvrir la fenêtre de configuration pour de déchiffrement
       :return:
       """
       self.show_configuration((.9, .4), DecryptionSetup())

    def start_encryption_process(self, button_instance ,dt):
        """
        Cette methode permet de lancer le processus de chiffrement
        :param dt: l'instance de filechooser_id
        :param button_instance: l'instance du bouton qui a été appuyé
        :return:
        """
        def get_filenumber_in_directory(path):
            """
            Cette fonction permet des compter les nombres des élements(fichier) à chiffré dans un dosiier
            :param path: le chemin absolu vers le dossier cible
            :return:
            """
            d_nb = 0
            for path, dirs, files in os.walk(path):
                for file in files:
                    d_nb += 1
                    self.ids['label_id'].text = f"Détection de {d_nb} éléments"

            time.sleep(2)
            try:
                self.ids['progressBar_id'].max = d_nb
                self.ids['progressBar_id'].opacity = 1
                self.ids['progressBar_id'].disabled = False
            except Exception:
                pass

        def check_encryption_status(file):
            """
            Cette fonction permet de vérifier si le fichier est déja chiffré ou nom
            :param file:
            :return:
            """
            sign = b''
            with open(file, "rb") as f:
                sign = f.read(32)

            if sign in cryptographic_engine.get_algorithm_signature():
                return True
            else:
                return False

        def get_algorithm_signature(algorithm, key_size):
            """
            Cette fonction permet de retrouver le signature de l'algorithme de chiffrement utilisé
            :param algorithm:
            :param key_size:
            :return:
            """
            match ENCRYPTION_ALGORITHM:
                case "AES-CBC":
                    match key_size:
                        case 128:
                            return cryptographic_engine.get_algorithm_signature()[3]
                        case 192:
                            return cryptographic_engine.get_algorithm_signature()[4]
                        case 256:
                            return cryptographic_engine.get_algorithm_signature()[5]
                case "AES-CFB":
                    match key_size:
                        case 128:
                            return cryptographic_engine.get_algorithm_signature()[0]
                        case 192:
                            return cryptographic_engine.get_algorithm_signature()[1]
                        case 256:
                            return cryptographic_engine.get_algorithm_signature()[2]
                case "AES-OFB":
                    match key_size:
                        case 128:
                            return cryptographic_engine.get_algorithm_signature()[6]
                        case 192:
                            return cryptographic_engine.get_algorithm_signature()[7]
                        case 256:
                            return cryptographic_engine.get_algorithm_signature()[8]
        
        def encrypt_file(path, encryptionKey, signature):
            file_name = path.split('\\')[-1]

            if check_encryption_status(path):
                self.ids['label_id'].text = f"Le fichier {file_name} est déjà chiffré"

                self.update_history(
                    state="Echec",
                    date=time.strftime("%A %d %B %Y %H:%M:%S"),
                    operation="Chiffrement",
                    target=path,
                    file_size="%.3f Mo" % (os.path.getsize(path) / (1024 * 1024)),
                    failure_cause="Le fichier est déjà chiffré")

            else:
                enc_time = time.time()
                try:
                    self.ids['label_id'].text = f"Chiffrement du fichier {file_name} en cours..."
                    match ENCRYPTION_ALGORITHM:
                        case "AES-CBC":
                            cryptographic_engine.Encryption_engine(path, encryptionKey).AES_CBC(signature)
                        case "AES-CFB":
                            cryptographic_engine.Encryption_engine(path, encryptionKey).AES_CFB(signature)
                        case "AES-OFB":
                            cryptographic_engine.Encryption_engine(path, encryptionKey).AES_OFB(signature)
                        case _:
                            pass
                except Exception as e:
                    self.ids['label_id'].text = f"Une erreur s'est produite lors du chiffrement: {str(e)}"
                    try:os.remove(path + ".bin")
                    except:pass

                    self.update_history(
                        state="Echec",
                        date=time.strftime("%A %d %B %Y %H:%M:%S"),
                        operation="Chiffrement",
                        target=path,
                        file_size="%.3f Mo" % (os.path.getsize(path) / (1024 * 1024)),
                        failure_cause=str(e))

                else:
                    Main_Window_Widget.save_encryption_key(RAW_ENCRYPTION_KEY, path)

                    self.ids["progress_id"].text = " "
                    self.ids['label_id'].text = f"Chiffrement du fichier {file_name} términé"

                    self.update_history(
                        state="Succès",
                        date=time.strftime("%A %d %B %Y %H:%M:%S"),
                        operation="Chiffrement",
                        algo=f"{ENCRYPTION_ALGORITHM} {ENCRYPTION_KEY_SIZE}",
                        target=path,
                        duration=time.time()-enc_time,
                        file_size="%.3f Mo" % (os.path.getsize(path) / (1024 * 1024)))


        def pre_encryption_checks(instance):
            """
            Cette fonction permet de lancer le processus de chiffrement sur un fichier
            :param instance: l'instance du bouton "Démarrer le chiffrement"
            :return:
            """
            instance.disabled = True
            encryption_key = cryptographic_engine.derive_cryptographic_key(RAW_ENCRYPTION_KEY, ENCRYPTION_KEY_SIZE)
            signature = get_algorithm_signature(ENCRYPTION_ALGORITHM, ENCRYPTION_KEY_SIZE)

            if self.CURRENT_SELECTION_MODE == "file":
                self.run_update_progress = True
                encrypt_file(TARGET_PATH, encryption_key, signature)

            elif self.CURRENT_SELECTION_MODE == "folder":
                get_filenumber_in_directory(TARGET_PATH)
                self.run_update_progress = True
                for path, dirs, files in os.walk(TARGET_PATH):
                    for file in files:
                        str_path = os.path.join(path, file)
                        encrypt_file(str_path, encryption_key, signature)

                        self.ids['progressBar_id'].value += 1

                self.ids["progress_id"].text = " "
                self.ids['label_id'].text = "Processus de chiffrement terminé"

            try:
                instance.disabled = False
                self.ids['progressBar_id'].value = 0
                self.ids['progressBar_id'].disabled = True
                self.ids['progressBar_id'].opacity = 0
            except Exception:
                pass

            self.run_update_progress = False
            reset_encryption_configuration()


        global TARGET_PATH
        if self.CURRENT_SELECTION_MODE == "file":
            TARGET_PATH = dt[0]
        else:
            TARGET_PATH = dt[1]

        if not TARGET_PATH or not RAW_ENCRYPTION_KEY:
            self.show_error("La clé de chiffrement et le fichier à chiffrer sont requisent.\n"
                                "Assurez-vous de les spécifier avant de continuer.")
        else:
            thread = threading.Thread(target=pre_encryption_checks, args=[button_instance])
            thread.start()


    def start_decryption_process(self, button_instance, dt):
        """
        Cette methode permet de lancer le processus de déchiffrement
        :param dt: l'instance de filechooser_id
        :param button_instance: l'instance du bouton "Démarrer le déchiffrement"
        :return:
        """
        def get_filenumber_in_directory(path):
            """
            Cette fonction permet des compter les nombres des élements(fichier) à chiffré dans un dosiier
            :param path: le chemin absolu vers le dossier cible
            :return:
            """
            d_nb = 0
            for path, dirs, files in os.walk(path):
                for file in files:
                    d_nb += 1
                    self.ids['label_id'].text = f"Détection de {d_nb} éléments"

            time.sleep(2)
            try:
                self.ids['progressBar_id'].max = d_nb
                self.ids['progressBar_id'].opacity = 1
                self.ids['progressBar_id'].disabled = False
            except Exception:
                pass
            del d_nb

        def get_key_length_and_algorithm(file):
            extract = b''
            with open(file, "rb") as f:
                extract = f.read(32)

            algorithm_signature = cryptographic_engine.get_algorithm_signature()
            try:
                pw_i = algorithm_signature.index(extract)
                match pw_i:
                    case 0:
                        return "AES-CFB", 128
                    case 1:
                        return "AES-CFB", 192
                    case 2:
                        return "AES-CFB", 256
                    case 3:
                        return "AES-CBC", 128
                    case 4:
                        return  "AES-CBC", 192
                    case 5:
                        return  "AES-CBC", 256
                    case 6:
                        return  "AES-OFB", 128
                    case 7:
                        return  "AES-OFB", 192
                    case 8:
                        return  "AES-OFB", 256
            except Exception as e:
                return None, None

        def decrypt_file(path):
            algorithm, key_lenght = get_key_length_and_algorithm(path)
            file_name = path.split('\\')[-1]
            if not algorithm:
                self.ids['label_id'].text = f"Le fichier {file_name} ne peut pas être déchiffré"

                self.update_history(
                    state="Echec",
                    date=time.strftime("%A %d %B %Y %H:%M:%S"),
                    operation="Déchiffrement",
                    target=path,
                    file_size="%.3f Mo" % (os.path.getsize(path) / (1024 * 1024)),
                    failure_cause="Le logiciel ne pas en mesure d'identitifier l'algorithme de chiffrement utilisé")

            else:
                self.ids['label_id'].text = f"Déchiffrement du fichier {file_name} en cours..."
                decryption_key = cryptographic_engine.derive_cryptographic_key(RAW_DECRYPTION_KEY, key_lenght)
                try:
                    dec_time = time.time()
                    match algorithm:
                        case "AES-CBC":
                            cryptographic_engine.Decryption_engine(path, decryption_key).AES_CBC()
                        case "AES-CFB":
                            cryptographic_engine.Decryption_engine(path, decryption_key).AES_CFB()
                        case "AES-OFB":
                            cryptographic_engine.Decryption_engine(path, decryption_key).AES_OFB()
                        case _:
                            pass
                except Exception as e:
                    if 'Padding' in str(e):
                        self.ids['label_id'].text = "La clé de déchiffrement est invalide!"
                    else:
                        self.ids['label_id'].text = f"Une erreur s'est produite lors du déchiffrement: {str(e)}"
                    try:os.remove(path + ".bin")
                    except:pass

                    self.update_history(
                        state="Echec",
                        date=time.strftime("%A %d %B %Y %H:%M:%S"),
                        operation="Déchiffrement",
                        target=path,
                        file_size="%.3f Mo" % (os.path.getsize(path) / (1024 * 1024)),
                        failure_cause=str(e) if 'Padding' in str(e) else "Clé de déchiffrement invalide")

                else:
                    self.ids["progress_id"].text = " "
                    self.ids['label_id'].text = f"Déchiffrement du fichier {file_name} términé"

                    self.update_history(
                        state="Succès",
                        date=time.strftime("%A %d %B %Y %H:%M:%S"),
                        operation="Déchiffrement",
                        target=path,
                        algo=f"{algorithm} {key_lenght}",
                        duration=time.time()-dec_time,
                        file_size="%.3f Mo" % (os.path.getsize(path) / (1024 * 1024)))

        def pre_decryption_checks(instance):
            """
            Cette fonction permet de lancer le processus de déchiffrement sur un fichier
            :param instance: l'instance du bouton "Démarrer le déchiffrement"
            :return:
            """
            instance.disabled = True

            if self.CURRENT_SELECTION_MODE == "file":
                self.run_update_progress = True
                decrypt_file(TARGET_PATH)

            elif self.CURRENT_SELECTION_MODE == "folder":
                get_filenumber_in_directory(TARGET_PATH)
                self.run_update_progress = True
                for path, dirs, files in os.walk(TARGET_PATH):
                    for file in files:
                        file_path = os.path.join(path, file)
                        decrypt_file(file_path)

                        self.ids['progressBar_id'].value += 1

                self.ids["progress_id"].text = " "
                self.ids['label_id'].text = "Processus de déchiffrement terminé"
            
            try:
                instance.disabled = False
                self.ids['progressBar_id'].value = 0
                self.ids['progressBar_id'].disabled = True
                self.ids['progressBar_id'].opacity = 0
            except Exception:
                pass
            self.run_update_progress = False
            reset_decryption_configuration()


        global TARGET_PATH
        if self.CURRENT_SELECTION_MODE == "file":
            TARGET_PATH = dt[0]
        else:
            TARGET_PATH = dt[1]

        if not TARGET_PATH or not RAW_DECRYPTION_KEY:
            self.show_error("La clé de déchiffrement et le fichier à déchiffrer sont requisent.\n"
                             "Assurez-vous de les spécifier avant de continuer.")
        else:
            thread = threading.Thread(target=pre_decryption_checks, args=[button_instance])
            thread.start()


class EncryptionSetup(BoxLayout):
    def __int__(self, **kwargs):
        super(EncryptionSetup, self).__init__(**kwargs)

    @staticmethod
    def select_encryption_algorithm(value):
        """
        Cette methode permet de specifier l'algorithme de chiffrement à utilisé
        :param value:
        :return:
        """
        global ENCRYPTION_ALGORITHM
        ENCRYPTION_ALGORITHM = str(value.value)

    @staticmethod
    def select_key_size(value):
        """
        Cette methode permet de specifier la longeur de la clé de chiffrement
        :param value:
        :return:
        """
        global ENCRYPTION_KEY_SIZE
        ENCRYPTION_KEY_SIZE = int(value.value)

    @staticmethod
    def generate_rawEncryption_key(chw, pws):
        """
        Cette methode permet de génerer une valeur de la clé
        :param chw: l'instance du TextInput
        :param pws: l'instance du TextInput saisit clé de chiffrement
        :return:
        """
        import secrets
        import string

        password = ""
        try:
            if 7 < int(chw.text) <= 256:
                characters = string.ascii_letters + string.digits + string.punctuation
                for _ in range(int(chw.text)):
                    password += ''.join(secrets.choice(characters))
            else:
                chw.text = ""
                chw.hint_text = "Valeur invalide"
        except Exception:
            chw.text = "Valeur invalide"
        else:
            pws.text = password

    @staticmethod
    def validate_config(key_value):
        global RAW_ENCRYPTION_KEY
        RAW_ENCRYPTION_KEY = key_value

    @staticmethod
    def reset_config():
        reset_encryption_configuration()


class DecryptionSetup(BoxLayout):
    def __init__(self, **kwargs):
        super(DecryptionSetup, self).__init__()

    @staticmethod
    def validate_config(key_value):
        global RAW_DECRYPTION_KEY
        RAW_DECRYPTION_KEY = key_value

    @staticmethod
    def reset_config():
        reset_decryption_configuration()


class HistoryWindow_ViewClass(BoxLayout):
    label_text = StringProperty(None)

class HistoryWindow(RelativeLayout):
    def __init__(self, **kwargs):
        super(HistoryWindow, self).__init__(**kwargs)
        self.textInput = None
        self.filechooser = None

        Clock.schedule_once(self.add_data, 0.5)

    def add_data(self, *args):
        self.ids["history_id"].data = []
        try:
            with open(HISTORY_FILE, 'rb') as htr_file:
               for line in htr_file:
                    line = line.decode()
                    line = line.rstrip('\n')
                    self.ids["history_id"].data.append({
                        "viewclass": "HistoryWindow_ViewClass",
                        "label_text": str(line + '\n'),
                    })
        except Exception as e:
            self.ids["history_id"].data = []
            self.ids["history_id"].data.append({
                "viewclass": "HistoryWindow_ViewClass",
                "label_text": str(e),
            })

    def export_history_to_pdf(self):
        def export(*args):
            """
            Cette methode permet d'exporter l'historique des opérations vers un fichier PDF
            Returns:
            """
            import time
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            popUp = lambda title, content, color:Popup(
                    title=str(title),
                    title_align="center",
                    title_color=get_color_from_hex(color),
                    title_size=18,
                    background_color=get_color_from_hex("#606060"),
                    separator_color=get_color_from_hex("#463C4B"),
                    size_hint=(.5, .2),
                    auto_dismiss=True,
                    content=Label(
                        text=str(content),
                        font_size=17,
                        color=color,
                        pos_hint={"center_x": .5, "center_y": .5}
                    )
                )

            file_path = os.path.join(self.filechooser.get_selected_path()[1], str(self.textInput.text + ".pdf"))
            if file_path == str(self.textInput.text + ".pdf"):
                popUp("Exportation Error", "Le chemin de stockage invalide", "#C94F4F").open()
            else:
                try:
                    pwd_time = time.strftime("%A %d %B %Y %Hh:%M")  # l'heure de l'enregistrement du PDF

                    c = canvas.Canvas(f"{file_path}.pdf", pagesize=letter)  # Création du document PDF
                    width, height = letter
                    title = f"HISTORIQUE DES OPERATIONS ({pwd_time})"  # le titre du document pdf

                    title_width = c.stringWidth(title, 'Helvetica', 16)  # la largeur du titre

                    c.setFont('Helvetica', 11)
                    c.drawString((width - title_width) / 2, height - 50, title)  # le positionnement du titre au center

                    i, m = 700, 0
                    with open(HISTORY_FILE, "rb") as htr_file:
                        for line in htr_file:
                            line = (line.decode()).rstrip('\n')
                            c.drawString(40, i, line)
                            i -= 15
                            m += 1
                            if m == 45:
                                c.showPage()
                                m = 0
                                i = 700
                    c.save()

                except Exception as e:
                    popUp("Exportation Error", e, "#C94F4F").open()
                else:
                    popUp("Exportation", f"Fichier {file_path}.pdf exporté avec succès", "#FFFFFF").open()


        layout = BoxLayout(orientation="vertical", spacing=5, padding=5)
        popUp = Popup(
            title="Exporter vers PDF",
            title_align="center",
            title_color=get_color_from_hex("#FFFFFF"),
            title_size=18,
            background_color=get_color_from_hex("#606060"),
            separator_color=get_color_from_hex("#463C4B"),
            size_hint=(.8, .8),
            auto_dismiss=False,
            content=layout
        )

        self.filechooser = fileChooser.CustomFileChooser()
        self.filechooser.SHOW_FILE = False
        layout.add_widget(self.filechooser)

        box1 = BoxLayout(orientation='horizontal',spacing=3,size_hint=(1, 0.1))
        label1 = Label(text="Nom du fichier:",
                       text_size=(None, None),
                       valign="center",
                       halign="center",
                       size_hint=(0.5, 1))
        box1.add_widget(label1)

        self.textInput = TextInput(multiline=False, text="history")
        box1.add_widget(self.textInput)

        label2 = Label(text=".pdf",
                       text_size=(None, None),
                       valign="center",
                       halign="left",
                       size_hint=(0.05, 1))
        box1.add_widget(label2)

        layout.add_widget(box1)

        box2 = BoxLayout(orientation='horizontal', spacing=4, size_hint=(1, 0.1))
        cancel_button = Button(text="Annuler")
        cancel_button.bind(on_release=popUp.dismiss)
        box2.add_widget(cancel_button)

        export_button = Button(text="Exporter")
        export_button.bind(on_release=export)
        box2.add_widget(export_button)

        layout.add_widget(box2)
        popUp.open()


    def confirm_delete_history(self):
        layout = BoxLayout(orientation="vertical")
        popUp = Popup(
            title="Confirmation de la suppression",
            title_align="center",
            title_color=get_color_from_hex("#FFFFFF"),
            title_size=17,
            background_color=get_color_from_hex("#606060"),
            separator_color=get_color_from_hex("#463C4B"),
            size_hint=(.5, .2),
            auto_dismiss=False,
            content=layout
        )

        message = Label(
            text="Voulez-vous supprimer l'historique des opérations ?",
            text_size=(self.width, None),
            valign='center',
            halign='center'
        )
        layout.add_widget(message)

        button_layout = BoxLayout(orientation='horizontal')
        no_button = Button(text="Non")
        no_button.bind(on_release=popUp.dismiss)
        button_layout.add_widget(no_button)

        yes_button = Button(text="Oui")
        yes_button.bind(on_release=self.clear_history)
        yes_button.bind(on_release=popUp.dismiss)
        button_layout.add_widget(yes_button)

        layout.add_widget(button_layout)
        popUp.open()

    def clear_history(self, *args):
        """
        Cette methode permet d'effacer le contenu de l'histrorique des opérations
        Returns:
        """
        try:
            with open(HISTORY_FILE, "wb") as htr_file:
                pass
        except Exception as e:
            Popup(
                title="Erreur lors de la suppression",
                title_align="center",
                title_color=get_color_from_hex("#DB5C5C"),
                title_size=17,
                background_color=get_color_from_hex("#606060"),
                separator_color=get_color_from_hex("#463C4B"),
                size_hint=(.5, .2),
                auto_dismiss=True,
                content=Label(
                    text=str(e),
                    text_size=self.size,
                    valign="center",
                    halign="center",
                    color=get_color_from_hex("#DB5C5C")
                )
            ).open()
        else:
            self.add_data(*args)

class KeyVault_ViewClass(BoxLayout):
    """
    Cette classe represente le viewClass du RecycleView de la classe KeyValut
    """
    num = StringProperty(None)
    date = StringProperty(None)
    hash = StringProperty(None)
    file_name = StringProperty(None)

class KeyVault(RelativeLayout):
    """
    Cette classe se charge de la restauration des clés de chiffrement, une fois perdue
    """
    def __init__(self, **kwargs):
        super(KeyVault, self).__init__(**kwargs)
        self.hashes = []

        Clock.schedule_once(self.add_data, 0.5)


    def restore_encryption_key(self, args1):
        customPopUp = lambda title, content, color: Popup(
            title=title,
            title_align="center",
            title_color=get_color_from_hex(color),
            title_size=18,
            background_color=get_color_from_hex("#606060"),
            separator_color=get_color_from_hex("#463C4B"),
            size_hint=(.5, .3),
            auto_dismiss=True,
            content=content
        )

        layout = BoxLayout(orientation="vertical", spacing=5, padding=[5, 2, 5, 2])
        popUp = customPopUp("Authentification",layout, "#FFFFFF")

        def restore(*args):
            popUp.dismiss()
            try:
                keys_index = int(args1) - 1
                encrypted_bytes = self.hashes[keys_index][2]

                nonce_tag = encrypted_bytes[:32]
                data = encrypted_bytes[32:]

                cipher_dec = AES.new(cryptographic_engine.derive_cryptographic_key(self.text_input.text, 128), AES.MODE_GCM,
                                 nonce=nonce_tag[:16])
                plaintext = cipher_dec.decrypt_and_verify(data, nonce_tag[16:])
            except Exception:
                customPopUp("Erreur", Label(
                        text="Mot de passe invalide",
                        font_size=17,
                        color=get_color_from_hex("#C94F4F"),
                        pos_hint={"center_x": .5, "center_y": .5}
                    ),"#C94F4F"
                ).open()
            else:
                self.display_restored_key(plaintext)


        label1 = Label(text="Mot de passe de sécurité",
                       text_size=self.size,
                       valign="center",
                       halign="center",
                       size_hint=(1, .5))
        layout.add_widget(label1)

        self.text_input = TextInput(multiline=False,
                              size_hint=(.8, .4),
                              password=True,
                              pos_hint={"center_x": .5, "center_y": .5})
        layout.add_widget(self.text_input)

        button = Button(text="Restaurer la clé",
                        size_hint=(.9, .5),
                        pos_hint={"center_x": .5, "center_y": .5})
        button.bind(on_release=restore)
        layout.add_widget(button)
        popUp.open()

    def add_data(self, *args):
        import pickle
        try:
            self.ids['restoring_id'].data = []
            with open(BACKUP_FILE, 'rb') as f:
                pick = pickle.Unpickler(f)
                i = 0
                while True:
                    i += 1
                    try:
                        data = pick.load()
                        self.hashes.append(data)
                        self.ids['restoring_id'].data.append({
                            "viewclass": "KeyVault_ViewClass",
                            "num": str(i),
                            "date": str(data[1]),
                            "file_name": str(data[0]),
                            "hash": str(data[2])
                        }
                        )
                    except EOFError:
                        break
        except Exception:
            pass

    @staticmethod
    def display_restored_key(key):
        Popup(
            title="Valeur de la clé de chiffrement",
            title_align="center",
            title_color=get_color_from_hex("#FFFFFF"),
            title_size=15,
            background_color=get_color_from_hex("#606060"),
            separator_color=get_color_from_hex("#463C4B"),
            size_hint=(.8, .2),
            auto_dismiss=True,
            content=TextInput(
                text=key,
                readonly=True,
                allow_copy=True,
                cursor_color=(1, 1, 1, .04),
                background_color=(1, 1, 1, .04),
                foreground_color="white",
                multiline=False
            )
        ).open()


    def delete_backup(self):
        cutomPopup = lambda title, content, color: Popup(
                    title=title,
                    title_align="center",
                    title_color=get_color_from_hex(color),
                    title_size=17,
                    background_color=get_color_from_hex("#606060"),
                    separator_color=get_color_from_hex("#463C4B"),
                    size_hint=(.5, .3),
                    auto_dismiss=True,
                    content=content
                )
        def delete():
            """
            Cette methode permet d'effacer la sauvegarde des clés
            :return:
            """
            try:
                with open(BACKUP_FILE, "wb") as htr_file:
                    pass
            except Exception as e:
                cutomPopup("Erreur lors de la suppression", Label(
                        text=str(e),
                        text_size=self.size,
                        valign="center",
                        halign="center",
                        color=get_color_from_hex("#DB5C5C")
                    ), "#DB5C5C"
                ).open()
            else:
                self.add_data()

        def authenticate(*args):
            layout = BoxLayout(orientation="vertical", spacing=5, padding=[5, 2, 5, 2])
            popUp = cutomPopup("Authentification", layout, "#FFFFFF")

            def check_passWord(*args):
                try:
                    pwd = None
                    with open(MASTER_PWD_FILE, "rb") as pw_file:
                        pickle_object = pickle.Unpickler(pw_file)
                        pwd = pickle_object.load()

                    if bcrypt.checkpw(str(self.text_input.text).encode('utf-8'), pwd):
                        delete()
                        popUp.dismiss()
                    else:
                        cutomPopup("Erreur", Label(
                                text="Mot de passe invalide",
                                font_size=17,
                                color=get_color_from_hex("#C94F4F"),
                                pos_hint={"center_x": .5, "center_y": .5}
                            ),"#C94F4F"
                        ).open()
                except Exception:
                    pass

            label1 = Label(text="Saisir votre mot de passe",
                           valign="center",
                           halign="center",
                           size_hint=(1, .5))
            layout.add_widget(label1)
            self.text_input = TextInput(multiline=False,
                                        size_hint=(.8, .4),
                                        password=True,
                                        pos_hint={"center_x": .5, "center_y": .5},
                                        on_text_validate=check_passWord)
            layout.add_widget(self.text_input)
            button = Button(text="Valider",
                            size_hint=(.9, .5),
                            pos_hint={"center_x": .5, "center_y": .5})
            button.bind(on_release=check_passWord)
            layout.add_widget(button)
            popUp.open()


        layout = BoxLayout(orientation="vertical")
        popUp = cutomPopup("Confirmation de la suppression", layout, "#FFFFFF")

        message = Label(
            text="Voulez-vous supprimer l'ensemble de vos sauvegarde ?",
            text_size=(self.width, None),
            valign='center',
            halign='center'
        )
        layout.add_widget(message)

        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, .4))

        no_button = Button(text="Non")
        no_button.bind(on_release=popUp.dismiss)
        button_layout.add_widget(no_button)

        yes_button = Button(text="Oui")
        yes_button.bind(on_release=authenticate)
        yes_button.bind(on_release=popUp.dismiss)
        button_layout.add_widget(yes_button)

        layout.add_widget(button_layout)
        popUp.open()
