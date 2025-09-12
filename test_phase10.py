import unittest
from unittest.mock import patch
from cards import Card, Deck, DiscardPile, CardType, Color
from player import Player
from phases import Phase, PhaseValidator, PHASES
from game import Phase10Game


class TestCard(unittest.TestCase):
    def test_card_creation(self):
        card = Card(5, Color.RED)
        self.assertEqual(card.rank, 5)
        self.assertEqual(card.color, Color.RED)
        self.assertEqual(card.card_type, CardType.NUMBER)
    
    def test_wild_card_creation(self):
        wild = Card(None, Color.BLUE, CardType.WILD)
        self.assertEqual(wild.card_type, CardType.WILD)
        self.assertEqual(str(wild), "Wild")
    
    def test_skip_card_creation(self):
        skip = Card(None, Color.GREEN, CardType.SKIP)
        self.assertEqual(skip.card_type, CardType.SKIP)
        self.assertEqual(str(skip), "Skip")
    
    def test_card_points(self):
        # Test number cards 1-9
        card = Card(5, Color.RED)
        self.assertEqual(card.get_points(), 5)
        
        # Test number cards 10-12
        card = Card(10, Color.BLUE)
        self.assertEqual(card.get_points(), 10)
        
        # Test wild card
        wild = Card(None, Color.GREEN, CardType.WILD)
        self.assertEqual(wild.get_points(), 25)
        
        # Test skip card
        skip = Card(None, Color.YELLOW, CardType.SKIP)
        self.assertEqual(skip.get_points(), 15)
    
    def test_can_substitute(self):
        # Regular card
        card = Card(7, Color.RED)
        self.assertTrue(card.can_substitute(7))
        self.assertFalse(card.can_substitute(8))
        
        # Wild card
        wild = Card(None, Color.BLUE, CardType.WILD)
        self.assertTrue(wild.can_substitute(5))
        self.assertTrue(wild.can_substitute(12))


class TestDeck(unittest.TestCase):
    def test_deck_creation(self):
        deck = Deck()
        self.assertEqual(len(deck.cards), 108)  # Total Phase 10 cards
    
    def test_deck_composition(self):
        deck = Deck()
        
        # Count different card types
        number_cards = sum(1 for card in deck.cards if card.card_type == CardType.NUMBER)
        wild_cards = sum(1 for card in deck.cards if card.card_type == CardType.WILD)
        skip_cards = sum(1 for card in deck.cards if card.card_type == CardType.SKIP)
        
        self.assertEqual(number_cards, 96)  # 24 * 4 colors
        self.assertEqual(wild_cards, 8)     # 2 * 4 colors
        self.assertEqual(skip_cards, 4)     # 1 * 4 colors
    
    def test_draw_card(self):
        deck = Deck()
        initial_size = deck.cards_remaining()
        
        card = deck.draw_card()
        self.assertIsNotNone(card)
        self.assertEqual(deck.cards_remaining(), initial_size - 1)
    
    def test_empty_deck(self):
        deck = Deck()
        
        # Draw all cards
        while not deck.is_empty():
            deck.draw_card()
        
        self.assertTrue(deck.is_empty())
        self.assertIsNone(deck.draw_card())


class TestDiscardPile(unittest.TestCase):
    def test_discard_pile_creation(self):
        pile = DiscardPile()
        self.assertTrue(pile.is_empty())
        self.assertEqual(pile.size(), 0)
    
    def test_add_and_take_card(self):
        pile = DiscardPile()
        card = Card(5, Color.RED)
        
        pile.add_card(card)
        self.assertFalse(pile.is_empty())
        self.assertEqual(pile.size(), 1)
        
        taken_card = pile.take_top_card()
        self.assertEqual(taken_card, card)
        self.assertTrue(pile.is_empty())
    
    def test_peek_top_card(self):
        pile = DiscardPile()
        card = Card(7, Color.BLUE)
        
        pile.add_card(card)
        peeked_card = pile.peek_top_card()
        
        self.assertEqual(peeked_card, card)
        self.assertEqual(pile.size(), 1)  # Card should still be there


