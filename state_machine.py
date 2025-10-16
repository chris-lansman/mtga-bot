"""
State machine for MTGA Bot game flow.

Implements a clean state pattern for managing different game states.
"""
import logging
import time
from enum import Enum, auto
from abc import ABC, abstractmethod

logger = logging.getLogger('mtgalog')


class GameState(Enum):
    """Enumeration of all possible game states."""
    UNKNOWN = auto()
    START_SCREEN = auto()
    DECK_SELECT = auto()
    MATCHMAKING = auto()
    CARD_DRAW = auto()
    IN_MATCH = auto()
    MY_TURN_MAIN = auto()
    MY_TURN_COMBAT = auto()
    MY_TURN_END = auto()
    OPPONENT_TURN = auto()
    MATCH_RESULTS = auto()
    REWARDS = auto()
    ERROR = auto()


class State(ABC):
    """Abstract base class for all states."""
    
    def __init__(self, context):
        """Initialize state with context.
        
        Args:
            context: GameStateMachine instance
        """
        self.context = context
        self.state_type = GameState.UNKNOWN
    
    @abstractmethod
    def enter(self):
        """Called when entering this state."""
        pass
    
    @abstractmethod
    def execute(self):
        """Execute state logic. Returns next state or None to stay in current state."""
        pass
    
    @abstractmethod
    def exit(self):
        """Called when exiting this state."""
        pass
    
    def __str__(self):
        return f"{self.state_type.name}"


class StartScreenState(State):
    """Start screen state - click Play button."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.START_SCREEN
    
    def enter(self):
        logger.info("Entered START_SCREEN state")
    
    def execute(self):
        """Click play button and transition to deck select."""
        logger.info("Clicking Play button")
        self.context.actions.click_play()
        time.sleep(1)
        return DeckSelectState(self.context)
    
    def exit(self):
        logger.debug("Exiting START_SCREEN state")


class DeckSelectState(State):
    """Deck selection state."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.DECK_SELECT
    
    def enter(self):
        logger.info("Entered DECK_SELECT state")
    
    def execute(self):
        """Select deck and game mode, then click play."""
        logger.info("Selecting deck and game mode")
        self.context.actions.select_deck_and_play_style()
        self.context.actions.click_play()
        time.sleep(2)
        return MatchmakingState(self.context)
    
    def exit(self):
        logger.debug("Exiting DECK_SELECT state")


class MatchmakingState(State):
    """Waiting for matchmaking."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.MATCHMAKING
        self.wait_time = 0
        self.max_wait = 60  # Maximum wait time in seconds
    
    def enter(self):
        logger.info("Entered MATCHMAKING state")
        self.wait_time = 0
    
    def execute(self):
        """Wait for match to start."""
        time.sleep(1)
        self.wait_time += 1
        
        # Check if we've entered card draw phase
        if self.context.actions.check_if_card_draw_screen():
            return CardDrawState(self.context)
        
        # Check if we've entered match directly
        if self.context.actions.check_in_match():
            return InMatchState(self.context)
        
        # Timeout protection
        if self.wait_time > self.max_wait:
            logger.warning("Matchmaking timeout, returning to start")
            return StartScreenState(self.context)
        
        return None  # Stay in matchmaking
    
    def exit(self):
        logger.debug("Exiting MATCHMAKING state")


class CardDrawState(State):
    """Initial card draw state (keep/mulligan)."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.CARD_DRAW
    
    def enter(self):
        logger.info("Entered CARD_DRAW state")
    
    def execute(self):
        """Handle card draw/mulligan decision."""
        if self.context.actions.check_if_my_card_draw_done():
            logger.info("Cards accepted, entering match")
            return InMatchState(self.context)
        
        # Still waiting for card draw
        time.sleep(0.5)
        return None
    
    def exit(self):
        logger.debug("Exiting CARD_DRAW state")


class InMatchState(State):
    """In-match state coordinator."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.IN_MATCH
    
    def enter(self):
        logger.info("Entered IN_MATCH state")
    
    def execute(self):
        """Coordinate match sub-states."""
        # Check if match ended
        if not self.context.actions.check_in_match():
            return MatchResultsState(self.context)
        
        # Check whose turn it is
        if self.context.actions.check_if_my_turn():
            return MyTurnMainState(self.context)
        else:
            return OpponentTurnState(self.context)
    
    def exit(self):
        logger.debug("Exiting IN_MATCH state")


class MyTurnMainState(State):
    """My turn - main phase."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.MY_TURN_MAIN
    
    def enter(self):
        logger.info("Entered MY_TURN_MAIN state")
    
    def execute(self):
        """Play cards from hand."""
        phase = self.context.actions.determine_turn_phase()
        
        if phase == "play cards":
            self.context.actions.play_my_cards()
            return InMatchState(self.context)
        elif phase == "attack phase":
            return MyTurnCombatState(self.context)
        elif phase == "end turn":
            return MyTurnEndState(self.context)
        else:
            # Unknown phase, return to in-match
            return InMatchState(self.context)
    
    def exit(self):
        logger.debug("Exiting MY_TURN_MAIN state")


class MyTurnCombatState(State):
    """My turn - combat phase."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.MY_TURN_COMBAT
    
    def enter(self):
        logger.info("Entered MY_TURN_COMBAT state")
    
    def execute(self):
        """Handle combat phase."""
        self.context.actions.play_attack_phase()
        time.sleep(1)
        return InMatchState(self.context)
    
    def exit(self):
        logger.debug("Exiting MY_TURN_COMBAT state")


class MyTurnEndState(State):
    """My turn - end phase."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.MY_TURN_END
    
    def enter(self):
        logger.info("Entered MY_TURN_END state")
    
    def execute(self):
        """End turn."""
        self.context.actions.end_turn()
        time.sleep(1)
        return InMatchState(self.context)
    
    def exit(self):
        logger.debug("Exiting MY_TURN_END state")


