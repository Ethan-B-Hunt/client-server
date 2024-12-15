import socket
import threading
import json
import time
from datetime import datetime
import random

# Global Variables
LOG_FILE = "chat_logs.txt"
MAX_CONNECTIONS = 5
active_connections = 0

# Chatbot database
CHAT_RESPONSES = {
    "hello": "Hi there! How can I assist you today?",
    "time": lambda: f"The current time is {datetime.now().strftime('%H:%M:%S')}.",
    "date": lambda: f"Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
    "joke": lambda: random.choice([
        "Why don’t skeletons fight each other? They don’t have the guts.",
        "I told my wife she was drawing her eyebrows too high. She looked surprised.",
        "What do you call fake spaghetti? An impasta."
    ]),
    "help": "You can ask me about the time, date, or even for a joke. Just say hello to start!"
}

# Maintain client contexts
CLIENT_CONTEXTS = {}

def log_conversation(client_address, message, response):
    """Log conversation to a file."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {client_address}: {message} -> {response}\n")

def generate_response(client_id, message):
    """Generate a server response based on the client request."""
    global CLIENT_CONTEXTS

    # Ensure client has a context
    if client_id not in CLIENT_CONTEXTS:
        CLIENT_CONTEXTS[client_id] = {"history": []}

    # Process the message
    message_lower = message.lower()

    if message_lower in CHAT_RESPONSES:
        response = CHAT_RESPONSES[message_lower]
        if callable(response):
            response = response()
    else:
        response = f"I don't know how to respond to '{message}'. Try asking for help."

    # Update context
    CLIENT_CONTEXTS[client_id]["history"].append({"message": message, "response": response})
    return response

def handle_client(client_socket, client_address):
    """Handle communication with a single client."""
    global active_connections
    active_connections += 1
    client_id = f"{client_address[0]}:{client_address[1]}"
    print(f"New connection from {client_id}. Active connections: {active_connections}/{MAX_CONNECTIONS}")

    try:
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Process message and generate response
            message = json.loads(data)["message"]
            response = generate_response(client_id, message)

            # Log the conversation
            log_conversation(client_address, message, response)

            # Send response
            client_socket.send(json.dumps({"response": response}).encode())

            if message.lower() == "bye":
                break
    except Exception as e:
        print(f"Error with client {client_id}: {e}")
    finally:
        active_connections -= 1
        client_socket.close()
        print(f"Connection with {client_id} closed. Active connections: {active_connections}/{MAX_CONNECTIONS}")

def start_server():
    """Start the server and listen for connections."""
    global active_connections

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server_socket.bind(("localhost", 12345))
        server_socket.listen(MAX_CONNECTIONS)
        print("Server is running on localhost:12345")

        while True:
            client_socket, client_address = server_socket.accept()

            if active_connections >= MAX_CONNECTIONS:
                client_socket.send(json.dumps({"response": "Server is full. Try again later."}).encode())
                client_socket.close()
                continue

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.start()

    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_socket.close()
        print("Server shut down.")

if __name__ == "__main__":
    # Clear previous logs
    open(LOG_FILE, "w").close()
    start_server()