class TestPhaseValidator(unittest.TestCase):
    def test_valid_set(self):
        # Valid set of 3 fives
        cards = [Card(5, Color.RED), Card(5, Color.BLUE), Card(5, Color.GREEN)]
        self.assertTrue(PhaseValidator.is_valid_set(cards, 3))
        
        # Valid set with wild card
        cards = [Card(5, Color.RED), Card(5, Color.BLUE), Card(None, Color.GREEN, CardType.WILD)]
        self.assertTrue(PhaseValidator.is_valid_set(cards, 3))
    
    def test_invalid_set(self):
        # Different ranks
        cards = [Card(5, Color.RED), Card(6, Color.BLUE), Card(5, Color.GREEN)]
        self.assertFalse(PhaseValidator.is_valid_set(cards, 3))
        
        # All wilds (not allowed)
        cards = [Card(None, Color.RED, CardType.WILD), Card(None, Color.BLUE, CardType.WILD), Card(None, Color.GREEN, CardType.WILD)]
        self.assertFalse(PhaseValidator.is_valid_set(cards, 3))
    
    def test_valid_run(self):
        # Valid run 5, 6, 7, 8
        cards = [Card(5, Color.RED), Card(6, Color.BLUE), Card(7, Color.GREEN), Card(8, Color.YELLOW)]
        self.assertTrue(PhaseValidator.is_valid_run(cards, 4))
        
        # Valid run with wild card
        cards = [Card(5, Color.RED), Card(None, Color.BLUE, CardType.WILD), Card(7, Color.GREEN), Card(8, Color.YELLOW)]
        self.assertTrue(PhaseValidator.is_valid_run(cards, 4))
    
    def test_invalid_run(self):
        # Non-consecutive
        cards = [Card(5, Color.RED), Card(6, Color.BLUE), Card(8, Color.GREEN), Card(9, Color.YELLOW)]
        self.assertFalse(PhaseValidator.is_valid_run(cards, 4))
        
        # All wilds (not allowed)
        cards = [Card(None, Color.RED, CardType.WILD)] * 4
        self.assertFalse(PhaseValidator.is_valid_run(cards, 4))
    
    def test_valid_color_requirement(self):
        # All red cards
        cards = [Card(1, Color.RED), Card(5, Color.RED), Card(9, Color.RED), Card(12, Color.RED)]
        self.assertTrue(PhaseValidator.is_valid_color_requirement(cards, 4))
        
        # Red cards with wild
        cards = [Card(1, Color.RED), Card(5, Color.RED), Card(9, Color.RED), Card(None, Color.BLUE, CardType.WILD)]
        self.assertTrue(PhaseValidator.is_valid_color_requirement(cards, 4))
    
    def test_phase_validation(self):
        # Phase 1: 2 sets of 3
        cards = [
            Card(5, Color.RED), Card(5, Color.BLUE), Card(5, Color.GREEN),  # Set of 5s
            Card(8, Color.RED), Card(8, Color.YELLOW), Card(8, Color.BLUE)  # Set of 8s
        ]
        phase1 = PHASES[1]
        self.assertTrue(PhaseValidator.validate_phase(cards, phase1))
        
        # Phase 4: 1 run of 7
        cards = [Card(i, Color.RED) for i in range(3, 10)]  # 3, 4, 5, 6, 7, 8, 9
        phase4 = PHASES[4]
        self.assertTrue(PhaseValidator.validate_phase(cards, phase4))


