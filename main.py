from telethon import TelegramClient, events
import pyttsx3
import os
import sys
import time
import pygame
import re

def find_content(search_word):
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    config_file = os.path.join(script_dir, 'config.txt')
    
    try:
        with open(config_file, 'r') as file:
            for line in file:
                if search_word in line:
                    return line.split(search_word, 1)[1].strip()
            print(f"{search_word} Not found in file.")
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found.")
    return None

API_ID = find_content('API_ID: ')
API_HASH = find_content('API_HASH: ')
SESSION_NAME = find_content('SESSION_NAME: ')
TARGET_GROUP_ID = find_content("GROUP_IP: ")

script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
TONES_DIR = os.path.join(script_dir, 'Tones')
KEYWORDS_DIR = os.path.join(script_dir, 'Keywords')

SOUND_FILES = {
    "priority1.txt": os.path.join(TONES_DIR, "tone1.mp3"),
    "priority2.txt": os.path.join(TONES_DIR, "tone2.mp3"),
    "priority3.txt": os.path.join(TONES_DIR, "tone3.mp3"),
    "notone.txt": os.path.join(TONES_DIR, "notone.mp3")
}
DEFAULT_SOUND_FILE = os.path.join(TONES_DIR, "default.mp3")

NO_TONE_CHECK = False

STREET_ABBREVIATIONS = {
    "dr": "drive",
    "st": "street",
    "ave": "avenue",
    "blvd": "boulevard",
    "rd": "road",
    "ln": "lane",
    "ct": "court",
    "pl": "place",
    "sq": "square",
    "n": "north",
    "e": "east",
    "s": "south",
    "w": "west",
    "1a": "first alarm",
    "2a": "second alarm",
    "3a": "third alarm",
    "4a": "fourth alarm"
}

def replace_abbreviations(message_text):
    for abbrev, full_form in STREET_ABBREVIATIONS.items():
        # Match the abbreviation only when it's a whole word (using \b for word boundaries)
        pattern = rf'\b{re.escape(abbrev)}\b'
        message_text = re.sub(pattern, full_form, message_text, flags=re.IGNORECASE)
    return message_text

def find_sound_file_for_keyword(keyword):
    print(f"Searching for keyword: '{keyword}'")
    keyword_lower = keyword.strip().lower()

    for file_name, sound_file in SOUND_FILES.items():
        file_path = os.path.join(KEYWORDS_DIR, file_name)
        print(f"Checking file: {file_name}")
        
        try:
            with open(file_path, 'r') as file:
                keywords = [line.strip().lower() for line in file]
                for line in keywords:
                    if line in keyword_lower:
                        print(f"Found match for '{keyword}' in file: {file_name}")
                        NO_TONE = False
                        if file_name == "notone.txt":
                            NO_TONE = True
                        return sound_file, NO_TONE
        except FileNotFoundError:
            print(f"Keyword file '{file_name}' not found.")
    
    print("No match found, returning default sound.")
    return DEFAULT_SOUND_FILE

pygame.mixer.init()
def play_sound(sound_file):
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except Exception as e:
        print(f"Error playing sound: {e}")

tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', find_content("READ_RATE: "))
tts_engine.setProperty('volume', 1.0)

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

@client.on(events.NewMessage)
async def message_handler(event):
    chat = await event.get_chat()
    chat_id = f"{chat.id}"
    print(f"Received message from chat: {chat_id}")
    if chat_id in TARGET_GROUP_ID:
        message_text = event.raw_text
        message_text = message_text.lower()
        if "live incident notification" in message_text:
            message_text = message_text.replace("live incident notification", "").strip()
        if "pending" in message_text:
            message_text = message_text.replace("pending", "").strip()
        if "-" in message_text:
            message_text = message_text.replace("-", " ").strip()

        sound_file, NO_TONE_CHECK = find_sound_file_for_keyword(message_text.splitlines()[0])
        if not sound_file:
            sound_file = DEFAULT_SOUND_FILE
        play_sound(sound_file)
        time.sleep(0.75)

        message_text = replace_abbreviations(message_text)

        message_reader = f"{find_content('READ_ALOUD: ')}"
        if message_reader != "false" and NO_TONE_CHECK == False:
            tts_engine.say(f"{message_text}")
            tts_engine.runAndWait()

def main():
    os.system('color c')
    os.system('cls' if os.name == 'nt' else 'clear')
    print("LINAS Telegram Reader - Release 1.3")
    print(" ")
    with client:
        client.run_until_disconnected()

if __name__ == '__main__':
    main()
