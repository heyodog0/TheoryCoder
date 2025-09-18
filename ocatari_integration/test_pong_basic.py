#!/usr/bin/env python3
"""
Basic test script for Pong integration without full TheoryCoder.

This tests just the OCAtari Pong environment wrapper.
"""

import sys
import os
from pathlib import Path

# Add the ocatari_integration directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from pong_extractor import PongExtractor
from envs.pong_env import PongEnv


def test_pong_extractor():
    """Test the basic Pong extractor functionality."""
    print("🧪 Testing PongExtractor...")
    
    try:
        extractor = PongExtractor(mode="ram")
        
        # Test initialization
        if extractor.initialize_env():
            print("Environment initialized successfully")
            
            # Test state extraction
            state = extractor.get_current_state()
            print(f"State extracted: {list(state.keys())}")
            
            # Test a few steps
            for i in range(3):
                action = i % 6  # Valid action range
                state, reward, done, info = extractor.step(action)
                print(f"Step {i+1}: Action {action}, Reward {reward}, Done {done}")
                print(f"  Ball: {len(state.get('ball', []))}, Paddles: Player={len(state.get('player_paddle', []))}, Enemy={len(state.get('enemy_paddle', []))}")
            
            extractor.close()
            print("PongExtractor test completed successfully")
            return True
        else:
            print("Failed to initialize environment")
            return False
            
    except Exception as e:
        print(f"PongExtractor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pong_env():
    """Test the PongEnv wrapper for TheoryCoder."""
    print("\nTesting PongEnv wrapper...")
    
    try:
        env = PongEnv(level_set="test", level_id=0)
        
        # Test reset
        state = env.reset()
        print(f"Environment reset: {list(state.keys())}")
        print(f"Actions available: {env.actions_set}")
        
        # Test steps
        for i, action in enumerate(env.actions_set[:3]):
            state, reward, done, info = env.step(action)
            print(f"Step {i+1}: Action '{action}', Reward {reward}, Done {done}")
            print(f"  Won: {env.won}, Lost: {env.lost}")
            print(f"  {env.get_state_summary()}")
            
            if done:
                break
        
        env.close()
        print("PongEnv test completed successfully")
        return True
        
    except Exception as e:
        print(f"PongEnv test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_predicates():
    """Test the Pong predicates."""
    print("\nTesting Pong predicates...")
    
    try:
        # Import predicates
        import pong_predicates as predicates
        
        # Create a test state
        test_state = {
            'player_paddle': [[20, 50]],
            'enemy_paddle': [[140, 60]],
            'ball': [[80, 55]],
            'score_left': [],
            'score_right': [],
            'walls': []
        }
        
        # Test predicates
        tests = [
            ("game_active", predicates.game_active(test_state)),
            ("paddle_can_reach_ball", predicates.paddle_can_reach_ball(test_state)),
            ("ball_moving_towards_paddle", predicates.ball_moving_towards_paddle(test_state)),
            ("paddle_aligned_with_ball", predicates.paddle_aligned_with_ball(test_state)),
            ("ball_near_paddle", predicates.ball_near_paddle(test_state, distance_threshold=50))
        ]
        
        print("Predicate test results:")
        for name, result in tests:
            print(f"  {name}: {result}")
        
        print("Predicates test completed successfully")
        return True
        
    except Exception as e:
        print(f"Predicates test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("OCAtari Pong Integration - Basic Tests")
    print("=" * 50)
    
    success_count = 0
    total_tests = 3
    
    # Test 1: PongExtractor
    if test_pong_extractor():
        success_count += 1
    
    # Test 2: PongEnv wrapper
    if test_pong_env():
        success_count += 1
    
    # Test 3: Predicates
    if test_predicates():
        success_count += 1
    
    print(f"\nTests completed: {success_count}/{total_tests} passed")
    
    if success_count == total_tests:
        print("All tests passed! Pong integration is ready.")
        print("\nNext steps:")
        print("1. Install OCAtari: pip install ocatari")
        print("2. Run: python ocatari_integration/pong_integration.py")
        print("3. Try with TheoryCoder: python theorycoderv2.py --game pong --level-sets \"{'pong': [0]}\"")
    else:
        print("Some tests failed. Check the errors above.")
        print("Make sure you have OCAtari installed: pip install ocatari")
