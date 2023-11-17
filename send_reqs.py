import threading
import queue
import requests

def send_requests(url, num_requests, response_queue):
    for i in range(num_requests):
        response = requests.get(url)
        response_queue.put((i + 1, response.text))
        print("Sent request ",i+1)

def process_responses(response_queue):
    while True:
        result = response_queue.get()
        print(f"Received response {result[0]}")

if __name__ == "__main__":
    target_url = "https://example.com"
    num_requests = 10  # Change this to the desired number of requests

    # Create a thread-safe queue for communication between threads
    response_queue = queue.Queue()

    # Create a thread for sending requests
    send_thread = threading.Thread(target=send_requests, args=(target_url, num_requests, response_queue))

    # Create a thread for processing responses
    process_thread = threading.Thread(target=process_responses, args=(response_queue,))

    # Start both threads
    send_thread.start()
    process_thread.start()

    # Wait for both threads to finish
    send_thread.join()
    process_thread.join()
