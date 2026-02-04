from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivymd.uix.card import MDCard
from kivymd.uix.circularlayout import MDCircularLayout


class CustomSpinner(MDCircularLayout):
    _DOTS = NumericProperty(12) # Le nombre totâl des points du Spinner
    _TRAIL = NumericProperty(10) # La trainé du spinner
    _DICT_COLORS = {
        "white": (1, 1, 1, 1),
        "red": (1, 0, 0, 1),
        "green": (0, 1, 0, .8),
        "blue": (0, 0, 1, 1),
    } # Les couleurs de base et leur correspondance RGB

    def __init__(self, color = (1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)

        self.base_color = self._normalize_color(color)
        self.current_index = 0

        self.spinner_colors = None
        self._generate_spinner_colors()

        self.circular_radius = 25
        self.size_hint = (None, None)
        self.size = (dp(60), dp(60))
        self.md_bg_color = (0, 0, 0, 0)

        for _ in range(int(self._DOTS)):
            self.add_widget(
                MDCard(
                    size_hint=(None, None),
                    size=(dp(10), dp(10)),
                    radius=[dp(50)],
                    md_bg_color=self.spinner_colors[-1]
                )
            )

        self._spinner_schedule = Clock.schedule_interval(self._run_spinner, 1 / 20)

    def _normalize_color(self, color: (str,tuple)) -> (tuple,list):
        """
        Cette methode permet de normaliser la couleur passée en paramètre
        :param color: la couleur de base
        :return: la valeur de la couleur normalisée
        """
        if isinstance(color, str):
            return self._DICT_COLORS.get(color.lower(), (1, 1, 1, 1))
        if isinstance(color, (tuple, list)) and len(color) in (3, 4):
            return tuple(color) if len(color) == 4 else (*color, 1)
        return [1, 1, 1, 1]

    def _generate_spinner_colors(self) -> None:
        """
        Cette methode permet de génerer les couleurs du CustomSpinner à partir de la couleur passée en paramètre
        :return: None
        """
        base_color = self.base_color
        trail = int(self._TRAIL)
        color_intensity = [(i + 1) / trail for i in reversed(range(trail))]
        self.spinner_colors = [(
            base_color[0],
            base_color[1],
            base_color[2],
            i) for i in color_intensity
        ]

    def _run_spinner(self, *args) -> None:
        """
        Cette methode permet de faire evoluer la progression du widget CustomSpinner
        :param args:
        :return: None
        """
        if self.current_index < len(self.children):
            self.children[self.current_index].md_bg_color = self.base_color
            for i in range(self._TRAIL):
                self.children[self.current_index - (i+1)].md_bg_color = self.spinner_colors[i]

            self.current_index += 1
            if self.current_index > len(self.children) - 1:
                self.current_index = 0

    def stop_spinner(self):
        self._spinner_schedule.cancel()
        if self.parent:
            self.parent.remove_widget(self)