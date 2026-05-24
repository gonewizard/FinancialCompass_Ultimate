class BaseTab:
    def __init__(self, parent, app, current_user):
        self.parent = parent
        self.app = app
        self.current_user = current_user
        self._create_widgets()

    def _create_widgets(self):
        pass

    def refresh(self):
        pass