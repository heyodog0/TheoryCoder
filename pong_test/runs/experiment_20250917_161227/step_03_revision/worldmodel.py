# make sure to include these import statements
from predicates import *
from copy import deepcopy
from utils import directions

def transition_model(state, action):
    # Create a deep copy of the state to avoid mutating the original state directly
    new_state = deepcopy(state)

    # Define max_x assuming it's part of the state or a constant
    max_x = state.get('max_x', 200)  # Replace 200 with the actual maximum x value if known

    # Initialize entities if they are missing in the initial state
    if 'player_paddle' not in new_state or not new_state['player_paddle']:
        new_state['player_paddle'] = [[142, 103]]
    if 'enemy_paddle' not in new_state or not new_state['enemy_paddle']:
        new_state['enemy_paddle'] = [[18, 126]]
    if 'ball' not in new_state or not new_state['ball']:
        new_state['ball'] = [[75, 121]]
    if 'score_left' not in new_state or not new_state['score_left']:
        new_state['score_left'] = [[42, 11]]
    if 'score_right' not in new_state or not new_state['score_right']:
        new_state['score_right'] = [[122, 11]]

    # Movement deltas
    player_move_delta = 5  # Adjusted based on observed state
    enemy_move_delta = 2   # Adjusted based on observed state
    ball_move_delta = 2    # Adjusted based on observed state

    # Example handling of action logic
    if action == 'left':
        # Move player paddle to the left, if possible
        if new_state['player_paddle']:
            new_state['player_paddle'][0][0] -= 1  # Move left by one unit
    elif action == 'right':
        # Move player paddle to the right, if possible
        if new_state['player_paddle']:
            new_state['player_paddle'][0][0] += 1  # Move right by one unit
    elif action == 'fire':
        # Logic to handle 'fire' (could be related to starting the ball movement)
        pass
    elif action == 'noop':
        # No operation, state remains unchanged
        pass
    elif action == 'leftfire':
        # Combination of moving left and firing
        if new_state['player_paddle']:
            new_state['player_paddle'][0][0] -= 1  # Move left by one unit
        # Additional logic for 'fire'
        pass
    elif action == 'rightfire':
        # Combination of moving right and firing
        if new_state['player_paddle']:
            new_state['player_paddle'][0][0] += 1  # Move right by one unit
        # Additional logic for 'fire'
        pass

    # Ensure player paddle stays within bounds
    if new_state['player_paddle']:
        player_x, player_y = new_state['player_paddle'][0]
        player_x = max(0, min(player_x, max_x))  # Ensure x is within 0 and max_x
        new_state['player_paddle'][0] = [player_x, player_y + player_move_delta]  # Move y

    # Move the ball
    if new_state['ball']:
        ball_x, ball_y = new_state['ball'][0]
        new_state['ball'][0] = [ball_x - ball_move_delta, ball_y + ball_move_delta]  # Adjusted ball movement

    # Move the enemy paddle
    if new_state['enemy_paddle']:
        enemy_x, enemy_y = new_state['enemy_paddle'][0]
        new_state['enemy_paddle'][0] = [enemy_x, enemy_y + enemy_move_delta]  # Move y

    # Update frame count to simulate time progression
    new_state['frame'] = state.get('frame', 0) + 21  # Adjust frame increment

    # Handle score logic, ball movement, and collision (not detailed here)
    # This would involve updating 'ball', 'score_left', and 'score_right' based on game rules

    # Return the modified state
    return new_state