import socket
import os
import requests
import time
import csv
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
    last_check_time = time.time()

    # Prepare CSV file
    with open('pulse_data.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'message-count']) # Header for CSV file

    while True:
        # Listens for data
        response = s.recv(2048).decode("utf-8")
        
        if response.startswith("PING"):
            s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
        elif "PRIVMSG" in response:
            message_count += 1 

        # Check if 1 min has passed
        current_time = time.time()
        if current_time - last_check_time >= 60:

            elapsed_seconds = int(current_time - match_start_time)
            match_minute = elapsed_seconds // 60

            # Save the "Pulse" to our CSV
            with open('pulse_data.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([match_minute, message_count])
            
            print(f"Minute {match_minute} | Pulse: {message_count} messages/min") 
            
            # Reset for the time measurement 
            message_count = 0
            last_check_time = current_time

if __name__ == "__main__":
    main()