from piano_transcription_inference import PianoTranscription, sample_rate
from PIL import Image, ImageDraw, ImageFont
from synthviz import create_video
import subprocess
import librosa
import shutil
import random
import os


title = ""
desc = ""
video_id = ""


def get_video():
    global title, desc
    with open('./assets/songs.txt') as f:
        adjectives = ["Epic", "Beautiful", "Enchanting", "Majestic", "Breathtaking", "Legendary", "Mythical",
                      "Grandiose", "Ethereal", "Transcendent", "Serene", "Melancholic", "Blissful", "Exquisite",
                      "Radiant", "Heavenly", "Harmonious", "Graceful", "Sublime", "Grandiloquent", "Heroic", "Grand",
                      "Impressive"]
        chosen_adj = random.choice(adjectives)
        fl = f.readline()
        yt_vid = fl[fl.find("https://www.youtube.com/watch?v=") + len("https://www.youtube.com/watch?v="):fl.rfind(" [")]
        print(yt_vid)
        title = fl[fl.find(" [") + 2:fl.find("]")] + f" | {chosen_adj} Piano Cover"
        desc = f"Subscribe to MeloVybs for more {chosen_adj.lower()} piano covers!\n\nThis video was auto generated using AI and Python. Code here: https://github.com/Dheirya"
        make_video(yt_vid)
    print(f"Finished making video called {title}: https://youtu.be/{video_id}")


def make_video(yt_vid):
    cmd_str = f'youtube-dl --extract-audio --audio-format mp3 -o "{yt_vid}.%(ext)s" {yt_vid}'
    subprocess.run(cmd_str, shell=True)
    audio_input = f'{yt_vid}.mp3'
    midi_intermediate_filename = f'{yt_vid}.mid'
    video_filename = f'{yt_vid}.mp4'
    filename = video_filename
    transcriptor = PianoTranscription(device='cpu', checkpoint_path=None)
    audio, _ = librosa.core.load(str(audio_input), sr=sample_rate)
    transcriptor.transcribe(audio, midi_intermediate_filename)
    create_video(input_midi=midi_intermediate_filename, video_filename=video_filename, image_width=1280, image_height=720)
    shutil.rmtree('./video_frames')
    os.remove(f'./{yt_vid}.wav')
    os.remove(f'./{yt_vid}.mp3')
    os.remove(f'./{yt_vid}.mid')
    upload_video(filename)


def upload_video(filename):
    global video_id
    cmd_str = f'python upload.py --noauth_local_webserver --file="./{filename}" --title="{title}" --description="{desc}"'
    video_id = subprocess.run(cmd_str, shell=True, capture_output=True, text=True).stdout.strip("\n")
    os.remove(f'./{filename}')
    remove_line()
    create_thumbnail()


def remove_line():
    source_file = open('./assets/songs.txt', 'r')
    source_file.readline()
    target_file = open('./assets/songs.txt', 'w')
    shutil.copyfileobj(source_file, target_file)


def create_thumbnail():
    title_only = title.split(" - ")[0].strip()
    thumbnail = Image.new("RGB", (1280, 720), (75, 105, 177))
    draw = ImageDraw.Draw(thumbnail)
    piano_keys_image = Image.open("./assets/piano.png")
    aspect_ratio = piano_keys_image.width / piano_keys_image.height
    piano_height_new = int(720 * 0.8)
    piano_width_new = int(piano_height_new * aspect_ratio)
    piano_keys_image = piano_keys_image.resize((piano_width_new, piano_height_new))
    available_height = 720 - piano_height_new + 25
    max_font_size = int(1280 * 0.105)
    piano_x = int((1280 - piano_width_new) / 2)
    thumbnail.paste(piano_keys_image, (piano_x, available_height))
    title_font = ImageFont.truetype("./assets/budmo jiggler.otf", max_font_size)
    title_width, title_height = draw.textsize(title_only, font=title_font)
    title_y = int((available_height - title_height) / 3.5)
    while title_width > 1280:
        max_font_size -= 10
        title_font = ImageFont.truetype("./assets/budmo jiggler.otf", max_font_size)
        title_width, title_height = draw.textsize(title_only, font=title_font)
        title_y = int((available_height - title_height) / 2)
    title_x = int((1280 - title_width) / 2)
    draw.text((title_x, title_y), title_only, font=title_font, fill="white")
    thumbnail.save("thumb.png")
    upload_thumbnail()


def upload_thumbnail():
    cmd_str = f'python upload_thumbnail.py --noauth_local_webserver --video-id="{video_id}" --file="./thumb.png"'
    subprocess.run(cmd_str, shell=True)
    os.remove('./thumb.png')


if __name__ == '__main__':
    print("Starting Uploading Process...")
    get_video()
