"""Game state management for saving and loading test scenarios"""
import json
import os
from typing import Dict, Any, List
from game import Phase10Game, GameState
from player import Player
from cards import Card, CardType, Color, Deck, DiscardPile

class GameStateManager:
    def __init__(self, states_dir: str = "test_states"):
        self.states_dir = states_dir
        if not os.path.exists(states_dir):
            os.makedirs(states_dir)
    
    def save_game_state(self, game: Phase10Game, name: str) -> bool:
        """Save current game state to a file"""
        try:
            state_data = self._serialize_game(game)
            file_path = os.path.join(self.states_dir, f"{name}.json")
            
            with open(file_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            print(f"[STATE] Saved game state to {file_path}")
            return True
            
        except Exception as e:
            print(f"[STATE] Error saving state: {e}")
            return False
    
    def load_game_state(self, name: str) -> Phase10Game:
        """Load game state from a file"""
        try:
            file_path = os.path.join(self.states_dir, f"{name}.json")
            
            with open(file_path, 'r') as f:
                state_data = json.load(f)
            
            game = self._deserialize_game(state_data)
            print(f"[STATE] Loaded game state from {file_path}")
            return game
            
        except Exception as e:
            print(f"[STATE] Error loading state: {e}")
            return None
    
    def list_available_states(self) -> List[str]:
        """List all available saved states"""
        if not os.path.exists(self.states_dir):
            return []
        
        states = []
        for filename in os.listdir(self.states_dir):
            if filename.endswith('.json'):
                states.append(filename[:-5])  # Remove .json extension
        
        return sorted(states)
    
    def _serialize_game(self, game: Phase10Game) -> Dict[str, Any]:
        """Convert game object to serializable dictionary"""
        return {
            'players': [self._serialize_player(p) for p in game.players],
            'deck': self._serialize_deck(game.deck),
            'discard_pile': self._serialize_discard_pile(game.discard_pile),
            'state': {
                'round_number': game.state.round_number,
                'current_player_index': game.state.current_player_index,
                'game_over': game.state.game_over,
                'winner_name': game.state.winner.name if game.state.winner else None
            }
        }
    
    def _serialize_player(self, player: Player) -> Dict[str, Any]:
        """Serialize a player object"""
        return {
            'name': player.name,
            'hand': [self._serialize_card(c) for c in player.hand],
            'current_phase': player.current_phase,
            'completed_phase_this_round': player.completed_phase_this_round,
            'completed_phase_cards': [self._serialize_card(c) for c in player.completed_phase_cards],
            'score': player.score
        }
    
    def _serialize_card(self, card: Card) -> Dict[str, Any]:
        """Serialize a card object"""
        return {
            'rank': card.rank,
            'color': card.color.value,
            'card_type': card.card_type.value
        }
    
    def _serialize_deck(self, deck: Deck) -> Dict[str, Any]:
        """Serialize deck"""
        return {
            'cards': [self._serialize_card(c) for c in deck.cards]
        }
    
    def _serialize_discard_pile(self, discard_pile: DiscardPile) -> Dict[str, Any]:
        """Serialize discard pile"""
        return {
            'cards': [self._serialize_card(c) for c in discard_pile.cards]
        }
    
    def _deserialize_game(self, data: Dict[str, Any]) -> Phase10Game:
        """Convert dictionary back to game object"""
        # Create players list
        player_names = [p['name'] for p in data['players']]
        game = Phase10Game(player_names)
        
        # Restore players
        for i, player_data in enumerate(data['players']):
            self._deserialize_player(game.players[i], player_data)
        
        # Restore deck
        game.deck = self._deserialize_deck(data['deck'])
        
        # Restore discard pile
        game.discard_pile = self._deserialize_discard_pile(data['discard_pile'])
        
        # Restore game state
        state_data = data['state']
        game.state.round_number = state_data['round_number']
        game.state.current_player_index = state_data['current_player_index']
        game.state.game_over = state_data['game_over']
        
        if state_data['winner_name']:
            for player in game.players:
                if player.name == state_data['winner_name']:
                    game.state.winner = player
                    break
        
        return game
    
    def _deserialize_player(self, player: Player, data: Dict[str, Any]):
        """Restore player from data"""
        player.hand = [self._deserialize_card(c) for c in data['hand']]
        player.current_phase = data['current_phase']
        player.completed_phase_this_round = data['completed_phase_this_round']
        player.completed_phase_cards = [self._deserialize_card(c) for c in data['completed_phase_cards']]
        player.score = data['score']
    
    def _deserialize_card(self, data: Dict[str, Any]) -> Card:
        """Recreate card from data"""
        return Card(
            rank=data['rank'],
            color=Color(data['color']),
            card_type=CardType(data['card_type'])
        )
    
    def _deserialize_deck(self, data: Dict[str, Any]) -> Deck:
        """Recreate deck from data"""
        deck = Deck()
        deck.cards = [self._deserialize_card(c) for c in data['cards']]
        return deck
    
    def _deserialize_discard_pile(self, data: Dict[str, Any]) -> DiscardPile:
        """Recreate discard pile from data"""
        pile = DiscardPile()
        pile.cards = [self._deserialize_card(c) for c in data['cards']]
        return pile

def create_preset_states():
    """Create preset test states"""
    manager = GameStateManager()
    
    # State 1: Ready for Phase 1 completion
    print("Creating preset state: ready_phase_1")
    game = Phase10Game(["Alice", "Bob"])
    alice = game.players[0]
    
    # Give Alice cards to complete Phase 1
    alice.hand = [
        Card(5, Color.RED), Card(5, Color.BLUE), Card(5, Color.GREEN),
        Card(8, Color.RED), Card(8, Color.BLUE), Card(8, Color.YELLOW),
        Card(2, Color.RED), Card(9, Color.GREEN), Card(10, Color.BLUE), Card(11, Color.YELLOW)
    ]
    
    manager.save_game_state(game, "ready_phase_1")
    
    # State 2: Complex hitting scenario
    print("Creating preset state: complex_hitting")
    game = Phase10Game(["Alice", "Bob", "Charlie"])
    alice = game.players[0]
    bob = game.players[1]
    
    # Alice completes Phase 1
    alice.completed_phase_this_round = True
    alice.completed_phase_cards = [
        Card(5, Color.RED), Card(5, Color.BLUE), Card(5, Color.GREEN),
        Card(8, Color.RED), Card(8, Color.BLUE), Card(8, Color.YELLOW)
    ]
    alice.hand = [Card(2, Color.RED), Card(9, Color.GREEN), Card(5, Color.YELLOW)]  # Can hit with 5
    
    # Bob completes Phase 1  
    bob.completed_phase_this_round = True
    bob.completed_phase_cards = [
        Card(3, Color.RED), Card(3, Color.BLUE), Card(3, Color.GREEN),
        Card(7, Color.RED), Card(7, Color.BLUE), Card(7, Color.YELLOW)
    ]
    bob.hand = [Card(4, Color.RED), Card(6, Color.GREEN)]
    
    manager.save_game_state(game, "complex_hitting")
    
    # State 3: Endgame scenario
    print("Creating preset state: endgame")
    game = Phase10Game(["Alice", "Bob"])
    alice = game.players[0]
    bob = game.players[1]
    
    # Alice is on Phase 10
    alice.current_phase = 10
    alice.score = 245
    alice.hand = [
        Card(6, Color.RED), Card(6, Color.BLUE), Card(6, Color.GREEN), Card(6, Color.YELLOW), Card(None, Color.RED, CardType.WILD),
        Card(12, Color.RED), Card(12, Color.BLUE), Card(12, Color.GREEN),
        Card(4, Color.RED), Card(9, Color.GREEN)
    ]
    
    # Bob is on Phase 9
    bob.current_phase = 9
    bob.score = 198
    
    manager.save_game_state(game, "endgame")
    
    # State 4: Edge case - mostly skip cards
    print("Creating preset state: skip_heavy")
    game = Phase10Game(["Alice", "Bob", "Charlie"])
    alice = game.players[0]
    
    # Give Alice lots of skip cards
    alice.hand = [
        Card(None, Color.RED, CardType.SKIP),
        Card(None, Color.BLUE, CardType.SKIP),
        Card(None, Color.GREEN, CardType.SKIP),
        Card(None, Color.YELLOW, CardType.SKIP),
        Card(5, Color.RED), Card(5, Color.BLUE), Card(5, Color.GREEN),
        Card(2, Color.RED), Card(9, Color.GREEN), Card(10, Color.BLUE)
    ]
    
    manager.save_game_state(game, "skip_heavy")
    
    print("Created 4 preset states!")

if __name__ == "__main__":
    create_preset_states()