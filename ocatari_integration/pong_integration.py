#!/usr/bin/env python3
"""
Main integration script for Pong + TheoryCoder

This script demonstrates how to run TheoryCoder with the OCAtari Pong environment.
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add the ocatari_integration directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from envs.pong_env import PongEnv
from theorycoderv2 import TheoryCoderAgent


def test_pong_with_theorycoder():
    """Test the complete Pong + TheoryCoder integration."""
    print("🚀 Testing Pong + TheoryCoder Integration")
    print("=" * 50)
    
    # Create the Pong environment
    print("🎮 Creating Pong environment...")
    pong_env = PongEnv(level_set="test", level_id=0)
    
    # Create TheoryCoder agent
    print("🧠 Creating TheoryCoder agent...")
    agent = TheoryCoderAgent(
        base_dir="ocatari_integration/experiments",
        episode_length=50,
        world_model_load_name="worldmodel",
        do_revise_model=True,
        plans_file_name="pong_plans.json",
        query_mode="openai_direct",
        prune_plans=False
    )
    
    try:
        # Test basic environment functionality
        print("\n🧪 Testing basic environment functionality...")
        state = pong_env.reset()
        print(f"Initial state keys: {list(state.keys())}")
        print(f"Action space: {pong_env.actions_set}")
        print(f"State summary: {pong_env.get_state_summary()}")
        
        # Test a few manual steps
        print("\n🎮 Testing manual steps...")
        for i in range(5):
            action = pong_env.actions_set[i % len(pong_env.actions_set)]
            state, reward, done, info = pong_env.step(action)
            print(f"Step {i+1}: Action '{action}', Reward {reward}, Done {done}")
            print(f"  {pong_env.get_state_summary()}")
            
            if done:
                print("🏁 Episode ended, resetting...")
                pong_env.reset()
        
        # Now test with TheoryCoder (basic integration)
        print("\n🧠 Testing basic TheoryCoder integration...")
        print("Note: Full integration requires domain files and world model setup.")
        
        # Reset environment for TheoryCoder
        pong_env.reset()
        
        # Test get_obs method (what TheoryCoder will use)
        obs = pong_env.get_obs()
        print(f"Observation format for TheoryCoder: {type(obs)}")
        print(f"Observation keys: {list(obs.keys())}")
        
        # Test properties TheoryCoder expects
        print(f"Won: {pong_env.won}, Lost: {pong_env.lost}")
        print(f"Level set: {pong_env.level_set}, Level ID: {pong_env.level_id}")
        
        print("\n✅ Basic integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        pong_env.close()


def run_pong_with_theorycoder_simple():
    """
    Run a simplified version of TheoryCoder with Pong.
    This demonstrates the core loop without full world model learning.
    """
    print("🎮 Running Pong with TheoryCoder (Simplified)")
    print("=" * 50)
    
    # Create environment
    env = PongEnv(level_set="demo", level_id=0)
    
    try:
        # Simple episode loop
        max_steps = 100
        step_count = 0
        
        state = env.reset()
        print(f"🔄 Starting episode with {max_steps} max steps")
        
        while step_count < max_steps and not env.won and not env.lost:
            # Simple strategy: always try to move towards the ball
            action = choose_simple_action(state)
            
            state, reward, done, info = env.step(action)
            step_count += 1
            
            if step_count % 10 == 0:
                print(f"Step {step_count}: Action '{action}', Reward {reward}")
                print(f"  {env.get_state_summary()}")
            
            if done:
                break
        
        print(f"\n🏁 Episode finished after {step_count} steps")
        print(f"Final status: Won={env.won}, Lost={env.lost}")
        print(f"Final score: {env.player_score}-{env.enemy_score}")
        
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        env.close()


def choose_simple_action(state):
    """
    Simple action selection strategy for demonstration.
    
    Args:
        state: Current game state
        
    Returns:
        str: Action to take
    """
    # Get ball and paddle positions
    ball_positions = state.get('ball', [])
    paddle_positions = state.get('player_paddle', [])
    
    if not ball_positions or not paddle_positions:
        return 'noop'  # No action if we can't see ball or paddle
    
    ball_y = ball_positions[0][1] if len(ball_positions[0]) >= 2 else 0
    paddle_y = paddle_positions[0][1] if len(paddle_positions[0]) >= 2 else 0
    
    # Simple strategy: move paddle towards ball
    if ball_y < paddle_y - 5:
        return 'left'   # Move up (left in Pong action space)
    elif ball_y > paddle_y + 5:
        return 'right'  # Move down (right in Pong action space)
    else:
        return 'fire'   # Stay in position or fire


if __name__ == "__main__":
    print("🎮 OCAtari Pong + TheoryCoder Integration")
    print("=" * 60)
    
    # Test basic integration
    test_pong_with_theorycoder()
    
    print("\n" + "=" * 60)
    
    # Run simple demonstration
    run_pong_with_theorycoder_simple()
    
    print("\n🎉 Integration demonstration complete!")
    print("Next steps:")
    print("  1. Set up proper domain files in TheoryCoder")
    print("  2. Create initial world model for Pong")
    print("  3. Add Pong support to theorycoderv2.py argument parser")
    print("  4. Test full world model learning pipeline")
