import socket
import os
import requests
import time
import csv
from collections import Counter
import re
from pynput import keyboard
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
NICK = os.getenv("TWITCH_NICK")
CHAN = os.getenv("TWITCH_CHANNEL")
PASS = os.getenv("TWITCH_TOKEN")

# -------------------------------
# Global pause variables and Key press callback
# -------------------------------
paused = False
match_phase = 1  # 1 = First Half, 2 = Second Half
match_start_time = 0
second_half_start_time = 0

def on_press(key):
    global paused, match_phase, second_half_start_time
    try:
        if key.char == 'p':
            if not paused:
                paused = True
                print("HALFTIME / PAUSE TRIGGERED")
                with open('pulse_data.csv', 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['HT', 0, '', time.time(), 'HALFTIME'])
            else:
                paused = False
                match_phase = 2
                second_half_start_time = time.time()
                print("SECOND HALF RESUMED - Clock set to 46'")
        elif key.char == 'q':
            with open('pulse_data.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['FT', 0, '', time.time(), 'Full Time'])
            print("GAME OVER")
            os._exit(0)
    except AttributeError:
        pass

# -------------------------------
# Main Function
# -------------------------------
def main():
    global match_start_time
    
    # -------------------------------
    # Connect to Twitch IRC server
    # -------------------------------
    s = socket.socket()
    s.connect(("irc.chat.twitch.tv", 6667))
    s.send(f"PASS {PASS}\r\n".encode("utf-8"))
    s.send(f"NICK {NICK}\r\n".encode("utf-8"))
    s.send(f"JOIN {CHAN}\r\n".encode("utf-8"))
    s.recv(2048) # Initial server message

    print(f"Connected to {CHAN}. . Ready to track.")
    input("PRESS ENTER WHEN THE GAME STARTS") 
    match_start_time = time.time()
    last_check_time = match_start_time
   


    # -------------------------------
    # Message counting and trending
    # -------------------------------
    message_count = 0
    word_counts = Counter()

    # -------------------------------
    # Stop words and bot filter
    # -------------------------------
    stop_words = {"the", "a", "and", "is", "in", "it", "to", "of", "i", "this", "that", "all", "you"}
    bot_blocklist = {"streamelements", "nightbot", "moobot", "caseoh_bot"}

    # -------------------------------
    # Initialize CSV file
    # -------------------------------
    with open('pulse_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Minute', 'Buzz', 'Trending', 'Timestamp', 'Status'])# Header for CSV file

    # -------------------------------
    # Start the keyboard listener
    # -------------------------------
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    # -------------------------------
    # Main loop
    # -------------------------------
    while True:
        # -------------------------------
        # Receive and process chat messages
        # -------------------------------
        response = s.recv(2048).decode("utf-8")
        
        if response.startswith("PING"):
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        elif "PRIVMSG" in response:
            try:
                user_part = response.split("!")[0] # Gets username and removes colon and makes it lowercase 
                username = user_part[1:].lower()   
            except:
                username = "unknown"

            if not paused:
                if username not in bot_blocklist:    
                    message_count += 1 

                    # Extract the message text
                    parts = response.split(":", 2)
                    if len(parts) > 2:
                        message_text = parts[2].lower()
                        # Clean the text (remove punctuation)
                        clean_words = re.findall(r'\b\w+\b', message_text)
                        for word in clean_words:
                            if word not in stop_words and len(word) > 2:
                                word_counts[word] += 1


        # -------------------------------
        # Every minute write summary to CSV
        # -------------------------------
        current_time = time.time()

        if not paused and (current_time - last_check_time >= 1):

            # Determine status 
            if paused:
                status = "HALFTIME"
            elif match_phase == 2:
                status = "Second Half"
            else:
                status = "First Half"

            # 1. Determine the "Soccer Minute" string
            if match_phase == 1:
                elapsed_min = int((current_time - match_start_time) // 1)
                if elapsed_min >= 45:
                    stoppage = elapsed_min - 45
                    match_minute = f"45+{stoppage}" if stoppage > 0 else "45"
                else:
                    match_minute = elapsed_min
            else:
                # Starts at 46 and counts up from the moment 'p' was unpaused
                elapsed_sh = int((current_time - second_half_start_time) // 1)
                display_min = 46 + elapsed_sh
                if display_min >= 90:
                    stoppage = display_min - 90
                    match_minute = f"90+{stoppage}" if stoppage > 0 else "90"
                else:
                    match_minute = display_min


            # 2. Get Trending Data
            top_words = [word for word, count in word_counts.most_common(5)]
            trending_str = ",".join(top_words)


            # 3. Save to CSV
            with open('pulse_data.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([match_minute, message_count, trending_str, current_time, status])

            print(f"Minute {match_minute} | Buzz: {message_count} messages/min | Status: {status}")

            # Reset counters for the next minute
            message_count = 0
            word_counts.clear()
            last_check_time = current_time

# -------------------------------
# Execution
# -------------------------------
if __name__ == "__main__":
    main()