import os
import shutil
import subprocess

def convert_webp_to_mp4(webp_path, output_path, fps=10):
    if not os.path.exists(webp_path):
        print(f"Error: {webp_path} not found.")
        return

    # Create temp directory
    temp_dir = "temp_frames"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    try:
        print("Extracting and coalescing frames using ImageMagick...")
        # Use magick to coalesce frames (reconstruct full frames from deltas)
        # And output as a sequence of PNGs
        # frame_%04d.png tells magick to number them.
        output_pattern = os.path.join(temp_dir, "frame_%04d.png")
        
        # Try 'magick' first, then 'convert'
        magick_cmd = "magick"
        if shutil.which("magick") is None:
            magick_cmd = "convert"
            if shutil.which("convert") is None:
                 print("Error: ImageMagick (magick or convert) is not found.")
                 return

        cmd_extract = [
            magick_cmd,
            webp_path,
            "-coalesce",
            output_pattern
        ]
        
        print(f"Running: {' '.join(cmd_extract)}")
        res = subprocess.run(cmd_extract, capture_output=True)
        if res.returncode != 0:
            print("Failed to extract frames.")
            print(res.stderr.decode())
            return

        # Check if frames exist
        frames = sorted([f for f in os.listdir(temp_dir) if f.endswith(".png")])
        if not frames:
            print("No frames extracted.")
            return

        print(f"Extracted {len(frames)} frames.")

        # Convert to MP4 using ffmpeg
        # -y to overwrite
        cmd = [
            "ffmpeg",
            "-y",
            "-framerate", str(fps),
            "-i", output_pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            # Ensure dimensions are even
            "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2",
            output_path
        ]

        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Successfully created {output_path}")
        else:
            print("ffmpeg failed:")
            print(result.stderr)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        webp_source = sys.argv[1]
    else:
        webp_source = "recording.webp"

    if len(sys.argv) > 2:
        mp4_target = sys.argv[2]
    else:
        mp4_target = "game_progression.mp4"

    # Default FPS 5
    convert_webp_to_mp4(webp_source, mp4_target, fps=5)
