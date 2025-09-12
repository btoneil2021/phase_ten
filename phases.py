from enum import Enum
from typing import List, Set, Dict, Tuple, Optional
from collections import Counter
from cards import Card, CardType, Color


class PhaseType(Enum):
    SET = "set"
    RUN = "run"
    COLOR = "color"


class PhaseRequirement:
    def __init__(self, phase_type: PhaseType, count: int, additional_info: Optional[str] = None):
        self.type = phase_type
        self.count = count
        self.additional_info = additional_info
    
    def __str__(self) -> str:
        if self.type == PhaseType.SET:
            return f"Set of {self.count}"
        elif self.type == PhaseType.RUN:
            return f"Run of {self.count}"
        elif self.type == PhaseType.COLOR:
            return f"{self.count} cards of one color"
        return f"Unknown requirement"


class Phase:
    def __init__(self, phase_number: int, requirements: List[PhaseRequirement], description: str):
        self.phase_number = phase_number
        self.requirements = requirements
        self.description = description
    
    def __str__(self) -> str:
        return f"Phase {self.phase_number}: {self.description}"


class PhaseValidator:
    @staticmethod
    def is_valid_set(cards: List[Card], required_count: int) -> bool:
        if len(cards) != required_count:
            return False
        
        if not cards:
            return False
        
        # Count wilds and non-wild cards
        wilds = [c for c in cards if c.card_type == CardType.WILD]
        non_wilds = [c for c in cards if c.card_type != CardType.WILD]
        
        if not non_wilds and wilds:
            return False  # Can't have all wilds in a set
        
        if non_wilds:
            target_rank = non_wilds[0].rank
            # Check that all non-wild cards have the same rank
            for card in non_wilds:
                if card.rank != target_rank:
                    return False
        
        return len(wilds) + len(non_wilds) == required_count
    
    @staticmethod
    def is_valid_run(cards: List[Card], required_count: int) -> bool:
        if len(cards) != required_count:
            return False
        
        if not cards:
            return False
        
        # Separate wilds and non-wilds
        wilds = [c for c in cards if c.card_type == CardType.WILD]
        non_wilds = [c for c in cards if c.card_type != CardType.WILD]
        
        if not non_wilds:
            return False  # Can't have all wilds in a run
        
        # Sort non-wild cards by rank
        non_wild_ranks = sorted([c.rank for c in non_wilds])
        
        # Check if we can form a consecutive sequence
        return PhaseValidator._can_form_run_with_wilds(non_wild_ranks, len(wilds), required_count)
    
    @staticmethod
    def _can_form_run_with_wilds(sorted_ranks: List[int], wild_count: int, target_length: int) -> bool:
        if len(sorted_ranks) + wild_count != target_length:
            return False
        
        if not sorted_ranks:
            return False
        
        # Try to place the run starting from each possible position
        for start in range(1, 13 - target_length + 1):
            needed_wilds = 0
            rank_index = 0
            
            for pos in range(start, start + target_length):
                if rank_index < len(sorted_ranks) and sorted_ranks[rank_index] == pos:
                    rank_index += 1
                else:
                    needed_wilds += 1
            
            if needed_wilds <= wild_count and rank_index == len(sorted_ranks):
                return True
        
        return False
    
    @staticmethod
    def is_valid_color_requirement(cards: List[Card], required_count: int) -> bool:
        if len(cards) != required_count:
            return False
        
        if not cards:
            return False
        
        # Count cards by color (excluding wilds)
        color_counts = Counter()
        wild_count = 0
        
        for card in cards:
            if card.card_type == CardType.WILD:
                wild_count += 1
            else:
                color_counts[card.color] += 1
        
        # Check if any single color plus wilds equals required count
        for color, count in color_counts.items():
            if count + wild_count >= required_count:
                return True
        
        # If only wilds, not valid
        return wild_count < required_count
    
    @staticmethod
    def validate_phase(cards: List[Card], phase: Phase) -> bool:
        """Validate if the given cards satisfy the phase requirements"""
        if phase.phase_number == 1:  # 2 sets of 3
            return PhaseValidator._validate_two_sets(cards, 3, 3)
        elif phase.phase_number == 2:  # 1 set of 3 + 1 run of 4
            return PhaseValidator._validate_set_and_run(cards, 3, 4)
        elif phase.phase_number == 3:  # 1 set of 4 + 1 run of 4
            return PhaseValidator._validate_set_and_run(cards, 4, 4)
        elif phase.phase_number == 4:  # 1 run of 7
            return PhaseValidator.is_valid_run(cards, 7)
        elif phase.phase_number == 5:  # 1 run of 8
            return PhaseValidator.is_valid_run(cards, 8)
        elif phase.phase_number == 6:  # 1 run of 9
            return PhaseValidator.is_valid_run(cards, 9)
        elif phase.phase_number == 7:  # 2 sets of 4
            return PhaseValidator._validate_two_sets(cards, 4, 4)
        elif phase.phase_number == 8:  # 7 cards of one color
            return PhaseValidator.is_valid_color_requirement(cards, 7)
        elif phase.phase_number == 9:  # 1 set of 5 + 1 set of 2
            return PhaseValidator._validate_two_sets(cards, 5, 2)
        elif phase.phase_number == 10:  # 1 set of 5 + 1 set of 3
            return PhaseValidator._validate_two_sets(cards, 5, 3)
        
        return False
    
    @staticmethod
    def _validate_two_sets(cards: List[Card], set1_size: int, set2_size: int) -> bool:
        total_required = set1_size + set2_size
        if len(cards) != total_required:
            return False
        
        # Try all possible combinations to split cards into two sets
        from itertools import combinations
        
        for set1_cards in combinations(cards, set1_size):
            set1_list = list(set1_cards)
            set2_list = [c for c in cards if c not in set1_list]
            
            if (PhaseValidator.is_valid_set(set1_list, set1_size) and 
                PhaseValidator.is_valid_set(set2_list, set2_size)):
                return True
        
        return False
    
    @staticmethod
    def _validate_set_and_run(cards: List[Card], set_size: int, run_size: int) -> bool:
        total_required = set_size + run_size
        if len(cards) != total_required:
            return False
        
        # Try all possible combinations to split cards into set and run
        from itertools import combinations
        
        for set_cards in combinations(cards, set_size):
            set_list = list(set_cards)
            run_list = [c for c in cards if c not in set_list]
            
            if (PhaseValidator.is_valid_set(set_list, set_size) and 
                PhaseValidator.is_valid_run(run_list, run_size)):
                return True
        
        return False


