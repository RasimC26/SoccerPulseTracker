import socket
import os
import requests
import time
import csv
from collections import Counter
import re
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
NICK = os.getenv("TWITCH_NICK")
CHAN = os.getenv("TWITCH_CHANNEL")
PASS = os.getenv("TWITCH_TOKEN")


def main():

    # Connect to server and authenticate
    s = socket.socket()
    s.connect(("irc.chat.twitch.tv", 6667))
    s.send(f"PASS {PASS}\r\n".encode("utf-8"))
    s.send(f"NICK {NICK}\r\n".encode("utf-8"))
    s.send(f"JOIN {CHAN}\r\n".encode("utf-8"))

    print(f"Connected to {CHAN}. . Ready to track.")
    input("PRESS ENTER WHEN THE GAME STARTS") 
    match_start_time = time.time()

    s.recv(2048)

    # counters
    message_count = 0
    word_counts = Counter()
    last_check_time = time.time()

    # common words to filter out of word count
    stop_words = {"the", "a", "and", "is", "in", "it", "to", "of", "i", "this", "that", "all", "you"}

    # bots to filter out
    bot_blocklist = {"streamelements", "nightbot", "moobot", "caseoh_bot"}

    # Prepare CSV file
    with open('pulse_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Minute', 'Buzz', 'Trending'])# Header for CSV file

    while True:
        # Listens for data
        response = s.recv(2048).decode("utf-8")
        
        if response.startswith("PING"):
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        elif "PRIVMSG" in response:
            try:
                user_part = response.split("!")[0] # Gets username and removes colon and makes it lowercase 
                username = user_part[1:].lower()   
            except:
                username = "unknown"

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

        # Check if 1 min has passed
        current_time = time.time()
        if current_time - last_check_time >= 60:    

            # Get the top 5 most used words this minute
            top_words = [word for word, count in word_counts.most_common(5)]
            trending_str = ",".join(top_words)

            elapsed_seconds = int(current_time - match_start_time)
            match_minute = elapsed_seconds // 60

            # Save the "Pulse" to our CSV
            with open('pulse_data.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([match_minute, message_count, trending_str])
            
            print(f"Minute {match_minute} | Pulse: {message_count} messages/min") 
            
            # Reset for the time measurement and reset top words for that minute 
            message_count = 0
            last_check_time = current_time
            word_counts.clear()

if __name__ == "__main__":
    main()