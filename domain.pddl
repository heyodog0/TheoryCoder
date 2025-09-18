(define (domain pong)
  (:requirements :strips)
  
  (:predicates
    (game_active)
    (paddle_can_reach_ball)
    (ball_near_paddle)
    (paddle_aligned_with_ball)
    (can_move)
  )
  
  (:action left
    :parameters ()
    :precondition (game_active)
    :effect (can_move)
  )
  
  (:action right
    :parameters ()
    :precondition (game_active)
    :effect (can_move)
  )
  
  (:action fire
    :parameters ()
    :precondition (game_active)
    :effect (can_move)
  )
  
  (:action noop
    :parameters ()
    :precondition (game_active)
    :effect (can_move)
  )
  
  (:action leftfire
    :parameters ()
    :precondition (game_active)
    :effect (can_move)
  )
  
  (:action rightfire
    :parameters ()
    :precondition (game_active)
    :effect (can_move)
  )
)
