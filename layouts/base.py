from abc import ABC, abstractmethod

class BaseLayout(ABC):
    layout = None

    def __init__(self):
        super.__init__(self)
        self.layout = self.layout()

    @abstractmethod
    def render(self):
        pass
