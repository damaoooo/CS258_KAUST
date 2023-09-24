
from http.server import HTTPServer, BaseHTTPRequestHandler
import cProfile

# use multiprocessing to run the server and client at the same time
import multiprocessing
import threading
import requests
import time

import argparse

class RequestHandler(BaseHTTPRequestHandler):

    # Make a API that returns string "stop"
    def do_POST(self):
        if self.path == '/stop':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'stop')
            threading.Thread(target=self.server.shutdown).start()
        
        elif self.path == '/hello':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'hello')
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 Not Found')
            
    def log_message(self, format, *args):
        return

def visit(url, endpoint):
    r = requests.post(url + endpoint)
    # print(r.text)

def stop(url, endpoint):
    r = requests.post(url + endpoint)
    # print(r.text)
    
def simulate_client(url):
    for i in range(1000):
        visit(url, '/hello')
    stop(url, '/stop')
    

def start_server(is_profile=False):
    # Start the server
    start_time = time.time()

    if is_profile:
        profiler = cProfile.Profile()
        profiler.enable()

    server = HTTPServer(('localhost', 18080), RequestHandler)
    server.serve_forever()

    if is_profile:
        profiler.disable()
    end_time = time.time()
    print('Time used: ' + str(end_time - start_time))
    if is_profile:
        profiler.dump_stats('q3.prof')
        profiler.print_stats()

if __name__ == '__main__':        
    # Put them together and run it
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--profile', action='store_true')
    args = arg_parser.parse_args()

    server_process = multiprocessing.Process(target=start_server, args=(args.profile,))
    client_process = multiprocessing.Process(target=simulate_client, args=('http://127.0.0.1:18080',))
    server_process.start()
    client_process.start()
    
