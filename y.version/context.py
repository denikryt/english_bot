from __future__ import annotations
from abc import ABC, abstractmethod
from state import State

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

    def __init__(self, state: State) -> None:
        self.transition_to(state)

    def transition_to(self, state: State):
        """
        Контекст позволяет изменять объект Состояния во время выполнения.
        """

        print(f"Context: Transition to {type(state).__name__}")
        self._state = state
        self._state.context = self

    """
    Контекст делегирует часть своего поведения текущему объекту Состояния.
    """

    def language(self, message, call):
        self._state.language(message,call)

    def data_base(self, message, call):
        self._state.data_base(message,call)

    def reset(self):
        self._state.reset()

    def inline_buttons(self, message, call):
        self._state.inline_buttons(message, call)

    def printing(self, message, call):
        self._state.printing(self, chat_id)
    
    def sentence_buttons(self, message, call):
        self._state.sentence_buttons(self, message, call)

    def menu(self,message, call):
        self._state.menu(self,message, call)

    def vars(self, message, call, sents, count, lang):
        self._state.vars(message, call, sents, count, lang)

    def hello(self, message, call):
        self._state.hello(message, call)

    def text_to_sents(self, message, call):
        self._state.text_to_sents(message, call)

    def sents_to_words(self, message, call, sents):
        self._state.sents_to_words(message, call, sents)
    
    def write_word(self, message):
        self._state.write_word(message)

    def random_words(self, message, call):
        self._state.random_words(message)

    def buttons(self, message):
        self._state.buttons(message)

    def instructions(self, message):
        self._state.instructions(message)
