from typing import List, Optional, Tuple
from cards import Card, CardType, Color
from phases import Phase, PHASES, PhaseValidator


class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []
        self.current_phase = 1
        self.completed_phase_this_round = False
        self.completed_phase_cards: List[Card] = []
        self.score = 0
    
    def add_card_to_hand(self, card: Card):
        """Add a card to the player's hand"""
        self.hand.append(card)
    
    def remove_card_from_hand(self, card: Card) -> bool:
        """Remove a card from the player's hand. Returns True if successful."""
        if card in self.hand:
            self.hand.remove(card)
            return True
        return False
    
    def get_hand_size(self) -> int:
        """Get the number of cards in the player's hand"""
        return len(self.hand)
    
    def get_hand_points(self) -> int:
        """Calculate total points value of cards in hand"""
        return sum(card.get_points() for card in self.hand)
    
    def has_completed_phase(self) -> bool:
        """Check if player has completed their current phase this round"""
        return self.completed_phase_this_round
    
    def get_current_phase(self) -> Phase:
        """Get the current phase the player needs to complete"""
        return PHASES[self.current_phase]
    
    def can_complete_phase(self, selected_cards: List[Card]) -> bool:
        """Check if the selected cards can complete the current phase"""
        if self.completed_phase_this_round:
            return False
        
        current_phase = self.get_current_phase()
        return PhaseValidator.validate_phase(selected_cards, current_phase)
    
    def complete_phase(self, selected_cards: List[Card]) -> bool:
        """Attempt to complete the current phase with selected cards"""
        if not self.can_complete_phase(selected_cards):
            return False
        
        # Remove the cards from hand and mark phase as completed
        for card in selected_cards:
            if not self.remove_card_from_hand(card):
                # If we can't remove a card, something went wrong
                # Add back any cards we already removed
                for added_back_card in selected_cards:
                    if added_back_card == card:
                        break
                    self.add_card_to_hand(added_back_card)
                return False
        
        self.completed_phase_cards = selected_cards[:]
        self.completed_phase_this_round = True
        return True
    
    def can_hit_on_phase(self, card: Card, target_player: 'Player') -> bool:
        """Check if a card can be played on another player's completed phase"""
        if not self.completed_phase_this_round or not target_player.completed_phase_this_round:
            return False
        
        return self._can_add_to_phase_cards(card, target_player.completed_phase_cards, target_player.get_current_phase())
    
    def can_hit_on_own_phase(self, card: Card) -> bool:
        """Check if a card can be played on own completed phase"""
        if not self.completed_phase_this_round:
            return False
        
        return self._can_add_to_phase_cards(card, self.completed_phase_cards, self.get_current_phase())
    
    def _can_add_to_phase_cards(self, card: Card, phase_cards: List[Card], phase: Phase) -> bool:
        """Helper method to check if a card can be added to existing phase cards"""
        if card.card_type == CardType.SKIP:
            return False
        
        # Try adding the card to the existing phase and see if it's still valid
        test_cards = phase_cards + [card]
        
        # For phases that require specific structures, we need more sophisticated checking
        if phase.phase_number in [1, 7, 9, 10]:  # Two sets
            return self._can_add_to_sets(card, phase_cards, phase)
        elif phase.phase_number in [2, 3]:  # Set + Run
            return self._can_add_to_set_and_run(card, phase_cards, phase)
        elif phase.phase_number in [4, 5, 6]:  # Single run
            return self._can_add_to_run(card, phase_cards)
        elif phase.phase_number == 8:  # Color requirement
            return self._can_add_to_color_group(card, phase_cards)
        
        return False
    
    def _can_add_to_sets(self, card: Card, phase_cards: List[Card], phase: Phase) -> bool:
        """Check if card can be added to one of the sets in a two-set phase"""
        # This is a simplified check - in a full implementation, you'd need to 
        # track which cards belong to which set
        if card.card_type == CardType.WILD:
            return True
        
        # Check if the card matches any rank already in the phase
        existing_ranks = set()
        for existing_card in phase_cards:
            if existing_card.card_type == CardType.NUMBER:
                existing_ranks.add(existing_card.rank)
        
        return card.rank in existing_ranks
    
    def _can_add_to_set_and_run(self, card: Card, phase_cards: List[Card], phase: Phase) -> bool:
        """Check if card can be added to either the set or run in a set+run phase"""
        # Simplified implementation - would need better structure tracking
        return card.card_type == CardType.WILD or card.card_type == CardType.NUMBER
    
    def _can_add_to_run(self, card: Card, phase_cards: List[Card]) -> bool:
        """Check if card can extend an existing run"""
        if card.card_type == CardType.WILD:
            return True
        
        if card.card_type != CardType.NUMBER:
            return False
        
        # Get the range of the existing run
        existing_numbers = []
        for existing_card in phase_cards:
            if existing_card.card_type == CardType.NUMBER:
                existing_numbers.append(existing_card.rank)
        
        if not existing_numbers:
            return True
        
        min_rank = min(existing_numbers)
        max_rank = max(existing_numbers)
        
        # Card can be added if it's adjacent to the existing run
        return card.rank == min_rank - 1 or card.rank == max_rank + 1
    
    def _can_add_to_color_group(self, card: Card, phase_cards: List[Card]) -> bool:
        """Check if card can be added to a color group"""
        if card.card_type == CardType.WILD:
            return True
        
        if card.card_type != CardType.NUMBER:
            return False
        
        # Find the dominant color in the existing cards
        color_counts = {}
        for existing_card in phase_cards:
            if existing_card.card_type == CardType.NUMBER:
                color = existing_card.color
                color_counts[color] = color_counts.get(color, 0) + 1
        
        if not color_counts:
            return True
        
        dominant_color = max(color_counts, key=color_counts.get)
        return card.color == dominant_color
    
    def hit_on_phase(self, card: Card, target_player: 'Player') -> bool:
        """Play a card on another player's completed phase"""
        if not self.can_hit_on_phase(card, target_player):
            return False
        
        if self.remove_card_from_hand(card):
            target_player.completed_phase_cards.append(card)
            return True
        return False
    
    def hit_on_own_phase(self, card: Card) -> bool:
        """Play a card on own completed phase"""
        if not self.can_hit_on_own_phase(card):
            return False
        
        if self.remove_card_from_hand(card):
            self.completed_phase_cards.append(card)
            return True
        return False
    
    def advance_to_next_phase(self):
        """Advance to the next phase (called at end of round if phase was completed)"""
        if self.completed_phase_this_round and self.current_phase < 10:
            self.current_phase += 1
    
    def reset_for_new_round(self):
        """Reset player state for a new round"""
        self.hand = []
        self.completed_phase_this_round = False
        self.completed_phase_cards = []
    
    def is_finished_with_all_phases(self) -> bool:
        """Check if player has completed all 10 phases"""
        return self.current_phase > 10
    
    def get_sorted_hand(self) -> List[Card]:
        """Get hand sorted optimally for the current phase"""
        if not self.hand:
            return []
        
        phase = self.get_current_phase()
        
        if phase.phase_number in [1, 7, 9, 10]:  # Phases with sets
            return self._sort_for_sets()
        elif phase.phase_number in [2, 3]:  # Set + Run phases
            return self._sort_for_set_and_run()
        elif phase.phase_number in [4, 5, 6]:  # Run phases
            return self._sort_for_runs()
        elif phase.phase_number == 8:  # Color phase
            return self._sort_for_color()
        else:
            return self._sort_basic()
    
    def _sort_for_sets(self) -> List[Card]:
        """Sort cards optimally for set-based phases"""
        numbered_cards = []
        wild_cards = []
        skip_cards = []
        
        for card in self.hand:
            if card.card_type == CardType.WILD:
                wild_cards.append(card)
            elif card.card_type == CardType.SKIP:
                skip_cards.append(card)
            else:
                numbered_cards.append(card)
        
        # Group numbered cards by rank
        from collections import defaultdict
        rank_groups = defaultdict(list)
        for card in numbered_cards:
            rank_groups[card.rank].append(card)
        
        # Sort by rank frequency (most common ranks first), then by rank
        sorted_ranks = sorted(rank_groups.keys(), key=lambda r: (-len(rank_groups[r]), r))
        
        result = []
        for rank in sorted_ranks:
            result.extend(sorted(rank_groups[rank], key=lambda c: c.color.value))
        
        # Add wilds and skips at the end
        result.extend(sorted(wild_cards, key=lambda c: c.color.value))
        result.extend(sorted(skip_cards, key=lambda c: c.color.value))
        
        return result
    
    def _sort_for_runs(self) -> List[Card]:
        """Sort cards optimally for run phases"""
        numbered_cards = []
        wild_cards = []
        skip_cards = []
        
        for card in self.hand:
            if card.card_type == CardType.WILD:
                wild_cards.append(card)
            elif card.card_type == CardType.SKIP:
                skip_cards.append(card)
            else:
                numbered_cards.append(card)
        
        # Sort numbered cards by rank
        numbered_cards.sort(key=lambda c: (c.rank, c.color.value))
        
        result = numbered_cards[:]
        result.extend(sorted(wild_cards, key=lambda c: c.color.value))
        result.extend(sorted(skip_cards, key=lambda c: c.color.value))
        
        return result
    
    def _sort_for_set_and_run(self) -> List[Card]:
        """Sort cards for phases that need both sets and runs"""
        # Use set sorting as it groups similar cards together
        return self._sort_for_sets()
    
    def _sort_for_color(self) -> List[Card]:
        """Sort cards optimally for color phase"""
        numbered_cards = []
        wild_cards = []
        skip_cards = []
        
        for card in self.hand:
            if card.card_type == CardType.WILD:
                wild_cards.append(card)
            elif card.card_type == CardType.SKIP:
                skip_cards.append(card)
            else:
                numbered_cards.append(card)
        
        # Group by color, then sort by rank within each color
        from collections import defaultdict
        color_groups = defaultdict(list)
        for card in numbered_cards:
            color_groups[card.color].append(card)
        
        # Sort colors by count (most common first)
        sorted_colors = sorted(color_groups.keys(), key=lambda c: (-len(color_groups[c]), c.value))
        
        result = []
        for color in sorted_colors:
            color_cards = sorted(color_groups[color], key=lambda c: c.rank)
            result.extend(color_cards)
        
        # Add wilds and skips at the end
        result.extend(sorted(wild_cards, key=lambda c: c.color.value))
        result.extend(sorted(skip_cards, key=lambda c: c.color.value))
        
        return result
    
    def _sort_basic(self) -> List[Card]:
        """Basic sorting by rank, then color"""
        numbered_cards = []
        wild_cards = []
        skip_cards = []
        
        for card in self.hand:
            if card.card_type == CardType.WILD:
                wild_cards.append(card)
            elif card.card_type == CardType.SKIP:
                skip_cards.append(card)
            else:
                numbered_cards.append(card)
        
        numbered_cards.sort(key=lambda c: (c.rank, c.color.value))
        
        result = numbered_cards[:]
        result.extend(sorted(wild_cards, key=lambda c: c.color.value))
        result.extend(sorted(skip_cards, key=lambda c: c.color.value))
        
        return result
    
    def __str__(self) -> str:
        return f"{self.name} (Phase {self.current_phase}, {len(self.hand)} cards, {self.score} points)"