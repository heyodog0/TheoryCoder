# from worldmodel2 import transition_model
from worldmodel import transition_model
from copy import deepcopy
from pathlib import Path
from predicates import *
from preprocessing import checker

def update_entity_categorizations(state):
    """
    Update the state dictionary with latent variables.

    Args:
        state (dict): The current game state.
    
    Returns:
        dict: The updated state with updated categorizations.
    """
    
    return state

def convert_state_to_hashable(state):
    """
    Convert the state dictionary to a hashable representation.
    """
    hashable_state = []
    for k, v in state.items():
        if isinstance(v, list):
            # Handle lists of lists (e.g., positions) and lists of dictionaries (e.g., agent_carrying)
            if all(isinstance(item, list) for item in v):
                hashable_state.append((k, tuple(map(tuple, v))))
            elif all(isinstance(item, dict) for item in v):
                # Convert list of dictionaries to a tuple of sorted tuples for hashability
                hashable_state.append(
                    (k, tuple(frozenset(item.items()) for item in v))
                )
            elif all(isinstance(item, (int, float, str, bool)) for item in v):
                # Handle flat lists of primitives like [0, 1]
                hashable_state.append((k, tuple(v)))
            else:
                raise TypeError(f"Unsupported list structure in state for key {k}")
        elif isinstance(v, dict):
            # Convert dictionary to a frozenset of its items for hashability
            hashable_state.append((k, frozenset(v.items())))
        elif isinstance(v, (bool, str, int, float)):
            # Primitive types are hashable as-is
            hashable_state.append((k, v))
        else:
            raise TypeError(f"Unsupported type in state: {type(v)} for key {k}")
    return frozenset(hashable_state)



# 50k was the baseline worked for mos 5000000
def enumerative_search(state0, operator, preconditions, effects, strategy='bfs', max_iters=500000, debug_callback=None, level=None):
    """
    Search for a goal state. Takes an optional `debug_callback` to call when errors occur.
    """
    from collections import deque

    actions_set = ["left", "right", "forward", "pickup", "drop", "toggle", "done"]

    # First check if preconditions are already satisfied
    if checker(state0, preconditions, operator):
        print("Preconditions already satisfied, checking if effects are met")
        if checker(state0, effects, operator):
            print("Effects already satisfied, goal reached immediately")
            return ["no-op"], state0

    start = ()
    states = {start: deepcopy(state0)}
    queue = deque([start])
    visited = set()
    search_iters = 0    
    no_progress_count = 0
    last_queue_size = len(queue)

    while queue:
        search_iters += 1
        if strategy == 'bfs':
            node = queue.popleft()
        else:
            node = queue.pop()

        current_state_hashable = convert_state_to_hashable(states[node])

        if current_state_hashable in visited:
            continue

        visited.add(current_state_hashable)

        # Check if effects (goals) are satisfied
        if checker(states[node], effects, operator):
            print('Goal reached')
            return list(node), states[node]

        # Termination conditions
        if search_iters > max_iters:
            print('MAX DEPTH REACHED')
            return ["no-op"], states[node]
            
        # Check for no progress (queue not growing)
        if len(queue) == last_queue_size:
            no_progress_count += 1
        else:
            no_progress_count = 0
        last_queue_size = len(queue)
        
        # If we haven't made progress for a while and queue is small, likely stuck
        if no_progress_count > 100 and len(queue) < 10:
            print('No progress being made, likely unreachable goal')
            return ["no-op"], states[node]

        for a in actions_set:
            try:
                states[node] = update_entity_categorizations(states[node])
                state = transition_model(deepcopy(states[node]), a)
                state = update_entity_categorizations(state)
                
                # Only add states that are different and not already visited
                if state and state != states[node]:
                    state_hashable = convert_state_to_hashable(state)
                    if state_hashable not in visited:
                        new_node = node + (a,)
                        states[new_node] = deepcopy(state)
                        queue.append(new_node)

                        # Check if this new state satisfies the goal
                        if checker(state, effects, operator):
                            print('Goal reached')
                            return list(new_node), state

            except Exception as e:  # Catch all exceptions
                print(f"Exception encountered: {e}. Triggering model debug.")
                if debug_callback:
                    debug_callback(states[node], a)  # Call the debug function with state and action
                else:
                    raise e  # Re-raise if no debug callback is provided
    
    print('Search exhausted, goal not reachable')
    return ["no-op"], states.get((), state0)
