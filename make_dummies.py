import os
from moviepy import ColorClip

os.makedirs("final_videos", exist_ok=True)
ids = ["TEST_ADOPTED_D3_final", "TEST_ADOPTED_D2_final", "TEST_ADOPTED_D1_final"]
for vid_id in ids:
    path = f"final_videos/{vid_id}.mp4"
    clip = ColorClip(size=(720, 1280), color=(0, 0, 0), duration=1)
    clip.write_videofile(path, fps=24, codec="libx264", logger=None)
    print(f"Created {path}")
