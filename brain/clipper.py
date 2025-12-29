import subprocess
import os


def cut_clips(video_path: str, clips_data: dict, output_dir: str = "output"):
    """
    video_path: path to input video
    clips_data: dict with key "clips" containing start/end timestamps
    output_dir: folder to save clips
    """

    os.makedirs(output_dir, exist_ok=True)

    for idx, clip in enumerate(clips_data["clips"], start=1):
        start = clip["start"]
        end = clip["end"]

        output_path = os.path.join(output_dir, f"clip_{idx}.mp4")

        command = [
            "ffmpeg",
            "-y",                     # overwrite if exists
            "-i", video_path,
            "-ss", start,
            "-to", end,
            "-c", "copy",
            output_path
        ]

        print(f"Creating clip {idx}: {start} → {end}")
        subprocess.run(command, check=True)

    print("All clips created successfully.")
