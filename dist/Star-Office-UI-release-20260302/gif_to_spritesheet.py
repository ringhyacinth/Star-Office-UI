#!/usr/bin/env python3
"""Convert GIF animation to sprite sheet for Phaser"""

from PIL import Image
import os

def gif_to_spritesheet(gif_path, output_path, target_height=64):
    # Open the GIF
    gif = Image.open(gif_path)
    
    # Get all frames
    frames = []
    try:
        while True:
            frame = gif.copy().convert('RGBA')
            # Calculate scale to fit target_height
            original_width, original_height = frame.size
            if original_height != target_height:
                scale = target_height / original_height
                target_width = int(original_width * scale)
                frame = frame.resize((target_width, target_height), Image.Resampling.NEAREST)
            frames.append(frame)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    
    if not frames:
        raise ValueError("No frames found in GIF")
    
    # Calculate sprite sheet dimensions
    frame_width, frame_height = frames[0].size
    num_frames = len(frames)
    
    # Arrange frames in a single row for simplicity
    sheet_width = frame_width * num_frames
    sheet_height = frame_height
    
    # Create sprite sheet
    spritesheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    
    # Paste each frame
    for i, frame in enumerate(frames):
        x = i * frame_width
        y = 0
        spritesheet.paste(frame, (x, y))
    
    # Save sprite sheet
    spritesheet.save(output_path)
    
    print(f"Sprite sheet created: {output_path}")
    print(f"Frames: {num_frames}")
    print(f"Frame size: {frame_width}x{frame_height}")
    print(f"Sprite sheet size: {sheet_width}x{sheet_height}")
    
    return {
        'num_frames': num_frames,
        'frame_width': frame_width,
        'frame_height': frame_height,
        'sheet_width': sheet_width,
        'sheet_height': sheet_height
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Usage: python gif_to_spritesheet.py <gif_path> <output_path> <target_height>")
        print("Example: python gif_to_spritesheet.py star-idle.gif star-idle-spritesheet.png 64")
        sys.exit(1)
    
    gif_path = sys.argv[1]
    output_path = sys.argv[2]
    target_height = int(sys.argv[3])
    
    result = gif_to_spritesheet(gif_path, output_path, target_height=target_height)
    print("\nDone!")
