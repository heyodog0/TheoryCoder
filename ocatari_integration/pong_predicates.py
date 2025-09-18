# Pong predicates for TheoryCoder

def paddle_at_position(state, paddle_type, x, y):
    """Check if a paddle is at a specific position."""
    paddle_positions = state.get(paddle_type, [])
    for paddle_pos in paddle_positions:
        if len(paddle_pos) >= 2 and paddle_pos[0] == x and paddle_pos[1] == y:
            return True
    return False

def ball_at_position(state, x, y):
    """Check if the ball is at a specific position."""
    ball_positions = state.get('ball', [])
    for ball_pos in ball_positions:
        if len(ball_pos) >= 2 and ball_pos[0] == x and ball_pos[1] == y:
            return True
    return False

def paddle_can_reach_ball(state, paddle_type='player_paddle'):
    """Check if the paddle can potentially reach the ball."""
    paddle_positions = state.get(paddle_type, [])
    ball_positions = state.get('ball', [])
    
    if not paddle_positions or not ball_positions:
        return False
    
    paddle_y = paddle_positions[0][1] if len(paddle_positions[0]) >= 2 else 0
    ball_y = ball_positions[0][1] if len(ball_positions[0]) >= 2 else 0
    
    # Allow some tolerance for reaching the ball
    return abs(paddle_y - ball_y) <= 20

def ball_moving_towards_paddle(state, paddle_type='player_paddle'):
    """Estimate if the ball is moving towards the paddle based on position."""
    paddle_positions = state.get(paddle_type, [])
    ball_positions = state.get('ball', [])
    
    if not paddle_positions or not ball_positions:
        return False
    
    paddle_x = paddle_positions[0][0] if len(paddle_positions[0]) >= 2 else 0
    ball_x = ball_positions[0][0] if len(ball_positions[0]) >= 2 else 0
    
    # For player paddle (left side), ball moving towards means ball x is decreasing
    # For enemy paddle (right side), ball moving towards means ball x is increasing
    if paddle_type == 'player_paddle':
        return ball_x < 100  # Ball is on the left side of the screen
    else:  # enemy_paddle
        return ball_x > 60   # Ball is on the right side of the screen

def paddle_should_move_up(state, paddle_type='player_paddle'):
    """Check if the paddle should move up to intercept the ball."""
    paddle_positions = state.get(paddle_type, [])
    ball_positions = state.get('ball', [])
    
    if not paddle_positions or not ball_positions:
        return False
    
    paddle_y = paddle_positions[0][1] if len(paddle_positions[0]) >= 2 else 0
    ball_y = ball_positions[0][1] if len(ball_positions[0]) >= 2 else 0
    
    return ball_y < paddle_y - 5  # Ball is above paddle

def paddle_should_move_down(state, paddle_type='player_paddle'):
    """Check if the paddle should move down to intercept the ball."""
    paddle_positions = state.get(paddle_type, [])
    ball_positions = state.get('ball', [])
    
    if not paddle_positions or not ball_positions:
        return False
    
    paddle_y = paddle_positions[0][1] if len(paddle_positions[0]) >= 2 else 0
    ball_y = ball_positions[0][1] if len(ball_positions[0]) >= 2 else 0
    
    return ball_y > paddle_y + 5  # Ball is below paddle

def paddle_aligned_with_ball(state, paddle_type='player_paddle'):
    """Check if the paddle is well-aligned with the ball."""
    paddle_positions = state.get(paddle_type, [])
    ball_positions = state.get('ball', [])
    
    if not paddle_positions or not ball_positions:
        return False
    
    paddle_y = paddle_positions[0][1] if len(paddle_positions[0]) >= 2 else 0
    ball_y = ball_positions[0][1] if len(ball_positions[0]) >= 2 else 0
    
    return abs(paddle_y - ball_y) <= 8  # Within reasonable hitting range

def game_active(state):
    """Check if the game is currently active (ball and paddles present)."""
    return (len(state.get('ball', [])) > 0 and 
            len(state.get('player_paddle', [])) > 0 and 
            len(state.get('enemy_paddle', [])) > 0)

def ball_near_paddle(state, paddle_type='player_paddle', distance_threshold=30):
    """Check if the ball is near the specified paddle."""
    paddle_positions = state.get(paddle_type, [])
    ball_positions = state.get('ball', [])
    
    if not paddle_positions or not ball_positions:
        return False
    
    paddle_x = paddle_positions[0][0] if len(paddle_positions[0]) >= 2 else 0
    paddle_y = paddle_positions[0][1] if len(paddle_positions[0]) >= 2 else 0
    ball_x = ball_positions[0][0] if len(ball_positions[0]) >= 2 else 0
    ball_y = ball_positions[0][1] if len(ball_positions[0]) >= 2 else 0
    
    distance = ((paddle_x - ball_x) ** 2 + (paddle_y - ball_y) ** 2) ** 0.5
    return distance <= distance_threshold
