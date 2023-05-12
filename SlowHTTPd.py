#!/usr/bin/env python3
# Robert Sturzbecher 2025-05-11

# A HTTP server to punish bots, 
# it will slowly reply to a HTTP GET request at a rate of 10 random bytes per second 
# with the intent of holding the connection open as long as possible use as little data as possible.

# The idea is that a bot connects and wastes time with and open connection trying to load the page that never finishes loading.

import http.server
import socketserver
import time
import random

PORT = 8000

class MyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress logging to stderr
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        # Print client's IP address, requested URL, and user agent  
        print(f"Client: {self.client_address[0]} Path: {self.path} User-Agent: {self.headers['User-Agent']}")

        start_time = time.monotonic()
        while True:
            # Generate random data of length 10 bytes
            data = bytes([random.randint(32, 90) for _ in range(10)])
            # Write the data to the client
            try:
                self.wfile.write(data)
            except ConnectionError:
                # Client disconnected
                break
            # Sleep for 1 second to slow down the sending
            time.sleep(1)
        
        end_time = time.monotonic()
        print(f"Client {self.client_address[0]} connected for {end_time - start_time:.2f} seconds")
        return

Handler = MyHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
