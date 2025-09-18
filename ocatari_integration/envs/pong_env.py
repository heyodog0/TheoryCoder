#!/usr/bin/env python3
"""
Pong Environment Wrapper for TheoryCoder

This wrapper integrates OCAtari Pong with TheoryCoder's interface,
converting object detection into a structured state representation.
"""

import numpy as np
import random
from typing import Dict, List, Any, Tuple
import sys
import os

# Add the parent directory to the path to import the extractor
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from pong_extractor import PongExtractor


class PongEnv:
    """
    Pong environment wrapper for TheoryCoder integration.
    
    This class provides a consistent interface that TheoryCoder expects,
    while using OCAtari for object detection and state representation.
    """
    
    def __init__(self, level_set="default", level_id=0):
        """
        Initialize the Pong environment.
        
        Args:
            level_set: Level set identifier (for compatibility with TheoryCoder)
            level_id: Level identifier (for compatibility with TheoryCoder)
        """
        self.level_set = level_set
        self.level_id = level_id
        
        # Initialize the OCAtari extractor
        self.extractor = PongExtractor(mode="ram")
        
        # Frame and coordinate capture
        self.capture_frames = True
        self.frames_dir = f"pong_frames_{level_set}_{level_id}"
        self.coords_file = f"pong_coords_{level_set}_{level_id}.txt"
        self.frame_counter = 0
        # Capture every frame unless changed
        self.capture_stride = 1
        self._frames_since_capture = 0
        
        if self.capture_frames:
            import os
            os.makedirs(self.frames_dir, exist_ok=True)
            # Initialize coordinate log file
            with open(self.coords_file, 'w') as f:
                f.write(f"# Pong Object Coordinates - Level {level_set}-{level_id}\n")
                f.write(f"# Format: frame_number,image_file,object_type,x,y,width,height,center_x,center_y\n")
                f.write("\n")
        
        # Define action space (Pong actions)
        # 0: NOOP, 1: FIRE, 2: RIGHT, 3: LEFT, 4: RIGHTFIRE, 5: LEFTFIRE
        self.actions_set = ["noop", "fire", "right", "left", "rightfire", "leftfire"]
        
        # Game state tracking
        self.current_state = {}
        self.previous_state = {}
        self.won = False
        self.lost = False
        self.episode_reward = 0
        self.step_count = 0
        self.max_steps = 1000  # Prevent infinite episodes
        
        # Score tracking for win/loss conditions
        self.player_score = 0
        self.enemy_score = 0
        self.max_score = 5  # Game ends when someone reaches this score
        
        print(f"🎮 Initialized Pong environment (Level {level_set}-{level_id})")
    
    def reset(self):
        """
        Reset the environment to initial state.
        
        Returns:
            dict: Initial game state
        """
        try:
            # Reset the extractor and get initial state
            self.current_state = self.extractor.reset()
            self.previous_state = {}
            
            # Reset game tracking variables
            self.won = False
            self.lost = False
            self.episode_reward = 0
            self.step_count = 0
            self.player_score = 0
            self.enemy_score = 0
            
            # Ensure we have a valid state
            if not self.current_state:
                self.current_state = self._create_empty_state()
            
            # Kick off the game by pressing FIRE until ball/enemy appears
            try:
                self._kickoff_if_needed(max_steps=60)
            except AttributeError:
                # Fallback: if helper not available, press FIRE a few times
                for _ in range(10):
                    _state, _rew, _done, _info = self.step('fire')
                    if _done:
                        break
            print(f"🔄 Environment reset - Step {self.step_count}")
            return self.get_obs()
            
        except Exception as e:
            print(f"❌ Error during reset: {e}")
            self.current_state = self._create_empty_state()
            return self.current_state.copy()
    
    def step(self, action):
        """
        Take a step in the environment.
        
        Args:
            action: Action to take (can be string or int)
            
        Returns:
            tuple: (observation, reward, done, info)
        """
        try:
            # Normalize alias from some planners
            if action == 'no-op':
                action = 'noop'

            # Convert action to integer if it's a string
            if isinstance(action, str):
                if action in self.actions_set:
                    action_idx = self.actions_set.index(action)
                else:
                    print(f"⚠️  Unknown action '{action}', using NOOP")
                    action_idx = 0
            else:
                action_idx = int(action)
            
            # Ensure action is within valid range
            action_idx = max(0, min(action_idx, len(self.actions_set) - 1))
            
            # Store previous state
            self.previous_state = self.current_state.copy()
            
            # Take step in OCAtari environment
            state, reward, done, info = self.extractor.step(action_idx)
            
            # Update current state
            self.current_state = state if state else self._create_empty_state()
            
            # Capture frame and coordinates
            if self.capture_frames:
                self._save_frame_and_coords(action)
            
            # Update tracking variables
            self.step_count += 1
            self.episode_reward += reward
            
            # Update scores and check win/loss conditions
            self._update_scores_and_status(reward, done)
            
            # Check for episode termination
            done = done or self.won or self.lost or (self.step_count >= self.max_steps)
            
            return self.current_state.copy(), reward, done, info
            
        except Exception as e:
            print(f"❌ Error during step: {e}")
            # Return safe defaults
            self.current_state = self._create_empty_state()
            return self.current_state.copy(), 0, True, {}
    
    def get_obs(self):
        """
        Get current observation/state.
        
        Returns:
            dict: Current game state
        """
        return self.current_state.copy()
    
    # Compatibility alias for callers expecting this name
    def get_current_state(self):
        return self.get_obs()
    
    def close(self):
        """Close the environment and clean up resources."""
        try:
            self.extractor.close()
            print("🔒 Pong environment closed")
        except Exception as e:
            print(f"⚠️  Error closing environment: {e}")
    
    def _create_empty_state(self):
        """
        Create an empty state when initialization fails.
        
        Returns:
            dict: Empty state with required keys
        """
        return {
            'player_paddle': [],
            'enemy_paddle': [],
            'ball': [],
            'score_left': [],
            'score_right': [],
            'walls': [],
            'frame': 0,
            'reward': 0,
            'action_space': list(range(len(self.actions_set)))
        }
    
    def _update_scores_and_status(self, reward, done):
        """
        Update score tracking and win/loss status.
        
        Args:
            reward: Reward from the last action
            done: Whether the episode is done from OCAtari
        """
        # In Pong, positive reward typically means player scored
        # Negative reward means opponent scored
        if reward > 0:
            self.player_score += 1
        elif reward < 0:
            self.enemy_score += 1
        
        # Check win conditions
        if self.player_score >= self.max_score:
            self.won = True
            print(f"🏆 Player wins! Final score: {self.player_score}-{self.enemy_score}")
        elif self.enemy_score >= self.max_score:
            self.lost = True
            print(f"💀 Player lost! Final score: {self.player_score}-{self.enemy_score}")
        
        # Emergency termination for very long episodes
        if self.step_count >= self.max_steps:
            print(f"⏰ Episode terminated due to max steps ({self.max_steps})")
            # Determine winner based on current score
            if self.player_score > self.enemy_score:
                self.won = True
            elif self.enemy_score > self.player_score:
                self.lost = True
            # If tied, neither won nor lost
    
    def get_state_summary(self):
        """
        Get a human-readable summary of the current state.
        
        Returns:
            str: State summary
        """
        state = self.current_state
        summary = f"Frame {state.get('frame', 0)}: "
        summary += f"Ball: {len(state.get('ball', []))} "
        summary += f"Player: {len(state.get('player_paddle', []))} "
        summary += f"Enemy: {len(state.get('enemy_paddle', []))} "
        summary += f"Score: {self.player_score}-{self.enemy_score} "
        summary += f"Steps: {self.step_count}"
        return summary
    
    def _save_frame_and_coords(self, action):
        """
        Save current frame and object coordinates.
        
        Args:
            action: Action taken this step
        """
        try:
            import numpy as np
            from PIL import Image
            
            # Save frame image
            self._frames_since_capture = (self._frames_since_capture + 1) % self.capture_stride
            do_capture = (self._frames_since_capture == 0)
            if hasattr(self.extractor, 'env') and self.extractor.env is not None:
                try:
                    if do_capture:
                        rgb_array = self.extractor.env.render()
                        if rgb_array is not None and hasattr(rgb_array, 'shape'):
                            if len(rgb_array.shape) == 3 and rgb_array.shape[2] == 3:
                                if rgb_array.dtype != np.uint8:
                                    rgb_array = np.clip(rgb_array, 0, 255).astype(np.uint8)
                                
                                image = Image.fromarray(rgb_array)
                                filename = f"frame_{self.frame_counter:06d}.png"
                                filepath = os.path.join(self.frames_dir, filename)
                                image.save(filepath)
                            else:
                                filename = f"frame_{self.frame_counter:06d}_failed.png"
                        else:
                            filename = f"frame_{self.frame_counter:06d}_failed.png"
                    else:
                        filename = f"frame_{self.frame_counter:06d}_skipped.png"
                except Exception as e:
                    print(f"⚠️  Failed to save frame {self.frame_counter}: {e}")
                    filename = f"frame_{self.frame_counter:06d}_failed.png"
            else:
                filename = f"frame_{self.frame_counter:06d}_no_env.png"
            
            # Log coordinates
            with open(self.coords_file, 'a') as f:
                # Write frame header
                f.write(f"# Frame {self.frame_counter}, Action: {action}, Step: {self.step_count}\n")
                
                # Write object coordinates
                state = self.current_state
                objects_logged = 0
                
                # Log player paddle
                for i, pos in enumerate(state.get('player_paddle', [])):
                    if len(pos) >= 2:
                        f.write(f"{self.frame_counter},{filename},player_paddle,{pos[0]},{pos[1]},10,30,{pos[0]},{pos[1]}\n")
                        objects_logged += 1
                
                # Log enemy paddle  
                for i, pos in enumerate(state.get('enemy_paddle', [])):
                    if len(pos) >= 2:
                        f.write(f"{self.frame_counter},{filename},enemy_paddle,{pos[0]},{pos[1]},10,30,{pos[0]},{pos[1]}\n")
                        objects_logged += 1
                
                # Log ball
                for i, pos in enumerate(state.get('ball', [])):
                    if len(pos) >= 2:
                        f.write(f"{self.frame_counter},{filename},ball,{pos[0]},{pos[1]},4,4,{pos[0]},{pos[1]}\n")
                        objects_logged += 1
                
                # Log scores
                for i, pos in enumerate(state.get('score_left', [])):
                    if len(pos) >= 2:
                        f.write(f"{self.frame_counter},{filename},score_left,{pos[0]},{pos[1]},8,8,{pos[0]},{pos[1]}\n")
                        objects_logged += 1
                
                for i, pos in enumerate(state.get('score_right', [])):
                    if len(pos) >= 2:
                        f.write(f"{self.frame_counter},{filename},score_right,{pos[0]},{pos[1]},8,8,{pos[0]},{pos[1]}\n")
                        objects_logged += 1
                
                # If no objects found, still log the frame
                if objects_logged == 0:
                    f.write(f"{self.frame_counter},{filename},NoObjects,,,,,,,\n")
            
            self.frame_counter += 1
            
        except Exception as e:
            print(f"⚠️  Error saving frame/coords: {e}")

    def _kickoff_if_needed(self, max_steps: int = 20):
        """Press FIRE a few times until ball/enemy appears so the game starts."""
        try:
            for _ in range(max_steps):
                # get_current_state isn't a public API; use current_state
                state = self.current_state if self.current_state else self.get_obs()
                ball_present = len(state.get('ball', [])) > 0
                enemy_present = len(state.get('enemy_paddle', [])) > 0
                if ball_present or enemy_present:
                    break
                # Press FIRE to start/serve
                _state, _rew, _done, _info = self.step('fire')
                if _done:
                    self.extractor.reset()
        except Exception as e:
            print(f"⚠️  Kickoff failed: {e}")

    def save_debug_info(self, output_dir="pong_debug"):
        """
        Save debug information about the current session.
        
        Args:
            output_dir: Directory to save debug files
        """
        try:
            self.extractor.save_state_visualization(output_dir=output_dir, max_frames=30)
        except Exception as e:
            print(f"⚠️  Failed to save debug info: {e}")


def test_pong_env():
    """Test the Pong environment wrapper."""
    print("🧪 Testing Pong Environment Wrapper")
    print("=" * 40)
    
    # Create environment
    env = PongEnv(level_set="test", level_id=0)
    
    try:
        # Test reset
        print("\n🔄 Testing reset...")
        state = env.reset()
        print(f"Initial state keys: {list(state.keys())}")
        print(f"State summary: {env.get_state_summary()}")
        
        # Test a few steps
        print("\n🎮 Testing steps...")
        for i in range(10):
            action = random.choice(env.actions_set)
            state, reward, done, info = env.step(action)
            
            print(f"Step {i+1}: Action '{action}', Reward {reward}, Done {done}")
            print(f"  {env.get_state_summary()}")
            
            if done:
                print(f"🏁 Episode ended after {i+1} steps")
                break
        
        print(f"\n📊 Final Statistics:")
        print(f"  Total steps: {env.step_count}")
        print(f"  Total reward: {env.episode_reward}")
        print(f"  Won: {env.won}, Lost: {env.lost}")
        print(f"  Final score: {env.player_score}-{env.enemy_score}")
        
    finally:
        env.close()
    
    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_pong_env()
