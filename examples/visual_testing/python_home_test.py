from seleniumbase import BaseCase
BaseCase.main(__name__, __file__)


class VisualLayoutTests(BaseCase):
    def test_python_home_layout_change(self):
        self.open("https://python.org/")
