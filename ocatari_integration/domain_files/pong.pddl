(define (domain pong)
  (:requirements :strips :typing)
  
  (:types
    paddle ball position direction
  )
  
  (:predicates
    (at_paddle ?p - paddle ?pos - position)
    (at_ball ?b - ball ?pos - position)
    (paddle_can_move ?p - paddle ?dir - direction)
    (ball_moving_towards ?b - ball ?dir - direction)
    (score_increased ?p - paddle)
    (game_won)
    (game_lost)
    (can_hit_ball ?p - paddle ?b - ball)
  )
  
  (:action move_paddle_up
    :parameters (?p - paddle ?pos1 ?pos2 - position)
    :precondition (and 
      (at_paddle ?p ?pos1)
      (paddle_can_move ?p up)
    )
    :effect (and 
      (not (at_paddle ?p ?pos1))
      (at_paddle ?p ?pos2)
    )
  )
  
  (:action move_paddle_down
    :parameters (?p - paddle ?pos1 ?pos2 - position)
    :precondition (and 
      (at_paddle ?p ?pos1)
      (paddle_can_move ?p down)
    )
    :effect (and 
      (not (at_paddle ?p ?pos1))
      (at_paddle ?p ?pos2)
    )
  )
  
  (:action hit_ball
    :parameters (?p - paddle ?b - ball ?pos - position)
    :precondition (and 
      (at_paddle ?p ?pos)
      (at_ball ?b ?pos)
      (can_hit_ball ?p ?b)
    )
    :effect (and 
      (ball_moving_towards ?b away)
    )
  )
  
  (:action score_point
    :parameters (?p - paddle)
    :precondition (score_increased ?p)
    :effect (game_won)
  )
)
