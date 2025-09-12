from typing import List, Optional
from cards import Card, Deck, DiscardPile, CardType
from player import Player
from phases import PHASES


class GameState:
    def __init__(self):
        self.current_player_index = 0
        self.round_number = 1
        self.game_over = False
        self.winner: Optional[Player] = None


class Phase10Game:
    def __init__(self, player_names: List[str]):
        if not (2 <= len(player_names) <= 6):
            raise ValueError("Phase 10 requires 2-6 players")
        
        self.players = [Player(name) for name in player_names]
        self.deck = Deck()
        self.discard_pile = DiscardPile()
        self.state = GameState()
        
        # Deal initial cards and set up discard pile
        self._deal_cards()
        self._setup_discard_pile()
    
    def _deal_cards(self):
        """Deal 10 cards to each player"""
        for _ in range(10):
            for player in self.players:
                card = self.deck.draw_card()
                if card:
                    player.add_card_to_hand(card)
    
    def _setup_discard_pile(self):
        """Place the first card on the discard pile"""
        first_card = self.deck.draw_card()
        if first_card:
            self.discard_pile.add_card(first_card)
    
    def get_current_player(self) -> Player:
        """Get the player whose turn it is"""
        return self.players[self.state.current_player_index]
    
    def get_next_player_index(self, skip_count: int = 1) -> int:
        """Get the index of the next player, accounting for skips"""
        return (self.state.current_player_index + skip_count) % len(self.players)
    
    def advance_turn(self, skip_count: int = 1):
        """Move to the next player's turn"""
        self.state.current_player_index = self.get_next_player_index(skip_count)
    
    def draw_from_deck(self) -> Optional[Card]:
        """Draw a card from the deck"""
        return self.deck.draw_card()
    
    def draw_from_discard(self) -> Optional[Card]:
        """Draw the top card from the discard pile"""
        return self.discard_pile.take_top_card()
    
    def peek_discard_top(self) -> Optional[Card]:
        """Peek at the top card of the discard pile without removing it"""
        return self.discard_pile.peek_top_card()
    
    def discard_card(self, player: Player, card: Card) -> bool:
        """Player discards a card"""
        if player.remove_card_from_hand(card):
            self.discard_pile.add_card(card)
            return True
        return False
    
    def player_draw_card(self, player: Player, from_discard: bool = False) -> Optional[Card]:
        """Player draws a card from either deck or discard pile"""
        if from_discard:
            card = self.draw_from_discard()
        else:
            card = self.draw_from_deck()
            
        if card:
            player.add_card_to_hand(card)
        
        return card
    
    def can_player_complete_phase(self, player: Player, selected_cards: List[Card]) -> bool:
        """Check if player can complete their current phase with selected cards"""
        return player.can_complete_phase(selected_cards)
    
    def player_complete_phase(self, player: Player, selected_cards: List[Card]) -> bool:
        """Player attempts to complete their current phase"""
        return player.complete_phase(selected_cards)
    
    def player_hit_on_phase(self, player: Player, card: Card, target_player: Player) -> bool:
        """Player hits on another player's completed phase"""
        return player.hit_on_phase(card, target_player)
    
    def player_hit_on_own_phase(self, player: Player, card: Card) -> bool:
        """Player hits on their own completed phase"""
        return player.hit_on_own_phase(card)
    
    def handle_skip_card(self, skip_card: Card) -> int:
        """Handle skip card logic and return number of players to skip"""
        if len(self.players) == 2:
            # In 2-player games, skip allows current player to take another turn
            return 0
        else:
            # In multiplayer games, skip the next player
            return 2
    
    def check_round_end(self) -> bool:
        """Check if the current round has ended (someone went out)"""
        for player in self.players:
            if player.get_hand_size() == 0:
                return True
        return False
    
    def end_round(self) -> Player:
        """End the current round and calculate scores"""
        # Find the player who went out
        round_winner = None
        for player in self.players:
            if player.get_hand_size() == 0:
                round_winner = player
                break
        
        # Calculate scores
        if round_winner:
            for player in self.players:
                if player != round_winner:
                    points = player.get_hand_points()
                    round_winner.score += points
        
        # Advance players to next phase if they completed their current phase
        for player in self.players:
            if player.completed_phase_this_round:
                player.advance_to_next_phase()
        
        return round_winner
    
    def start_new_round(self):
        """Start a new round"""
        self.state.round_number += 1
        
        # Reset players for new round
        for player in self.players:
            player.reset_for_new_round()
        
        # Create new deck and deal cards
        self.deck = Deck()
        self.discard_pile = DiscardPile()
        
        self._deal_cards()
        self._setup_discard_pile()
    
    def check_game_end(self) -> bool:
        """Check if the game has ended"""
        # Check if anyone has completed all phases
        completed_all_phases = []
        for player in self.players:
            if player.is_finished_with_all_phases():
                completed_all_phases.append(player)
        
        if len(completed_all_phases) == 1:
            # One player completed all phases
            self.state.winner = completed_all_phases[0]
            self.state.game_over = True
            return True
        elif len(completed_all_phases) > 1:
            # Multiple players completed all phases in same round - highest score wins
            self.state.winner = max(completed_all_phases, key=lambda p: p.score)
            self.state.game_over = True
            return True
        
        return False
    
    def get_game_status(self) -> dict:
        """Get current game status information"""
        return {
            'round': self.state.round_number,
            'current_player': self.get_current_player().name,
            'current_player_index': self.state.current_player_index,
            'players': [
                {
                    'name': p.name,
                    'phase': p.current_phase,
                    'hand_size': p.get_hand_size(),
                    'score': p.score,
                    'completed_phase': p.completed_phase_this_round
                }
                for p in self.players
            ],
            'discard_top': self.peek_discard_top(),
            'deck_size': self.deck.cards_remaining(),
            'game_over': self.state.game_over,
            'winner': self.state.winner.name if self.state.winner else None
        }
    
    def get_player_by_name(self, name: str) -> Optional[Player]:
        """Get a player by their name"""
        for player in self.players:
            if player.name == name:
                return player
        return None
    
    def get_available_targets_for_hitting(self, current_player: Player) -> List[Player]:
        """Get list of players that current player can hit on"""
        targets = []
        for player in self.players:
            if player != current_player and player.completed_phase_this_round:
                targets.append(player)
        return targets
    
    def is_deck_empty(self) -> bool:
        """Check if the deck is empty"""
        return self.deck.is_empty()
    
    def reshuffle_if_needed(self):
        """Reshuffle discard pile into deck if deck is empty"""
        if self.deck.is_empty() and self.discard_pile.size() > 1:
            # Keep top card of discard pile, shuffle rest back into deck
            top_card = self.discard_pile.take_top_card()
            
            # Move all remaining cards from discard to deck
            while not self.discard_pile.is_empty():
                card = self.discard_pile.take_top_card()
                if card:
                    self.deck.cards.append(card)
            
            # Shuffle the deck and put top card back on discard
            self.deck.shuffle()
            if top_card:
                self.discard_pile.add_card(top_card)