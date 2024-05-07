from __future__ import annotations
from abc import ABC, abstractmethod

class State(ABC):
    """
    Базовый класс Состояния объявляет методы, которые должны реализовать все
    Конкретные Состояния, а также предоставляет обратную ссылку на объект
    Контекст, связанный с Состоянием. Эта обратная ссылка может использоваться
    Состояниями для передачи Контекста другому Состоянию.
    """

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context) -> None:
        self._context = context


    @abstractmethod
    def build_for_sents(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def work_with_text(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def inline_buttons(self, message=None, call=None):
        pass

    @abstractmethod
    def print_words(self, message, call):
        pass

    @abstractmethod
    def menu(self, message, call):
        pass

    @abstractmethod
    def hello(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def text_to_sents(self, message, call):
        pass

    @abstractmethod
    def sent_to_words(self, *args, **kwargs):
        pass

    @abstractmethod
    def  save_word(self, message):
        pass

    @abstractmethod
    def random_words(self):
        pass

    @abstractmethod
    def words_buttons(self, message):
        pass

    @abstractmethod
    def instructions(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def detect_language(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_language_fullname(self, *args, **kwargs):
        pass

    @abstractmethod
    def save_text(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def text_window_buttons(self, *args, **kwargs):
        pass

    @abstractmethod
    def send_text_window(self, *args, **kwargs):
        pass