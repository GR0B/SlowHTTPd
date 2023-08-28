#!/usr/bin/env python3
# Robert Sturzbecher 2025-05-11

# A HTTP server to punish bots, 
# it will slowly reply to a HTTP GET request at a rate of 10 random bytes per second 
# with the intent of holding the connection open as long as possible use as little data as possible.

# The idea is that a bot connects and wastes time with and open connection trying to load the page that never finishes loading.

import http.server
import socketserver
import threading
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
        msg = f"\n{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} Client: {self.client_address[0]} Path: {self.path} User-Agent: {self.headers['User-Agent']}"
        print(msg)
        with open('SlowHTTPd.log', 'a') as log_file:
            log_file.write(msg)

        start_time = time.monotonic()
        while True:
            # Generate random data of length 10 bytes
            data = bytes([random.randint(32, 90) for _ in range(10)])
            print(".", end = '')
            # Write the data to the client
            try:
                self.wfile.write(data)
                # Sleep for 1 second to slow down the sending
                time.sleep(1)
            except ConnectionError:
                break
            
        end_time = time.monotonic()
        endured_time = end_time - start_time
        endured_bytes = round(endured_time,0) *10 
        msg = f"\n{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} Client: {self.client_address[0]} Disconnected, they endured {endured_time:,.2f} Seconds {endured_bytes:,.0f} Bytes"
        print(msg)
        with open('SlowHTTPd.log', 'a') as log_file:
            log_file.write(msg)
        return


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

Handler = MyHandler

with ThreadedHTTPServer(("", PORT), Handler) as httpd:
    print("Slooooowly serving on port", PORT)
    httpd.serve_forever()