from predicates import *
from copy import deepcopy

# Sokoban World Model - Learning how boxes and avatar interact
def transition_model(state, action):
    """
    Initial Sokoban transition model - will be improved through experience
    
    Basic rules:
    - Avatar can move left/right/up/down
    - Avatar pushes boxes when moving into them
    - Boxes can be pushed if there's empty space behind them
    - Holes (goals) capture boxes when boxes are pushed into them
    """
    new_state = deepcopy(state)
    
    # Get current avatar position (take first avatar if multiple exist)
    avatars = new_state.get('avatar', [[0, 0]])
    avatar_pos = avatars[0] if avatars else [0, 0]
    boxes = new_state.get('box', [])
    walls = new_state.get('wall', [])
    holes = new_state.get('hole', [])
    
    # Calculate new position based on action
    if action == 'left':
        new_pos = [avatar_pos[0], avatar_pos[1] - 1]
    elif action == 'right':
        new_pos = [avatar_pos[0], avatar_pos[1] + 1]
    elif action == 'up':
        new_pos = [avatar_pos[0] - 1, avatar_pos[1]]
    elif action == 'down':
        new_pos = [avatar_pos[0] + 1, avatar_pos[1]]
    else:
        return new_state  # No change for invalid action
    
    # Check if new position is blocked by wall
    if new_pos in walls:
        return new_state  # Can't move into wall
    
    # Check if there's a box at the new position
    if new_pos in boxes:
        # Calculate where the box would be pushed
        box_new_pos = [new_pos[0] + (new_pos[0] - avatar_pos[0]), 
                       new_pos[1] + (new_pos[1] - avatar_pos[1])]
        
        # Check if box can be pushed (not into wall or another box)
        if box_new_pos in walls or box_new_pos in boxes:
            return new_state  # Can't push box
        
        # Push the box
        box_index = boxes.index(new_pos)
        new_state['box'][box_index] = box_new_pos
        
        # Check if box landed in a hole
        if box_new_pos in holes:
            # Box captured by hole - remove box and hole
            new_state['box'].pop(box_index)
            hole_index = holes.index(box_new_pos)
            new_state['hole'].pop(hole_index)
    
    # Move avatar to new position
    new_state['avatar'][0] = new_pos
    
    return new_state