class TestPlayer(unittest.TestCase):
    def test_player_creation(self):
        player = Player("Alice")
        self.assertEqual(player.name, "Alice")
        self.assertEqual(player.current_phase, 1)
        self.assertEqual(player.get_hand_size(), 0)
        self.assertFalse(player.completed_phase_this_round)
    
    def test_hand_management(self):
        player = Player("Bob")
        card = Card(7, Color.RED)
        
        player.add_card_to_hand(card)
        self.assertEqual(player.get_hand_size(), 1)
        self.assertIn(card, player.hand)
        
        self.assertTrue(player.remove_card_from_hand(card))
        self.assertEqual(player.get_hand_size(), 0)
    
    def test_phase_completion(self):
        player = Player("Charlie")
        
        # Give player cards for Phase 1 (2 sets of 3)
        cards = [
            Card(5, Color.RED), Card(5, Color.BLUE), Card(5, Color.GREEN),
            Card(8, Color.RED), Card(8, Color.YELLOW), Card(8, Color.BLUE)
        ]
        
        for card in cards:
            player.add_card_to_hand(card)
        
        # Should be able to complete phase
        self.assertTrue(player.can_complete_phase(cards))
        self.assertTrue(player.complete_phase(cards))
        self.assertTrue(player.completed_phase_this_round)
        self.assertEqual(player.get_hand_size(), 0)
    
    def test_phase_advancement(self):
        player = Player("Dave")
        self.assertEqual(player.current_phase, 1)
        
        # Complete phase and advance
        cards = [Card(5, Color.RED)] * 6  # Simplified for test
        player.completed_phase_this_round = True
        player.advance_to_next_phase()
        
        self.assertEqual(player.current_phase, 2)
    
    def test_score_calculation(self):
        player = Player("Eve")
        
        # Add various cards to hand
        player.add_card_to_hand(Card(5, Color.RED))      # 5 points
        player.add_card_to_hand(Card(10, Color.BLUE))    # 10 points
        player.add_card_to_hand(Card(None, Color.GREEN, CardType.WILD))  # 25 points
        player.add_card_to_hand(Card(None, Color.YELLOW, CardType.SKIP)) # 15 points
        
        self.assertEqual(player.get_hand_points(), 55)
    
    def test_hand_sorting_for_sets(self):
        """Test hand sorting for set-based phases"""
        player = Player("Alice")
        
        # Add cards that would be good for Phase 1 (2 sets of 3)
        cards = [
            Card(5, Color.RED), Card(7, Color.BLUE), Card(5, Color.GREEN),
            Card(7, Color.YELLOW), Card(5, Color.BLUE), Card(None, Color.RED, CardType.WILD),
            Card(3, Color.GREEN), Card(None, Color.BLUE, CardType.SKIP)
        ]
        
        for card in cards:
            player.add_card_to_hand(card)
        
        sorted_hand = player.get_sorted_hand()
        
        # Should group cards by rank with most frequent first
        # Expected order: 5s (3 cards), 7s (2 cards), 3s (1 card), wild, skip
        ranks = []
        for card in sorted_hand:
            if card.card_type == CardType.NUMBER:
                ranks.append(card.rank)
            elif card.card_type == CardType.WILD:
                ranks.append('W')
            elif card.card_type == CardType.SKIP:
                ranks.append('S')
        
        # 5s should come first (most frequent), then 7s, then 3, then wild, then skip
        self.assertEqual(ranks[:3], [5, 5, 5])
        self.assertEqual(ranks[3:5], [7, 7])
        self.assertEqual(ranks[5], 3)
        self.assertEqual(ranks[6], 'W')
        self.assertEqual(ranks[7], 'S')
    
    def test_hand_sorting_for_runs(self):
        """Test hand sorting for run-based phases"""
        player = Player("Alice")
        player.current_phase = 4  # Phase 4: run of 7
        
        # Add cards that could form a run
        cards = [
            Card(8, Color.RED), Card(5, Color.BLUE), Card(7, Color.GREEN),
            Card(6, Color.YELLOW), Card(10, Color.BLUE), Card(None, Color.RED, CardType.WILD),
            Card(9, Color.GREEN), Card(None, Color.BLUE, CardType.SKIP)
        ]
        
        for card in cards:
            player.add_card_to_hand(card)
        
        sorted_hand = player.get_sorted_hand()
        
        # Should sort numbered cards by rank, with wilds and skips at end
        numbered_ranks = []
        special_cards = []
        
        for card in sorted_hand:
            if card.card_type == CardType.NUMBER:
                numbered_ranks.append(card.rank)
            else:
                special_cards.append(card.card_type)
        
        # Numbered cards should be in ascending order
        self.assertEqual(numbered_ranks, [5, 6, 7, 8, 9, 10])
        # Wild and skip should be at the end
        self.assertEqual(special_cards, [CardType.WILD, CardType.SKIP])
    
    def test_hand_sorting_for_color(self):
        """Test hand sorting for color phase"""
        player = Player("Alice")
        player.current_phase = 8  # Phase 8: 7 cards of one color
        
        # Add cards with different colors
        cards = [
            Card(5, Color.RED), Card(7, Color.BLUE), Card(8, Color.RED),
            Card(3, Color.BLUE), Card(9, Color.RED), Card(None, Color.GREEN, CardType.WILD),
            Card(2, Color.BLUE), Card(None, Color.YELLOW, CardType.SKIP)
        ]
        
        for card in cards:
            player.add_card_to_hand(card)
        
        sorted_hand = player.get_sorted_hand()
        
        # Should group by color with most common first
        # RED: 3 cards, BLUE: 3 cards, so RED should come first (by color value if tied)
        colors = []
        for card in sorted_hand:
            if card.card_type == CardType.NUMBER:
                colors.append(card.color)
            else:
                colors.append(f"{card.card_type.value}")
        
        # First 3 should be RED or BLUE (grouped together)
        first_color = colors[0]
        if first_color == Color.RED:
            self.assertEqual(colors[:3], [Color.RED, Color.RED, Color.RED])
            self.assertEqual(colors[3:6], [Color.BLUE, Color.BLUE, Color.BLUE])
        else:
            self.assertEqual(colors[:3], [Color.BLUE, Color.BLUE, Color.BLUE])
            self.assertEqual(colors[3:6], [Color.RED, Color.RED, Color.RED])
        
        # Wild and skip at the end
        self.assertEqual(colors[-2:], ['wild', 'skip'])


