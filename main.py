from typing import List, Optional
import os
from game import Phase10Game
from player import Player
from cards import Card, CardType
from phases import PHASES, Phase


class Phase10CLI:
    def __init__(self):
        self.game: Optional[Phase10Game] = None
    
    def start_game(self):
        """Start a new Phase 10 game"""
        print("Welcome to Phase 10!")
        print("=" * 50)
        
        # Get number of players
        while True:
            try:
                num_players = int(input("Enter number of players (2-6): "))
                if 2 <= num_players <= 6:
                    break
                else:
                    print("Please enter a number between 2 and 6.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Get player names
        player_names = []
        for i in range(num_players):
            while True:
                name = input(f"Enter name for player {i + 1}: ").strip()
                if not name:
                    name = f"Player {i + 1}"
                
                # Check for duplicate names
                if name in player_names:
                    print(f"Name '{name}' is already taken. Please choose a different name.")
                else:
                    player_names.append(name)
                    break
        
        # Create game
        self.game = Phase10Game(player_names)
        print(f"\nGame started with players: {', '.join(player_names)}")
        print("=" * 50)
        
        # Main game loop
        self.play_game()
    
    def play_game(self):
        """Main game loop"""
        while not self.game.state.game_over:
            self.play_round()
            
            if not self.game.check_game_end():
                input("\nPress Enter to start next round...")
                self.game.start_new_round()
        
        self.show_game_results()
    
    def play_round(self):
        """Play a single round"""
        self.clear_console()
        print(f"--- Round {self.game.state.round_number} ---")
        
        while not self.game.check_round_end():
            current_player = self.game.get_current_player()
            self.play_turn(current_player)
        
        # Round ended
        winner = self.game.end_round()
        print(f"\n{winner.name} won the round!")
        self.show_round_scores()
    
    def clear_console(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def play_turn(self, player: Player):
        """Play a single player's turn"""
        self.clear_console()
        print("="*60)
        print(f"                    {player.name}'s TURN")
        print("="*60)
        
        self.show_player_status(player)
        self.show_game_state()
        
        # Show current hand before drawing
        print("\n" + "-"*40)
        print("YOUR CURRENT HAND (before drawing):")
        print("-"*40)
        self.show_player_hand(player)
        
        # Phase 1: Draw a card
        print("\n" + "-"*40)
        print("PHASE 1: DRAW A CARD")
        print("-"*40)
        drawn_card = self.handle_draw_phase(player)
        if drawn_card:
            print(f"\n>>> You drew: {drawn_card}")
        
        # Show updated hand
        print("\n" + "-"*40)
        print("YOUR UPDATED HAND (after drawing):")
        print("-"*40)
        self.show_player_hand(player)
        
        # Phase 2: Complete phase if possible and not already completed
        if not player.completed_phase_this_round:
            print("\n" + "-"*40)
            print("PHASE 2: COMPLETE YOUR PHASE (Optional)")
            print("-"*40)
            self.handle_phase_completion(player)
        
        # Phase 3: Hit on phases (if phase completed)
        if player.completed_phase_this_round:
            print("\n" + "-"*40)
            print("PHASE 3: HIT ON PHASES (Optional)")
            print("-"*40)
            self.handle_hitting_phase(player)
        
        # Phase 4: Discard a card
        print("\n" + "-"*40)
        print("PHASE 4: DISCARD A CARD (Required)")
        print("-"*40)
        skip_count = self.handle_discard_phase(player)
        
        # Advance turn
        self.game.advance_turn(skip_count)
    
    def handle_draw_phase(self, player: Player) -> Optional[Card]:
        """Handle the draw phase of a turn"""
        print("\nChoose where to draw from:")
        print("  [1] Draw from deck")
        
        top_discard = self.game.peek_discard_top()
        # Skip cards cannot be picked up from discard pile
        can_take_discard = top_discard and top_discard.card_type != CardType.SKIP
        
        if can_take_discard:
            print(f"  [2] Take from discard pile: {top_discard}")
        elif top_discard and top_discard.card_type == CardType.SKIP:
            print(f"  [2] Discard pile: Skip card (CANNOT BE TAKEN)")
        
        while True:
            choice = input("\nYour choice (1 or 2): ").strip()
            if choice == "1":
                return self.game.player_draw_card(player, from_discard=False)
            elif choice == "2" and can_take_discard:
                return self.game.player_draw_card(player, from_discard=True)
            else:
                if choice == "2" and not can_take_discard:
                    print("[ERROR] Cannot take Skip card from discard pile. Please draw from deck.")
                else:
                    print("[ERROR] Invalid choice. Please enter 1 or 2.")
    
    def handle_phase_completion(self, player: Player):
        """Handle phase completion attempt"""
        current_phase = player.get_current_phase()
        print(f"\nCurrent phase: {current_phase}")
        
        while True:
            complete = input("Do you want to attempt to complete your phase? (y/n): ").strip().lower()
            if complete in ['y', 'yes']:
                break
            elif complete in ['n', 'no']:
                return
            else:
                print("Please enter y or n.")
        
        # Get cards for phase completion
        selected_cards = self.select_cards_for_phase(player)
        if selected_cards and self.game.player_complete_phase(player, selected_cards):
            print(f"Phase {current_phase.phase_number} completed!")
            self.show_completed_phase(player)
        else:
            print("Unable to complete phase with selected cards.")
    
    def select_cards_for_phase(self, player: Player) -> List[Card]:
        """Allow player to select cards for phase completion"""
        print("\nSelect cards for phase completion:")
        print("Enter card numbers separated by spaces (e.g., 1 3 5)")
        
        # Get the sorted hand to match what was displayed
        sorted_hand = player.get_sorted_hand()
        
        while True:
            try:
                indices = input("Card numbers: ").strip().split()
                if not indices:
                    return []
                
                card_indices = [int(i) - 1 for i in indices]
                selected_cards = []
                
                for idx in card_indices:
                    if 0 <= idx < len(sorted_hand):
                        selected_cards.append(sorted_hand[idx])
                    else:
                        print(f"Invalid card number: {idx + 1}")
                        break
                else:
                    return selected_cards
            except ValueError:
                print("Please enter valid numbers.")
    
    def handle_hitting_phase(self, player: Player):
        """Handle hitting on completed phases"""
        while True:
            hit = input("Do you want to hit on a phase? (y/n): ").strip().lower()
            if hit in ['n', 'no']:
                break
            elif hit not in ['y', 'yes']:
                print("Please enter y or n.")
                continue
            
            # Show available targets
            targets = self.game.get_available_targets_for_hitting(player)
            if not targets and not player.completed_phase_this_round:
                print("No available targets for hitting.")
                break
            
            print("\n" + "="*50)
            print("AVAILABLE TARGETS FOR HITTING:")
            print("="*50)
            
            if player.completed_phase_this_round:
                current_phase = player.get_current_phase()
                print(f"\n0. YOUR OWN PHASE (Phase {current_phase.phase_number}: {current_phase.description})")
                print("   Your cards:", ", ".join(str(c) for c in player.completed_phase_cards))
            
            for i, target in enumerate(targets, 1):
                target_phase = target.get_current_phase()
                print(f"\n{i}. {target.name}'s PHASE (Phase {target_phase.phase_number}: {target_phase.description})")
                print(f"   Their cards: {', '.join(str(c) for c in target.completed_phase_cards)}")
            
            # Select target and card
            target_choice = input("Select target (or 'done' to finish): ").strip()
            if target_choice.lower() == 'done':
                break
            
            try:
                target_idx = int(target_choice)
                if target_idx == 0 and player.completed_phase_this_round:
                    target_player = player
                elif 1 <= target_idx <= len(targets):
                    target_player = targets[target_idx - 1]
                else:
                    print("Invalid target selection.")
                    continue
            except ValueError:
                print("Invalid target selection.")
                continue
            
            # Select card to play
            self.show_player_hand(player)
            sorted_hand = player.get_sorted_hand()
            try:
                card_idx = int(input("Select card number to play: ")) - 1
                if 0 <= card_idx < len(sorted_hand):
                    card = sorted_hand[card_idx]
                    
                    if target_player == player:
                        success = self.game.player_hit_on_own_phase(player, card)
                    else:
                        success = self.game.player_hit_on_phase(player, card, target_player)
                    
                    if success:
                        print(f"Successfully played {card} on {target_player.name}'s phase!")
                    else:
                        print(f"Cannot play {card} on that phase.")
                else:
                    print("Invalid card selection.")
            except ValueError:
                print("Invalid card number.")
    
    def handle_discard_phase(self, player: Player) -> int:
        """Handle the discard phase and return skip count"""
        print("\nSelect a card to discard:")
        self.show_player_hand(player)
        
        # Get the sorted hand to match what was displayed
        sorted_hand = player.get_sorted_hand()
        
        while True:
            try:
                card_idx = int(input("Card number to discard: ")) - 1
                if 0 <= card_idx < len(sorted_hand):
                    card = sorted_hand[card_idx]
                    
                    if self.game.discard_card(player, card):
                        print(f"Discarded: {card}")
                        
                        # Check if it's a skip card
                        if card.card_type == CardType.SKIP:
                            skip_count = self.game.handle_skip_card(card)
                            if skip_count == 0:
                                print("Skip card played! You get another turn!")
                            else:
                                print("Skip card played! Next player is skipped!")
                            return skip_count
                        return 1
                    else:
                        print("Unable to discard that card.")
                else:
                    print("Invalid card number.")
            except ValueError:
                print("Please enter a valid number.")
    
    def show_player_status(self, player: Player):
        """Show current player's status"""
        current_phase = player.get_current_phase()
        print("\n" + "-"*40)
        print("YOUR STATUS")
        print("-"*40)
        print(f"Name: {player.name}")
        print(f"Current Phase: Phase {current_phase.phase_number} - {current_phase.description}")
        print(f"Total Score: {player.score} points")
        
        if player.completed_phase_this_round:
            print("\n[COMPLETED] PHASE COMPLETED THIS ROUND!")
            print("Completed cards:")
            for card in player.completed_phase_cards:
                print(f"  - {card}")
        else:
            print(f"\n[!] Phase Requirements: {self._get_phase_hint(current_phase)}")
    
    def _get_phase_hint(self, phase: Phase) -> str:
        """Get a helpful hint for completing the current phase"""
        hints = {
            1: "Look for pairs of the same number (like 5,5,5 and 8,8,8)",
            2: "Need 3 of a kind AND 4 consecutive numbers", 
            3: "Need 4 of a kind AND 4 consecutive numbers",
            4: "Need 7 consecutive numbers (like 3,4,5,6,7,8,9)",
            5: "Need 8 consecutive numbers",
            6: "Need 9 consecutive numbers", 
            7: "Look for two groups of 4 same numbers each",
            8: "Need 7 cards all the same color (wilds count as any color)",
            9: "Need 5 of a kind AND 2 of a kind",
            10: "Need 5 of a kind AND 3 of a kind"
        }
        return hints.get(phase.phase_number, "Complete the phase requirements")
    
    def show_player_hand(self, player: Player):
        """Show player's hand with numbered cards, sorted optimally for current phase"""
        print(f"\n{player.name}'s hand (sorted for Phase {player.current_phase}):")
        sorted_hand = player.get_sorted_hand()
        
        # Display cards with sequential numbering in sorted order
        for i, card in enumerate(sorted_hand, 1):
            print(f"{i}. {card}")
    
    def show_completed_phase(self, player: Player):
        """Show player's completed phase cards"""
        print(f"\n{player.name}'s completed phase:")
        for card in player.completed_phase_cards:
            print(f"  {card}")
    
    def show_game_state(self):
        """Show current game state"""
        status = self.game.get_game_status()
        print("\n" + "-"*40)
        print("GAME STATUS")
        print("-"*40)
        print(f"Round: {status['round']}")
        print(f"Deck: {status['deck_size']} cards remaining")
        if status['discard_top']:
            if status['discard_top'].card_type == CardType.SKIP:
                print(f"Discard pile top: {status['discard_top']} [CANNOT BE PICKED UP]")
            else:
                print(f"Discard pile top: {status['discard_top']}")
        
        print("\nOTHER PLAYERS:")
        for player_info in status['players']:
            completed = " [PHASE COMPLETED THIS ROUND]" if player_info['completed_phase'] else ""
            print(f"  - {player_info['name']}: Phase {player_info['phase']}, "
                  f"{player_info['hand_size']} cards, Score: {player_info['score']}{completed}")
    
    def show_round_scores(self):
        """Show scores after a round"""
        print("\nRound Scores:")
        for player in self.game.players:
            print(f"{player.name}: {player.score} points")
    
    def show_game_results(self):
        """Show final game results"""
        print("\n" + "=" * 50)
        print("GAME OVER!")
        print("=" * 50)
        
        if self.game.state.winner:
            print(f"Winner: {self.game.state.winner.name}!")
        
        print("\nFinal Scores:")
        sorted_players = sorted(self.game.players, key=lambda p: p.score, reverse=True)
        for i, player in enumerate(sorted_players, 1):
            print(f"{i}. {player.name}: {player.score} points (Phase {player.current_phase})")


def main():
    """Main entry point"""
    cli = Phase10CLI()
    try:
        cli.start_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Thanks for playing!")


if __name__ == "__main__":
    main()