# Define all 10 phases
PHASES = {
    1: Phase(1, [PhaseRequirement(PhaseType.SET, 3), PhaseRequirement(PhaseType.SET, 3)], "2 sets of 3"),
    2: Phase(2, [PhaseRequirement(PhaseType.SET, 3), PhaseRequirement(PhaseType.RUN, 4)], "1 set of 3 + 1 run of 4"),
    3: Phase(3, [PhaseRequirement(PhaseType.SET, 4), PhaseRequirement(PhaseType.RUN, 4)], "1 set of 4 + 1 run of 4"),
    4: Phase(4, [PhaseRequirement(PhaseType.RUN, 7)], "1 run of 7"),
    5: Phase(5, [PhaseRequirement(PhaseType.RUN, 8)], "1 run of 8"),
    6: Phase(6, [PhaseRequirement(PhaseType.RUN, 9)], "1 run of 9"),
    7: Phase(7, [PhaseRequirement(PhaseType.SET, 4), PhaseRequirement(PhaseType.SET, 4)], "2 sets of 4"),
    8: Phase(8, [PhaseRequirement(PhaseType.COLOR, 7)], "7 cards of one color"),
    9: Phase(9, [PhaseRequirement(PhaseType.SET, 5), PhaseRequirement(PhaseType.SET, 2)], "1 set of 5 + 1 set of 2"),
    10: Phase(10, [PhaseRequirement(PhaseType.SET, 5), PhaseRequirement(PhaseType.SET, 3)], "1 set of 5 + 1 set of 3")
}