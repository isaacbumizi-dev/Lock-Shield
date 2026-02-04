import os
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from kivy.uix.popup import Popup
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.utils import get_color_from_hex
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.relativelayout import MDRelativeLayout

from gui.components import fileChooser
from kivymd.uix.textfield import MDTextField


class HistoryViewClass(MDBoxLayout):
    content = StringProperty(None)
    status = StringProperty(None)

class HistoryWindow(MDRelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.running_app = MDApp.get_running_app()
        Clock.schedule_once(self.add_data, 0.5)

    def add_data(self, *args):
        """
        Cette methode ajoute les données sur l'ecran
        :param *args
        :return
        """
        try:
            self.ids['history_viewclass_id'].data = []
            history_content = self.running_app.DATABASE_MANAGER.get_history()

            if not history_content:
                self.ids['history_viewclass_id'].data.append({
                    "viewclass": "MDLabel",
                    "text": "Aucun historique disponible",
                    "valign": "center",
                    "halign": "center"
                })
                return

            with open(os.path.join(self.running_app.DATA_STORGAGE, "historique"), "wb") as f:
                for data in history_content:
                    if data.get('status') == "Succès":
                        viewclass_data = f"""
Date: {data.get('operation_date')}
        Opération: {data.get('operation')}
        Fichier: {data.get('file')}
        Taille: {data.get('size')}
        Statut: {data.get('status')}
        Durée: {data.get('duration')} Sécondes
        Algorithme: {data.get('algorithm')} bits\n
                        """
                    else:
                        viewclass_data = f"""
Date: {data.get('operation_date')}
        Opération: {data.get('operation')}
        Fichier: {data.get('file')}
        Taille: {data.get('size')}
        Statut: {data.get('status')}
        Raison: {data.get('problem')}
        Algorithme: {data.get('algorithm')} bits\n
                        """

                    self.ids['history_viewclass_id'].data.append({
                        "viewclass": "HistoryViewClass",
                        "content": viewclass_data,
                        "status": data.get('status')
                    })

                    f.write(viewclass_data.encode())

        except Exception as e:
            self.ids['history_viewclass_id'].data = []
            self.ids['history_viewclass_id'].data.append({
                "viewclass": "HistoryViewClass",
                "content": str(e),
                "status": "error"
            })

    def erase_history(self):
        """
        Cette methode supprime l'ensemble de l'historique des opérations dans la base des données
        :param
        """
        if len(self.ids['history_viewclass_id'].data) == 0:
            return

        dialog_box = None
        def _close_dialog_box(*args):
            if dialog_box:
                dialog_box.dismiss()

        def _erase_history(*args):
            _close_dialog_box()
            erase_result = self.running_app.DATABASE_MANAGER.erase_history()
            if erase_result:
                self.add_data()


        dialog_box = MDDialog(
            title="Confirmation requise",
            text="Voulez-vous supprimer l'historique des opérations ?",
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
                    on_release=_erase_history
                )
            ],
        )
        dialog_box.open()

    def export_to_pdf(self):
        """
        Cette methode export les données de l'historique vers un fichier pdf
        :return
        """
        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=5)
        popUp = Popup(
            title="Exportation vers PDF",
            title_align="center",
            title_color=get_color_from_hex("#FFFFFF"),
            title_size=17,
            background_color=get_color_from_hex("#606060"),
            separator_color=get_color_from_hex("#463C4B"),
            size_hint=(None, None),
            size=(812.6, 652),
            auto_dismiss=False,
            content=layout
        )

        def export(*args):
            dialog_box = lambda stitle, content: MDDialog(
                title=str(stitle),
                text=str(content),
                radius=[5, 5, 5, 5],
                auto_dismiss=True,
            )

            selected_path = self.filechooser.get_selected_path()[1]
            file_path = os.path.join(selected_path, str(self.textInput.text + ".pdf"))

            if os.path.exists(file_path) or not selected_path.strip() or selected_path=="":
                dialog_box("Erreur d'exportation", "Nom du fichier invalide").open()
            else:
                try:
                    exp_time = time.strftime("%A %d %B %Y %Hh:%M")

                    c = canvas.Canvas(f"{file_path}", pagesize=letter)  # Création du document PDF
                    width, height = letter
                    title = f"HISTORIQUE DES OPERATIONS ({exp_time})"  # le titre du document pdf

                    title_width = c.stringWidth(title, 'Helvetica', 16)  # la largeur du titre

                    c.setFont('Helvetica', 11)
                    c.drawString((width - title_width) / 2, height - 50, title)  # le positionnement du titre au center

                    i, m = 700, 0
                    with open(os.path.join(self.running_app.DATA_STORGAGE, "historique"), "rb") as htr_file:
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
                    dialog_box("Erreur d'exportation", e).open()
                else:
                    dialog_box("Exportation réussie", f"Fichier {file_path} exporté avec succès.").open()
                    popUp.dismiss()


        self.filechooser = fileChooser.CustomFileChooser()
        self.filechooser.SHOW_FILE = False
        layout.add_widget(self.filechooser)

        box1 = MDBoxLayout(
            orientation='horizontal',
            spacing=3,
            size_hint=(.9, 0.1),
            pos_hint={"center_x": .5, "center_y": .5}
        )

        self.textInput = MDTextField(
            multiline=False,
            text="historique",
            mode="rectangle",
            hint_text="Nom du fichier",
            size_hint=(1, 1)
        )
        box1.add_widget(self.textInput)

        label2 = MDLabel(text=".pdf",
                       text_size=(None, None),
                       valign="center",
                       halign="left",
                       size_hint=(0.5, 1))
        box1.add_widget(label2)

        layout.add_widget(box1)

        box2 = MDBoxLayout(
            orientation='horizontal',
            spacing=5,
            size_hint=(.9, .07),
            pos_hint={"center_x": .5, "center_y": .5}
        )
        cancel_button = MDRaisedButton(text="Annuler", size_hint=(1, 1))
        cancel_button.bind(on_release=popUp.dismiss)
        box2.add_widget(cancel_button)

        export_button = MDRaisedButton(text="Exporter", size_hint=(1, 1))
        export_button.bind(on_release=export)
        box2.add_widget(export_button)

        layout.add_widget(box2)
        popUp.open()