class OpponentTurnState(State):
    """Opponent's turn."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.OPPONENT_TURN
    
    def enter(self):
        logger.info("Entered OPPONENT_TURN state")
    
    def execute(self):
        """Wait during opponent's turn, respond to prompts."""
        # Click resolve/next if needed
        self.context.actions.handle_opponent_prompts()
        
        # Check if it's our turn now
        if self.context.actions.check_if_my_turn():
            return InMatchState(self.context)
        
        # Check if match ended
        if not self.context.actions.check_in_match():
            return MatchResultsState(self.context)
        
        time.sleep(0.5)
        return None  # Stay in opponent turn
    
    def exit(self):
        logger.debug("Exiting OPPONENT_TURN state")


class MatchResultsState(State):
    """Match results screen (victory/defeat)."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.MATCH_RESULTS
    
    def enter(self):
        logger.info("Entered MATCH_RESULTS state")
    
    def execute(self):
        """Handle match results screen."""
        self.context.actions.match_result_actions()
        time.sleep(2)
        
        # Check if we have rewards to claim
        if self.context.actions.check_for_rewards():
            return RewardsState(self.context)
        
        # Otherwise return to start
        return StartScreenState(self.context)
    
    def exit(self):
        logger.debug("Exiting MATCH_RESULTS state")


class RewardsState(State):
    """Rewards screen."""
    
    def __init__(self, context):
        super().__init__(context)
        self.state_type = GameState.REWARDS
    
    def enter(self):
        logger.info("Entered REWARDS state")
    
    def execute(self):
        """Claim rewards."""
        self.context.actions.rewards_actions()
        time.sleep(2)
        return StartScreenState(self.context)
    
    def exit(self):
        logger.debug("Exiting REWARDS state")


class ErrorState(State):
    """Error recovery state."""
    
    def __init__(self, context, error_message="Unknown error"):
        super().__init__(context)
        self.state_type = GameState.ERROR
        self.error_message = error_message
        self.recovery_attempts = 0
        self.max_attempts = 3
    
    def enter(self):
        logger.error(f"Entered ERROR state: {self.error_message}")
    
    def execute(self):
        """Attempt error recovery."""
        self.recovery_attempts += 1
        
        if self.recovery_attempts > self.max_attempts:
            logger.error("Maximum recovery attempts reached, stopping bot")
            return None  # Will cause bot to stop
        
        logger.info(f"Error recovery attempt {self.recovery_attempts}/{self.max_attempts}")
        time.sleep(2)
        
        # Try to detect current state
        detected_state = self.context.actions.detect_current_state()
        if detected_state:
            return detected_state
        
        # If can't detect, try returning to start
        return StartScreenState(self.context)
    
    def exit(self):
        logger.debug("Exiting ERROR state")


class GameStateMachine:
    """Main state machine for game flow."""
    
    def __init__(self, actions):
        """Initialize state machine.
        
        Args:
            actions: Object containing all game actions (clicks, checks, etc.)
        """
        self.actions = actions
        self.current_state = StartScreenState(self)
        self.previous_state = None
        self.running = False
    
    def start(self):
        """Start the state machine."""
        logger.info("Starting state machine")
        self.running = True
        self.current_state.enter()
    
    def stop(self):
        """Stop the state machine."""
        logger.info("Stopping state machine")
        self.running = False
        if self.current_state:
            self.current_state.exit()
    
    def update(self):
        """Update state machine (call in main loop)."""
        if not self.running:
            return False
        
        try:
            # Execute current state
            next_state = self.current_state.execute()
            
            # Transition to next state if needed
            if next_state is not None:
                self.transition_to(next_state)
            
            return True
        
        except Exception as e:
            logger.error(f"Error in state machine: {e}", exc_info=True)
            error_state = ErrorState(self, str(e))
            self.transition_to(error_state)
            return True
    
    def transition_to(self, new_state):
        """Transition to a new state.
        
        Args:
            new_state: State instance to transition to
        """
        if new_state is None:
            self.stop()
            return
        
        logger.info(f"State transition: {self.current_state} -> {new_state}")
        
        # Exit current state
        self.current_state.exit()
        
        # Update states
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Enter new state
        self.current_state.enter()
    
    def get_current_state(self):
        """Get current state type.
        
        Returns:
            GameState: Current state enumeration
        """
        return self.current_state.state_type if self.current_state else GameState.UNKNOWN


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Mock actions object for testing
    class MockActions:
        def click_play(self):
            logger.info("Mock: Clicking play")
        
        def select_deck_and_play_style(self):
            logger.info("Mock: Selecting deck")
        
        def check_in_match(self):
            return True
        
        def check_if_my_turn(self):
            return True
        
        def determine_turn_phase(self):
            return "play cards"
        
        def play_my_cards(self):
            logger.info("Mock: Playing cards")
        
        def detect_current_state(self):
            return None
    
    # Create and run state machine
    actions = MockActions()
    sm = GameStateMachine(actions)
    sm.start()
    
    # Simulate a few updates
    for i in range(5):
        logger.info(f"Update {i+1}")
        sm.update()
        time.sleep(1)
    
    sm.stop()

