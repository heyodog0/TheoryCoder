# make sure to include these import statements
from predicates import *
from copy import deepcopy
from utils import directions

def transition_model(state, action):
    # Create a deep copy of the state to avoid mutating the original state directly
    new_state = deepcopy(state)
    
    # Define max_x assuming it's part of the state or a constant
    max_x = state.get('max_x', 200)  # Replace 200 with the actual maximum x value if known

    # Movement deltas
    player_move_delta = 5  # Adjusted based on observed state
    enemy_move_delta = 4   # Adjusted based on observed state
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

    # Move the ball if it's initialized
    if new_state['ball']:
        ball_x, ball_y = new_state['ball'][0]
        new_state['ball'][0] = [ball_x - ball_move_delta, ball_y + ball_move_delta]  # Adjust ball movement

    # Move the enemy paddle if it's initialized
    if new_state['enemy_paddle']:
        enemy_x, enemy_y = new_state['enemy_paddle'][0]
        new_state['enemy_paddle'][0] = [enemy_x, enemy_y + enemy_move_delta]  # Move y

    # Update frame count to simulate time progression
    new_state['frame'] = state.get('frame', 0) + 1  # Increment frame by 1 per action

    # Handle score logic, ball movement, and collision (not detailed here)
    # This would involve updating 'ball', 'score_left', and 'score_right' based on game rules

    # Return the modified state
    return new_state