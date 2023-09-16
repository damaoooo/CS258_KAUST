# Suggest to use Python 3.10 or newer

import numpy as np
from collections import deque
from dataclasses import dataclass
from enum import Enum

class RequestType(Enum):
    Short = 0
    Long = 1

@dataclass
class Request:
    type: RequestType = RequestType.Short
    arrival_time: int = 0
    proc_time: int = 0
    exec_start_time: int = 0
    exec_stop_time: int = 0
    response_time: int = 0

class Server:
    def __init__(self):
        self.clock = 0
        self.busy_clock = 0
        self.current_request: Request = None
        self.complete_queue: list[Request] = []
    
    def is_busy(self):
        return self.current_request != None
    
    def get_avail_time(self):
        if self.is_busy():
            return self.current_request.exec_stop_time
        else:
            return self.clock
    
    def process_request(self, request: Request):
        assert not self.is_busy()
        request.exec_start_time = self.clock
        request.exec_stop_time = self.clock + request.proc_time
        request.response_time = request.exec_stop_time - request.arrival_time
        self.current_request = request
        
    def run(self, to_clock: int):
        assert to_clock >= self.clock
        self.clock = to_clock
        if self.is_busy() and to_clock >= self.current_request.exec_stop_time:
            self.busy_clock += self.current_request.proc_time
            self.complete_queue.append(self.current_request)
            self.current_request = None

class Queue:
    def __init__(self, num_servers: int):
        self.servers = [Server() for _ in range(num_servers)]
        self.work_queue_prio0: deque[Request] = deque()
        self.work_queue_prio1: deque[Request] = deque()
    
    def get_num_pending_requests(self):
        return len(self.work_queue_prio0) + len(self.work_queue_prio1)
    
    def get_pending_request(self):
        if len(self.work_queue_prio0) > 0:
            return self.work_queue_prio0.popleft()
        else:
            return self.work_queue_prio1.popleft()
        
    def get_min_avail_time(self):
        return min([(s.get_avail_time(), i) for i, s in enumerate(self.servers)], key=lambda x: x[1])
    
    def get_max_avail_time(self):
        return max([(s.get_avail_time(), i) for i, s in enumerate(self.servers)], key=lambda x: x[1])
    
    def put_request(self, request: Request, enable_prio=False):
        if enable_prio:
            if request.type == RequestType.Short:
                self.work_queue_prio0.append(request)
            elif request.type == RequestType.Long:
                self.work_queue_prio1.append(request)
        else:
            self.work_queue_prio0.append(request)    
    
    def _run_all_server(self, to_clock: int):
        for server in self.servers:
            server.run(to_clock)

    def run(self, to_clock: int):
        while True:
            if self.get_num_pending_requests() == 0:
                self._run_all_server(to_clock)
                return
            else:
                min_avail_time, server_idx = self.get_min_avail_time()
                if min_avail_time <= to_clock:
                    self._run_all_server(min_avail_time)
                    request = self.get_pending_request()
                    self.servers[server_idx].process_request(request)
                else:
                    self._run_all_server(to_clock)
                    return
    
    def drain(self):
        while True:
            self.run(self.get_max_avail_time()[0])
            if self.get_num_pending_requests() > 0:
                return

class System:
    def __init__(self, num_queues: int, num_servers_per_queue: int, enable_prio=False):
        self.queues = [Queue(num_servers_per_queue) for _ in range(num_queues)]
        self.enable_prio = enable_prio
    
    def get_min_avail_time(self):
        return min([(s.get_min_avail_time(), i) for i, s in enumerate(self.queues)], key=lambda x: x[1])
    
    def get_max_avail_time(self):
        return max([(s.get_max_avail_time(), i) for i, s in enumerate(self.queues)], key=lambda x: x[1])
    
    def drain(self):
        for queue in self.queues:
            queue.drain()
        stop_time = self.get_max_avail_time()
        for queue in self.queues:
            queue.run(stop_time)
    
    def simulate_single_server(self, requests: list[Request]):
        for req in requests:
            self.servers[0].run(req.arrival_time)
            self.servers[0].put_request(req)
        self.run_to_complete()
    
    def simulate_sq(self, requests: list[Request]):
        # shortest-queue algorithm
        for req in requests:
            for server in self.servers:
                server.run(req.arrival_time)
            
            server_idx = min([(idx, server.get_num_pending_requests()) \
                               for idx, server in enumerate(self.servers)], key=lambda x: x[1])[0]
            print(server_idx)
            self.servers[server_idx].put_request(req)
        self.run_to_complete()

    def simulate_rr(self, requests: list[Request]):
        # round-robin algorithm
        server_idx = 0
        for req in requests:
            for server in self.servers:
                server.run(req.arrival_time)

            print(server_idx)
            self.servers[server_idx].put_request(req)
            server_idx = (server_idx + 1) % len(self.servers)
        self.run_to_complete()
    
    def summary(self):
        for idx, server in enumerate(self.servers):
            print("idx=%s, clock=%s, busy=%s" % (idx, server.clock, server.busy_clock))
            print(server.complete_queue)


cluster = Cluster(3)
reqs = [Request(1, 5), Request(2, 5), Request(100, 5), Request(102, 5)]
cluster.simulate_rr(reqs)
cluster.summary()

