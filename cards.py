from enum import Enum
import random
from typing import List, Optional


class CardType(Enum):
    NUMBER = "number"
    WILD = "wild"
    SKIP = "skip"


class Color(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"


class Card:
    def __init__(self, rank: Optional[int], color: Color, card_type: CardType = CardType.NUMBER):
        self.rank = rank
        self.color = color
        self.card_type = card_type
        
    def __str__(self) -> str:
        if self.card_type == CardType.WILD:
            return "Wild"
        elif self.card_type == CardType.SKIP:
            return "Skip"
        else:
            return f"{self.rank} {self.color.value.capitalize()}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def get_points(self) -> int:
        if self.card_type == CardType.WILD:
            return 25
        elif self.card_type == CardType.SKIP:
            return 15
        elif self.rank is not None and self.rank >= 10:
            return 10
        else:
            return 5
    
    def can_substitute(self, target_rank: int) -> bool:
        return self.card_type == CardType.WILD or self.rank == target_rank


class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self._create_deck()
        self.shuffle()
    
    def _create_deck(self):
        colors = list(Color)
        
        # Add 24 of each number (1-12) - 2 per color
        for rank in range(1, 13):
            for color in colors:
                self.cards.append(Card(rank, color))
                self.cards.append(Card(rank, color))
        
        # Add 8 wild cards (2 per color)
        for color in colors:
            self.cards.append(Card(None, color, CardType.WILD))
            self.cards.append(Card(None, color, CardType.WILD))
        
        # Add 4 skip cards (1 per color)
        for color in colors:
            self.cards.append(Card(None, color, CardType.SKIP))
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def draw_card(self) -> Optional[Card]:
        if len(self.cards) == 0:
            return None
        return self.cards.pop()
    
    def cards_remaining(self) -> int:
        return len(self.cards)
    
    def is_empty(self) -> bool:
        return len(self.cards) == 0


class DiscardPile:
    def __init__(self):
        self.cards: List[Card] = []
    
    def add_card(self, card: Card):
        self.cards.append(card)
    
    def take_top_card(self) -> Optional[Card]:
        if len(self.cards) == 0:
            return None
        return self.cards.pop()
    
    def peek_top_card(self) -> Optional[Card]:
        if len(self.cards) == 0:
            return None
        return self.cards[-1]
    
    def is_empty(self) -> bool:
        return len(self.cards) == 0
    
    def size(self) -> int:
        return len(self.cards)