class TestPhase10Game(unittest.TestCase):
    def test_game_creation(self):
        game = Phase10Game(["Alice", "Bob"])
        self.assertEqual(len(game.players), 2)
        self.assertEqual(game.players[0].name, "Alice")
        self.assertEqual(game.players[1].name, "Bob")
        
        # Each player should have 10 cards
        for player in game.players:
            self.assertEqual(player.get_hand_size(), 10)
    
    def test_invalid_player_count(self):
        with self.assertRaises(ValueError):
            Phase10Game(["Alice"])  # Too few players
        
        with self.assertRaises(ValueError):
            Phase10Game([f"Player{i}" for i in range(8)])  # Too many players
    
    def test_turn_management(self):
        game = Phase10Game(["Alice", "Bob", "Charlie"])
        
        self.assertEqual(game.get_current_player().name, "Alice")
        
        game.advance_turn()
        self.assertEqual(game.get_current_player().name, "Bob")
        
        game.advance_turn()
        self.assertEqual(game.get_current_player().name, "Charlie")
        
        game.advance_turn()
        self.assertEqual(game.get_current_player().name, "Alice")
    
    def test_skip_handling(self):
        game = Phase10Game(["Alice", "Bob", "Charlie"])
        
        # Test skip in 3-player game
        skip_card = Card(None, Color.RED, CardType.SKIP)
        skip_count = game.handle_skip_card(skip_card)
        self.assertEqual(skip_count, 2)  # Skip next player
        
        # Test skip in 2-player game
        game2 = Phase10Game(["Alice", "Bob"])
        skip_count = game2.handle_skip_card(skip_card)
        self.assertEqual(skip_count, 0)  # Take another turn
    
    def test_round_end_detection(self):
        game = Phase10Game(["Alice", "Bob"])
        
        # Initially, round should not be ended
        self.assertFalse(game.check_round_end())
        
        # Remove all cards from Alice's hand
        game.players[0].hand = []
        self.assertTrue(game.check_round_end())
    
    def test_game_status(self):
        game = Phase10Game(["Alice", "Bob"])
        status = game.get_game_status()
        
        self.assertEqual(status['round'], 1)
        self.assertEqual(status['current_player'], "Alice")
        self.assertEqual(len(status['players']), 2)
        self.assertFalse(status['game_over'])
    
    def test_deck_reshuffling(self):
        game = Phase10Game(["Alice", "Bob"])
        
        # Manually empty the deck
        game.deck.cards = []
        
        # Add cards to discard pile
        for i in range(5):
            game.discard_pile.add_card(Card(i + 1, Color.RED))
        
        # Reshuffle should work
        game.reshuffle_if_needed()
        
        # Deck should have cards now (minus top discard)
        self.assertGreater(game.deck.cards_remaining(), 0)
        self.assertEqual(game.discard_pile.size(), 1)


class TestIntegration(unittest.TestCase):
    def test_complete_round_simulation(self):
        """Test a simplified complete round"""
        game = Phase10Game(["Alice", "Bob"])
        
        # Give Alice cards to complete Phase 1
        alice = game.players[0]
        alice.hand = [
            Card(5, Color.RED), Card(5, Color.BLUE), Card(5, Color.GREEN),
            Card(8, Color.RED), Card(8, Color.YELLOW), Card(8, Color.BLUE),
            Card(3, Color.RED)  # Extra card to discard
        ]
        
        # Alice completes her phase
        phase_cards = alice.hand[:6]
        self.assertTrue(alice.complete_phase(phase_cards))
        
        # Alice discards her last card (goes out)
        last_card = alice.hand[0]
        self.assertTrue(game.discard_card(alice, last_card))
        
        # Round should end
        self.assertTrue(game.check_round_end())
        
        # End round and check scoring
        winner = game.end_round()
        self.assertEqual(winner, alice)
        self.assertGreater(alice.score, 0)  # Should have points from Bob's hand
    
    def test_phase_progression(self):
        """Test that players advance through phases correctly"""
        game = Phase10Game(["Alice", "Bob"])
        alice = game.players[0]
        
        # Start at phase 1
        self.assertEqual(alice.current_phase, 1)
        
        # Complete phase 1
        alice.completed_phase_this_round = True
        alice.advance_to_next_phase()
        self.assertEqual(alice.current_phase, 2)
        
        # Reset for new round
        alice.reset_for_new_round()
        self.assertFalse(alice.completed_phase_this_round)
        self.assertEqual(alice.current_phase, 2)  # Should stay at phase 2


if __name__ == '__main__':
    unittest.main()