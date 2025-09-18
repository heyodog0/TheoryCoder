from copy import deepcopy

def transition_model(state, action):
    new_state = deepcopy(state)
    agent_pos = state['red_agent'][0]
    agent_dir = state['agent_direction']
    carrying = state['agent_carrying']
    
    # Calculate the position in front of the agent
    front_pos = [agent_pos[0] + agent_dir[0], agent_pos[1] + agent_dir[1]]
    
    # Helper function to check if a position is blockable
    def is_position_blocked(position):
        # Check walls
        if position in state.get('grey_wall', []):
            return True
        # Check if position is occupied by another entity
        for key in state:
            if key != 'red_agent' and key != 'agent_direction' and key != 'agent_carrying':
                if position in state[key]:
                    return True
        return False

    if action == 'forward':
        # Move the agent forward if not blocked
        if not is_position_blocked(front_pos):
            new_state['red_agent'] = [front_pos]
        return new_state

    elif action == 'left':
        # Rotate the agent's direction to the left (counterclockwise)
        if agent_dir == [-1, 0]:  # Facing left
            new_state['agent_direction'] = [0, 1]  # Face up
        elif agent_dir == [1, 0]:  # Facing right
            new_state['agent_direction'] = [0, -1]  # Face down
        elif agent_dir == [0, 1]:  # Facing up
            new_state['agent_direction'] = [1, 0]  # Face right
        elif agent_dir == [0, -1]:  # Facing down
            new_state['agent_direction'] = [-1, 0]  # Face left
        return new_state

    elif action == 'right':
        # Rotate the agent's direction to the right (clockwise)
        if agent_dir == [-1, 0]:  # Facing left
            new_state['agent_direction'] = [0, -1]  # Face down
        elif agent_dir == [1, 0]:  # Facing right
            new_state['agent_direction'] = [0, 1]  # Face up
        elif agent_dir == [0, 1]:  # Facing up
            new_state['agent_direction'] = [-1, 0]  # Face left
        elif agent_dir == [0, -1]:  # Facing down
            new_state['agent_direction'] = [1, 0]  # Face right
        return new_state

    elif action == 'pickup':
        # Attempt to pick up an item if one exists at the front position
        if not carrying:  # Can only pick up if not already carrying something
            for entity in state.keys():
                if entity.endswith('_box') or entity.endswith('_ball') or entity.endswith('_key'):
                    if front_pos in state[entity]:
                        new_state['agent_carrying'] = [entity]
                        new_state[entity].remove(front_pos)
                        break
        return new_state

    elif action == 'drop':
        # Attempt to drop the carried item at the front position
        if carrying:
            item_to_drop = carrying[0]
            item_type = item_to_drop.split('_')[-1]
            if not is_position_blocked(front_pos):
                new_state['agent_carrying'] = []
                if item_to_drop not in new_state:
                    new_state[item_to_drop] = []
                new_state[item_to_drop].append(front_pos)
        return new_state

    elif action == 'toggle':
        # Toggle boxes and doors
        for entity in state.keys():
            if entity.endswith('_box') and front_pos in state[entity]:
                color = entity.split('_')[0]
                locked_door_key = f'locked_{color}_door'
                corresponding_key = f'{color}_key'
                
                # Check for locked door and absence of key
                if locked_door_key in state and corresponding_key not in state:
                    new_state[corresponding_key] = [front_pos]
                    new_state[entity].remove(front_pos)
                break
            elif entity.startswith('locked_') and front_pos in state[entity]:
                color = entity.split('_')[1]
                key_name = f'{color}_key'
                if key_name in carrying:
                    open_door_key = f'open_{color}_door'
                    if open_door_key not in new_state:
                        new_state[open_door_key] = []
                    new_state[open_door_key].append(front_pos)
                    new_state[entity].remove(front_pos)
                break
            elif entity.startswith('closed_') and front_pos in state[entity]:
                open_door_key = entity.replace('closed_', 'open_')
                if open_door_key not in new_state:
                    new_state[open_door_key] = []
                new_state[open_door_key].append(front_pos)
                new_state[entity].remove(front_pos)
                break
        return new_state

    return state