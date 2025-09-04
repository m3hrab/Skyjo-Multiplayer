# game/deck.py
import random

class Deck:
    def __init__(self):
        self.cards = self._generate_deck()
        random.shuffle(self.cards)

    def _generate_deck(self):
        # Originale Skyjo-Verteilung:
        # -2: 5x, 0: 15x, andere (1-12): je 10x, -1: 10x
        distribution = {
            -2: 5,
            -1: 10,
            0: 15,
            1: 10,
            2: 10,
            3: 10,
            4: 10,
            5: 10,
            6: 10,
            7: 10,
            8: 10,
            9: 10,
            10: 10,
            11: 10,
            12: 10,
        }
        deck = []
        for value, count in distribution.items():
            deck.extend([value] * count)
        return deck

    def draw_card(self):
        return self.cards.pop() if self.cards else None

    def is_empty(self):
        return len(self.cards) == 0

    def cards_left(self):
        return len(self.cards)
