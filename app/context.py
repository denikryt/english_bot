from __future__ import annotations
from abc import ABC, abstractmethod
from state import State
from default import Default

class Context:
    """
    Контекст определяет интерфейс, представляющий интерес для клиентов. Он также
    хранит ссылку на экземпляр подкласса Состояния, который отображает текущее
    состояние Контекста.
    """

    _state = None
    """
    Ссылка на текущее состояние Контекста.
    """
    # def __str__ (self, state: State) -> None:
    #     return state.__name__

    def __init__(self, initial_state: State = None) -> None:
        if initial_state:
            self.transition_to(initial_state)

    def transition_to(self, state: State):
        """
        Контекст позволяет изменять объект Состояния во время выполнения.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    def set_default_state(self):
        self._state = Default() 

    def current_state(self):
        """
        Возвращает имя текущего состояния или None, если состояние не установлено.
        """
        if self._state:
            return type(self._state).__name__
        else:
            return None

    """
    Контекст делегирует часть своего поведения текущему объекту Состояния.
    """

    def build_for_sents(self, *args, **kwargs):
        self._state.build_for_sents(*args, **kwargs)

    def send_text_window(self, *args, **kwargs):
        self._state.send_text_window(*args, **kwargs)

    def text_window_buttons(self, *args, **kwargs):
        self._state.text_window_buttons(*args, **kwargs)

    def detect_language(self, *args, **kwargs):
        self._state.detect_language(*args, **kwargs)

    def get_language_fullname(self, *args, **kwargs):
        self._state.get_language_fullname(*args, **kwargs)

    def save_text(self, *args, **kwargs):
        return self._state.save_text(*args, **kwargs)

    def work_with_text(self, *args, **kwargs):
        self._state.work_with_text(*args, **kwargs)

    def inline_buttons(self, message=None, call=None):
        self._state.inline_buttons(message, call)

    def print_words(self, *args, **kwargs):
        self._state.printing(self, *args, **kwargs)

    def menu(self,message, call):
        self._state.menu(self,message, call)

    def hello(self, *args, **kwargs):
        self._state.hello(*args, **kwargs)

    def text_to_sents(self, message, call):
        self._state.text_to_sents(message, call)

    def sent_to_words(self, *args, **kwargs):
        self._state.sent_to_words(*args, **kwargs)
    
    def save_word(self, message):
        self._state.write_word(message)

    def random_words(self, message, call):
        self._state.random_words(message)

    def words_buttons(self, message):
        self._state.buttons(message)

    def instructions(self, *args, **kwargs):
        self._state.instructions(*args, **kwargs)
