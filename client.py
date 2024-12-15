import socket
import json

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect(("localhost", 12345))
        print("Connected to the server.")
        print("Type your message and press Enter. Type 'bye' to exit.")

        while True:
            # Get user input
            message = input("You: ")

            # Send message to the server
            client_socket.send(json.dumps({"message": message}).encode())

            # Receive response from the server
            response_data = client_socket.recv(1024).decode()
            response = json.loads(response_data)["response"]
            print(f"Server: {response}")

            if message.lower() == "bye":
                break
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        print("Disconnected from the server.")

if __name__ == "__main__":
    main()
