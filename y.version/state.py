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
    def language(self, message=None, call=None):
        pass

    @abstractmethod
    def data_base(self, message, call):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def inline_buttons(self, message, call):
        pass

    @abstractmethod
    def printing(self, message, call):
        pass

    @abstractmethod
    def sentence_buttons(self, message=None, call=None):
        pass

    @abstractmethod
    def menu(self, message, call):
        pass

    @abstractmethod
    def vars(self, message, sents, count):
        pass

    @abstractmethod
    def hello(self, message) -> None:
        pass

    @abstractmethod
    def text_to_sents(self, message, call):
        pass

    @abstractmethod
    def sents_to_words(self, message, sents):
        pass

    @abstractmethod
    def write_word(self, message):
        pass

    @abstractmethod
    def random_words(self):
        pass

    @abstractmethod
    def buttons(self, message):
        pass

    @abstractmethod
    def instructions(self, message) -> None:
        pass
