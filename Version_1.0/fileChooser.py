# -----------------------------------------------------------------------------
# Python 3.10                                                                |
# Kivy 1.2.0                                                               |
# Copyright (c), 22/06/2024, Developped by Isaac Bumizi                      |
# -----------------------------------------------------------------------------

import os
import sys
import pathlib
import win32api

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, ListProperty, BooleanProperty

Builder.load_string("""
#:import get_color_from_hex kivy.utils.get_color_from_hex
<CustomFileChooser>:
    orientation: "vertical"
    padding: [0, 7, 0, 0]
    RelativeLayout:
        RecycleView:
            id: recycleView_id
            key_viewclass: 'viewclass'
            key_size: 'height'
            bar_color: get_color_from_hex("#9F9F9F")
            scroll_type: ['bars', 'content']
            bar_width: 8
            RecycleBoxLayout:
                padding: [4, 5, 4, 5]
                default_size: None, dp(35)
                default_size_hint: 1, None
                size_hint_y: None
                height: self.minimum_height
                orientation: 'vertical'
    BoxLayout:
        size_hint: 1, .15
        padding: [10, 5, 10, 10]
        orientation: "horizontal"
        spacing: 1
        Label:
            text: str(root.PATH_NAMES[0])
            color: "grey"
            font_size: 12
            text_size: self.size
            halign: "left"
            valign: "center"
            opacity: 1 if root.SHOW_FOLDER else 0
        Label:
            text: str(root.PATH_NAMES[1])
            color: "grey"
            font_size: 12
            text_size: self.size
            halign: "left"
            valign: "center"
            opacity: 1 if root.SHOW_FILE else 0


<CustomLineListItem>:
    orientation: "horizontal"
    padding: [10, .5, 10, .5]
    spacing: 7
    canvas.before:
        Color:
            rgba: root.ITEM_COLOR_PROPERTY
        Rectangle:
            size: self.size
            pos: self.pos

    Image:
        source: root.ITEM_ICON
        size_hint: None, None
        size: '22dp', '22dp'
        pos_hint: {"center_x": .5, "center_y": .5}
    Label:
        text: str(root.NAME)
        text_size: self.size
        halign: "left"
        valign: "center"
        font_size: 16
        on_touch_down: root.on_label_click(*args, label_object=self)
    Label:
        text: str(root.ITEM_SIZE)
        font_size: 15
        size_hint: .2, 1
        text_size: self.size
        halign: "right"
        valign: "center"
""")

class CustomLineListItem(BoxLayout):
    NAME = StringProperty()
    ITEM_SIZE = StringProperty()
    ITEM_ICON = StringProperty()
    ITEM_COLOR_PROPERTY = ListProperty()

    def __init__(self, **kwargs):
        super(CustomLineListItem, self).__init__(**kwargs)

    def on_label_click(self, instance, touch, label_object):
        """
        Cette methode permet de gerer l'action du click sur le label
        :param instance:
        :param touch:
        :param label_object:
        :return:
        """
        if self.collide_point(*touch.pos):
            self.parent.parent.parent.parent.go_to_path(label_object)


