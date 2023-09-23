
from http.server import HTTPServer, BaseHTTPRequestHandler
import cProfile

# use multiprocessing to run the server and client at the same time
import multiprocessing
import threading
import requests






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


def visit(url, endpoint):
    r = requests.post(url + endpoint)
    # print(r.text)

def stop(url, endpoint):
    r = requests.post(url + endpoint)
    # print(r.text)
    
def simulate_client(url):
    for i in range(10):
        visit(url, '/hello')
    stop(url, '/stop')
    

def start_server():
    profiler = cProfile.Profile()
    profiler.enable()

    server = HTTPServer(('localhost', 18080), RequestHandler)
    server.serve_forever()

    profiler.disable()
    profiler.print_stats(sort='tottime')

if __name__ == '__main__':        
    # Put them together and run it
    server_process = multiprocessing.Process(target=start_server)
    client_process = multiprocessing.Process(target=simulate_client, args=('http://127.0.0.1:18080',))
    server_process.start()
    client_process.start()
    
    # server_process.join()
    # client_process.join()
    
    print("End of program")
