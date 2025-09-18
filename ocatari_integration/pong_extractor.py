#!/usr/bin/env python3
"""
OCAtari Pong Extractor for TheoryCoder Integration

This script extracts object information from Pong and converts it into
a state representation that TheoryCoder can work with.
"""

import os
import sys
import random
import numpy as np
from PIL import Image
from datetime import datetime
import json
from typing import Dict, List, Any

from ocatari.core import OCAtari


class PongExtractor:
    """Extract and convert Pong game state for TheoryCoder."""
    
    def __init__(self, mode="vision", render_mode='rgb_array'):
        """
        Initialize the Pong extractor.
        
        Args:
            mode: OCAtari mode ("ram" or "vision")
            render_mode: Rendering mode for the environment
        """
        self.mode = mode
        self.render_mode = render_mode
        self.env = None
        self.frame_count = 0
        
    def initialize_env(self):
        """Initialize the OCAtari Pong environment."""
        try:
            self.env = OCAtari("Pong", mode=self.mode, hud=True, render_mode=self.render_mode)
            observation, info = self.env.reset()
            print(f"✅ Pong environment initialized in {self.mode} mode!")
            print(f"🎯 Action space: {self.env.action_space.n} possible actions")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Pong environment: {e}")
            return False
    
    def extract_pong_objects(self, objects):
        """
        Extract Pong-specific objects and convert to structured format.
        
        Args:
            objects: List of detected objects from OCAtari
            
        Returns:
            dict: Structured state representation for TheoryCoder
        """
        state = {
            'player_paddle': [],
            'enemy_paddle': [],
            'ball': [],
            'score_left': [],
            'score_right': [],
            'walls': []
        }
        
        # Debug: print all detected objects
        print(f"🔍 OCAtari detected {len(objects)} objects:")
        for i, obj in enumerate(objects):
            if hasattr(obj, 'category'):
                print(f"  Object {i}: {obj.category} at ({getattr(obj, 'x', 'N/A')}, {getattr(obj, 'y', 'N/A')})")
        
        for obj in objects:
            if hasattr(obj, 'category') and obj.category != "NoObject":
                obj_info = {
                    'x': int(getattr(obj, 'x', 0)),
                    'y': int(getattr(obj, 'y', 0)),
                    'width': int(getattr(obj, 'w', 1)),
                    'height': int(getattr(obj, 'h', 1)),
                }
                obj_info['center_x'] = int(obj_info['x'] + obj_info['width'] // 2)
                obj_info['center_y'] = int(obj_info['y'] + obj_info['height'] // 2)
                
                # Add color if available
                if hasattr(obj, 'rgb'):
                    r, g, b = obj.rgb
                    obj_info['color'] = [int(r), int(g), int(b)]
                
                # Categorize objects based on their type and position
                obj_type = obj.category.lower()
                print(f"  📍 Processing {obj_type} at {obj_info['center_x']}, {obj_info['center_y']}")
                
                # For Pong, we need to handle different object categories
                if 'paddle' in obj_type:
                    # Determine if left or right paddle based on x position
                    if obj_info['x'] < 80:  # Left side of screen
                        state['player_paddle'].append([obj_info['center_x'], obj_info['center_y']])
                        print(f"    ➜ Added to player_paddle")
                    else:  # Right side of screen
                        state['enemy_paddle'].append([obj_info['center_x'], obj_info['center_y']])
                        print(f"    ➜ Added to enemy_paddle")
                        
                elif 'ball' in obj_type:
                    state['ball'].append([obj_info['center_x'], obj_info['center_y']])
                    print(f"    ➜ Added to ball")
                    
                elif obj_type in ['player', 'enemy', 'opponent']:
                    # Some OCAtari versions use 'player' and 'enemy' for paddles
                    if obj_type == 'player':
                        state['player_paddle'].append([obj_info['center_x'], obj_info['center_y']])
                        print(f"    ➜ Added to player_paddle (as player)")
                    else:
                        state['enemy_paddle'].append([obj_info['center_x'], obj_info['center_y']])
                        print(f"    ➜ Added to enemy_paddle (as enemy)")
                        
                elif 'score' in obj_type or 'digit' in obj_type or obj_type.isdigit():
                    # Determine left or right score based on position
                    if obj_info['x'] < 80:
                        state['score_left'].append([obj_info['center_x'], obj_info['center_y']])
                        print(f"    ➜ Added to score_left")
                    else:
                        state['score_right'].append([obj_info['center_x'], obj_info['center_y']])
                        print(f"    ➜ Added to score_right")
                        
                elif 'wall' in obj_type or 'border' in obj_type:
                    state['walls'].append([obj_info['center_x'], obj_info['center_y']])
                    print(f"    ➜ Added to walls")
                else:
                    # For any unrecognized objects, try to categorize by position
                    print(f"    ❓ Unknown object type: {obj_type}")
                    # If it's tall and narrow, might be a paddle
                    if obj_info['height'] > obj_info['width'] * 2:
                        if obj_info['x'] < 80:
                            state['player_paddle'].append([obj_info['center_x'], obj_info['center_y']])
                            print(f"    ➜ Guessed as player_paddle (tall object on left)")
                        else:
                            state['enemy_paddle'].append([obj_info['center_x'], obj_info['center_y']])
                            print(f"    ➜ Guessed as enemy_paddle (tall object on right)")
                    # If it's small and square, might be ball
                    elif abs(obj_info['width'] - obj_info['height']) <= 2:
                        state['ball'].append([obj_info['center_x'], obj_info['center_y']])
                        print(f"    ➜ Guessed as ball (small square object)")
        
        print(f"📊 Final state: {len(state['player_paddle'])} player, {len(state['enemy_paddle'])} enemy, {len(state['ball'])} ball")
        return state
    
    def get_current_state(self):
        """
        Get the current game state in TheoryCoder format.
        
        Returns:
            dict: Current state representation
        """
        if self.env is None:
            raise RuntimeError("Environment not initialized. Call initialize_env() first.")
        
        try:
            # Extract objects from current frame
            raw_objects = self.env.objects
            state = self.extract_pong_objects(raw_objects)
            
            # Add metadata
            state['frame'] = self.frame_count
            state['reward'] = getattr(self.env, '_last_reward', 0)
            state['action_space'] = list(range(self.env.action_space.n))
            
            return state
            
        except Exception as e:
            print(f"❌ Error extracting state: {e}")
            return {}
    
    def step(self, action):
        """
        Take a step in the environment and return the new state.
        
        Args:
            action: Action to take
            
        Returns:
            tuple: (state, reward, done, info)
        """
        if self.env is None:
            raise RuntimeError("Environment not initialized.")
            
        try:
            obs, reward, terminated, truncated, info = self.env.step(action)
            self.frame_count += 1
            
            # Store reward for state extraction
            self.env._last_reward = reward
            
            state = self.get_current_state()
            done = terminated or truncated
            
            return state, reward, done, info
            
        except Exception as e:
            print(f"❌ Error during step: {e}")
            return {}, 0, True, {}
    
    def reset(self):
        """
        Reset the environment and return initial state.
        
        Returns:
            dict: Initial state representation
        """
        if self.env is None:
            if not self.initialize_env():
                return {}
        
        try:
            observation, info = self.env.reset()
            self.frame_count = 0
            self.env._last_reward = 0
            
            return self.get_current_state()
            
        except Exception as e:
            print(f"❌ Error during reset: {e}")
            return {}
    
    def close(self):
        """Close the environment."""
        if self.env is not None:
            self.env.close()
            self.env = None
    
    def save_state_visualization(self, output_dir="pong_debug", max_frames=50):
        """
        Save frames and state data for debugging/visualization.
        
        Args:
            output_dir: Directory to save debug files
            max_frames: Maximum number of frames to capture
        """
        print(f"🎮 Starting Pong state extraction for debugging...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        frames_dir = os.path.join(output_dir, "frames")
        os.makedirs(frames_dir, exist_ok=True)
        
        if not self.initialize_env():
            return
        
        states_file = os.path.join(output_dir, "pong_states.json")
        all_states = []
        
        try:
            # Reset and capture initial state
            initial_state = self.reset()
            all_states.append({
                'frame': 0,
                'action': None,
                'state': initial_state,
                'reward': 0
            })
            
            for frame in range(max_frames):
                # Take random action
                action = random.randint(0, self.env.action_space.n - 1)
                state, reward, done, info = self.step(action)
                
                # Save frame image if possible
                try:
                    rgb_array = self.env.render()
                    if rgb_array is not None and hasattr(rgb_array, 'shape'):
                        if len(rgb_array.shape) == 3 and rgb_array.shape[2] == 3:
                            if rgb_array.dtype != np.uint8:
                                rgb_array = np.clip(rgb_array, 0, 255).astype(np.uint8)
                            
                            image = Image.fromarray(rgb_array)
                            filename = f"frame_{frame:06d}.png"
                            filepath = os.path.join(frames_dir, filename)
                            image.save(filepath)
                except Exception as e:
                    print(f"⚠️  Failed to save frame {frame}: {e}")
                
                # Store state data
                all_states.append({
                    'frame': frame + 1,
                    'action': action,
                    'state': state,
                    'reward': reward
                })
                
                if frame % 10 == 0:
                    print(f"📍 Frame {frame}: Action {action}, Reward {reward}")
                    print(f"   Objects: Ball: {len(state.get('ball', []))}, "
                          f"Player: {len(state.get('player_paddle', []))}, "
                          f"Enemy: {len(state.get('enemy_paddle', []))}")
                
                if done:
                    print(f"🏁 Game ended at frame {frame}. Resetting...")
                    self.reset()
            
            # Save all states to JSON
            with open(states_file, 'w') as f:
                json.dump(all_states, f, indent=2)
            
            print(f"\n🎉 Debug extraction complete!")
            print(f"📁 Files saved in: {output_dir}/")
            print(f"   📄 States: {os.path.basename(states_file)}")
            print(f"   🖼️  Frames: {frames_dir}/ ({max_frames} images)")
            
        finally:
            self.close()


def test_pong_extraction():
    """Test function to validate Pong extraction."""
    print("🚀 Testing Pong Extraction for TheoryCoder")
    print("=" * 50)
    
    extractor = PongExtractor(mode="ram")
    
    # Test basic functionality
    if extractor.initialize_env():
        print("\n🧪 Testing basic state extraction...")
        
        # Test reset
        initial_state = extractor.reset()
        print(f"Initial state keys: {list(initial_state.keys())}")
        
        # Test a few steps
        for i in range(5):
            action = random.randint(0, extractor.env.action_space.n - 1)
            state, reward, done, info = extractor.step(action)
            print(f"Step {i+1}: Action {action}, Reward {reward}")
            print(f"  Ball positions: {state.get('ball', [])}")
            print(f"  Player paddle: {state.get('player_paddle', [])}")
            print(f"  Enemy paddle: {state.get('enemy_paddle', [])}")
        
        extractor.close()
        print("\n✅ Basic test completed successfully!")
        
        # Run debug visualization
        print("\n🎬 Running debug visualization...")
        debug_extractor = PongExtractor(mode="ram")
        debug_extractor.save_state_visualization(max_frames=20)
        
    else:
        print("❌ Failed to initialize environment for testing.")


if __name__ == "__main__":
    test_pong_extraction()