class CustomFileChooser(BoxLayout):
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        BASE_DIR = sys._MEIPASS
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    RETURN_ICON = os.path.join(BASE_DIR, 'images', 'filemanager_go_back.png')
    FOLDER_ICON = os.path.join(BASE_DIR, 'images', 'filemanager_folder.png')
    FILE_ICON = os.path.join(BASE_DIR, 'images', 'filemanager_file.png')
    DISK_ICON = os.path.join(BASE_DIR, 'images', 'filemanager_disk.png')

    ITEM_COLOR = [(1, 1, 1, .05), (1, 1, 1, .02)]
    # Variable de stockage du nom du dossier et celui du fichier sélectionné
    PATH_NAMES = ListProperty(["Dossier: ", "Fichier: "])
    SHOW_FOLDER = BooleanProperty(True) # Si True affiche le chemin du dossier sélectionné
    SHOW_FILE = BooleanProperty(True) # Si True affiche le chemin du fichier sélectionné

    def __init__(self, **kwargs):
        super(CustomFileChooser, self).__init__(**kwargs)

        Clock.schedule_once(self.show_system_logicalDrive, 1)

        self.item_color_index = 0  # L'indice qui permet d'alterner les couleurs d'affichage
        self.partitions_list = [] #La liste des partitions du disques
        self.nodes_list = [] #La liste des noeuds visité
        self.current_path = ""  # Le chemin au temps T

        self.current_file_name = ""  # Le dossier dans lequel on se trouve
        self.current_folder_name = ""  # Le dernier fichier selectionné

        self.layout = lambda layout_name, item_size, item_icon: {
            "viewclass": "CustomLineListItem",
            "NAME": layout_name,
            "ITEM_SIZE": item_size,
            "ITEM_ICON": item_icon,
            "ITEM_COLOR_PROPERTY": self.ITEM_COLOR[self.item_color_index]
        }

        self.popup = lambda x: Popup(
            title="",
            size_hint=(.8, .3),
            separator_color=(1, 1, 1, 1),
            auto_dismiss=True,
            content=Label(
                text=str(x),
                pos_hint={"center_x": .5, "center_y": .5}
            )
        )

    def get_selected_path(self):
        """
        Cette methode permet de retourner le chemin du fichier ou dossier sélectionné
        :return:
        """
        return [self.current_file_name, self.current_folder_name]


    def show_system_logicalDrive(self, *args):
        """
        Cette methode permet d'afficher les partitions présents sur le disque
        """
        def get_system_LogicalDriveString1A():
            """
            Cette fonction permet de récuperer les partitions du disque
            """
            logicalDrive = win32api.GetLogicalDriveStrings()
            logicalDrive = (str(logicalDrive)).split("\x00")
            logicalDrive.remove('')
            return logicalDrive

        try:
            self.ids['recycleView_id'].data.clear()
            for drive in get_system_LogicalDriveString1A():
                self.partitions_list.append(drive)
                self.ids['recycleView_id'].data.append(
                    self.layout(str(drive), "", CustomFileChooser.DISK_ICON)
                )
                if self.item_color_index < 1:
                    self.item_color_index += 1
                else:
                    self.item_color_index -= 1
        except Exception:
            self.popup("Erreur lors de l'ouverture du gestionnaire des fichiers, redémarrez le programme").open()

    def go_to_path(self, clicklb):
        """
        Avec l'action du clic sur un élément du recycleView,
        Cette methode permet de naviguer vers le screen secondaire
        :param clicklb: Le nom de l'élement clické sur le recycleView
        :return:
        """
        try:
            if clicklb.text in self.partitions_list and not pathlib.Path(clicklb.text).exists():
                self.popup("La partition selectionnée n'est pas prête").open()
            else:
                if clicklb.text == "..\\":  # Si l'utilisateur click sur return
                    if len(self.nodes_list) <= 1:  # Si l'utilisateur veut retourner à la racine du disque
                        self.current_path = self.current_folder_name = self.current_file_name = ""
                        self.nodes_list.pop()
                        self.ids['recycleView_id'].data = []
                        self.show_system_logicalDrive()
                    else:
                        self.nodes_list.pop() if len(self.nodes_list) > 0 else None
                        self.current_path = "\\".join(self.nodes_list)
                        self.ids['recycleView_id'].data = []

                        self.ids['recycleView_id'].data.append(
                            self.layout("..\\", "Taille", CustomFileChooser.RETURN_ICON)
                        )
                        self.initialise_recycleView_content(self.current_path)

                    pw_d = self.current_folder_name.split("\\")
                    self.current_folder_name = "\\".join(pw_d[:-1])
                else:
                    path = os.path.join(self.current_path, clicklb.text)
                    if os.path.isdir(path):
                        self.nodes_list.append(clicklb.text)
                        self.current_path = self.current_folder_name = path

                        if len(self.nodes_list) > 0:
                            self.ids['recycleView_id'].data = []
                            self.ids['recycleView_id'].data.append(
                                self.layout("..\\", "Taille", CustomFileChooser.RETURN_ICON)
                            )
                            self.initialise_recycleView_content(self.current_path)
                    else:
                        if pathlib.Path(path).exists():
                            self.current_file_name = path
                        else:
                            self.popup("Le fichier ou dossier sélectionné à été déplacé ou n'existe plus").open()
                            self.current_file_name = ""
                            self.ids['recycleView_id'].data = []
                            self.ids['recycleView_id'].data.append(
                                self.layout("..\\", "Taille", CustomFileChooser.RETURN_ICON)
                            )
                            self.initialise_recycleView_content(self.current_path)
        except Exception as e:
            self.popup(str(e)).open()
            self.nodes_list.pop() if len(self.nodes_list) > 0 else None
            self.current_path = "\\".join(self.nodes_list)

            self.ids['recycleView_id'].data = []
            self.ids['recycleView_id'].data.append(
                self.layout("..\\", "Taille", CustomFileChooser.RETURN_ICON)
            )
            self.initialise_recycleView_content(self.current_path)

        finally:
            self.PATH_NAMES[0] = "Dossier : " + self.current_folder_name
            self.PATH_NAMES[1] = "Fichier : " + (self.current_file_name.split("\\"))[-1]

    def initialise_recycleView_content(self, path):
        """
        Cette methode permet d'afficher les éléments dans le recycleView
        :param path: le chemin des élement à afficher
        :return:
        """
        for value in os.listdir(path):
            file_path = os.path.join(path, value)

            if not (os.stat(file_path).st_file_attributes & 2) == 2: # Verification si le fichier n'a pas un attribut caché
                if pathlib.Path(os.path.join(path, value)).is_file():
                    file_size = "%.3f Mo" % (os.path.getsize(file_path) / (1024 * 1024))
                    self.ids['recycleView_id'].data.append(
                        self.layout(str(value), file_size, CustomFileChooser.FILE_ICON)
                    )
                else:
                    self.ids['recycleView_id'].data.insert(
                        1, self.layout(str(value), " ", CustomFileChooser.FOLDER_ICON)
                    )

                if self.item_color_index < 1:
                    self.item_color_index += 1
                else:
                    self.item_color_index -= 1