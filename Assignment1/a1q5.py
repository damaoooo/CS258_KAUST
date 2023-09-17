# Suggest to use Python 3.10 or newer

import numpy as np
import warnings
import copy
import json
from collections import deque
from dataclasses import dataclass
from multiprocessing import Pool
from enum import Enum

N_REQUESTS = 10000
MAX_N_SERVERS = 300

def DEBUG(*args, **kwargs):
    # print(*args, **kwargs)
    pass

def TRACE(*args, **kwargs):
    # print(*args, **kwargs)
    pass

class RequestType(Enum):
    Short = 0
    Long = 1

@dataclass
class Request:
    arrival_time: int = 0
    proc_time: int = 0
    type: RequestType = RequestType.Short
    exec_start_time: int = 0
    exec_stop_time: int = 0
    response_time: int = 0

class Server:
    def __init__(self, sid: int, qid: int):
        self.sid = sid
        self.qid = qid
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
        request.response_time = request.exec_start_time - request.arrival_time
        self.current_request = request
        
    def run(self, to_clock: int):
        TRACE("[%s/%s] (Trying %s -> %s)" % (self.qid, self.sid, self.clock, to_clock))
        assert to_clock >= self.clock
        self.clock = to_clock
        if self.is_busy() and to_clock >= self.current_request.exec_stop_time:
            self.busy_clock += self.current_request.proc_time
            self.complete_queue.append(self.current_request)
            self.current_request = None
            DEBUG("[%s/%s] Complete %s" % (self.qid, self.sid, self.complete_queue[-1]))
        TRACE("[%s/%s] (Finish -> %s)" % (self.qid, self.sid, self.clock))

class Queue:
    def __init__(self, qid: int, num_servers: int):
        self.qid = qid
        self.servers = [Server(i, qid) for i in range(num_servers)]
        self.work_queue: deque[Request] = deque()
    
    def get_num_busy_servers(self):
        return sum([1 if s.is_busy() else 0 for s in self.servers])
        
    def get_min_avail_time(self):
        return min([(s.get_avail_time(), i) for i, s in enumerate(self.servers)], key=lambda x: x[0])
    
    def get_max_avail_time(self):
        return max([(s.get_avail_time(), i) for i, s in enumerate(self.servers)], key=lambda x: x[0])
    
    def put_request(self, request: Request):
        self.work_queue.append(request)
        DEBUG("[%s] # of pending requests: %s, # of busy servers: %s, +%s"
              % (self.qid, len(self.work_queue), self.get_num_busy_servers(), request))
    
    def _run_all_server(self, to_clock: int):
        for server in self.servers:
            server.run(to_clock)

    def run(self, to_clock: int):
        DEBUG("[%s] (Trying -> %s)" % (self.qid, to_clock))
        while True:
            if len(self.work_queue) == 0:
                self._run_all_server(to_clock)
                break
            else:
                min_avail_time, server_idx = self.get_min_avail_time()
                TRACE("[%s] Min avail time: %s" % (self.qid, min_avail_time))
                if min_avail_time <= to_clock:
                    self._run_all_server(min_avail_time)
                    request = self.work_queue.popleft()
                    self.servers[server_idx].process_request(request)
                    DEBUG("[%s] Dispatch to [%s/%s]: %s"
                          % (self.qid, self.qid, server_idx, request))
                else:
                    self._run_all_server(to_clock)
                    break
        DEBUG("[%s] (Finish -> %s)" % (self.qid, to_clock))
    
    def drain(self):
        DEBUG("[%s] Start draining" % (self.qid))
        while len(self.work_queue) + self.get_num_busy_servers() > 0:
            self.run(self.get_max_avail_time()[0])
        DEBUG("[%s] Finish draining" % (self.qid))

class System:
    def __init__(self):
        self.queues: list[Queue] = []
    
    def get_min_avail_time(self):
        return min([(q.get_min_avail_time()[0], i) for i, q in enumerate(self.queues)], key=lambda x: x[0])
    
    def get_max_avail_time(self):
        return max([(q.get_max_avail_time()[0], i) for i, q in enumerate(self.queues)], key=lambda x: x[0])
    
    def drain(self):
        DEBUG("[SYS] Start draining")
        for queue in self.queues:
            queue.drain()
        stop_time, _ = self.get_max_avail_time()
        DEBUG("[SYS] Sync to (%s)" % stop_time)
        for queue in self.queues:
            queue.run(stop_time)
    
    def simulate_sq(self, requests: list[Request], num_queues: int, num_servers_per_queue: int):
        # shortest-queue algorithm
        self.queues = [Queue(i, num_servers_per_queue) for i in range(num_queues)]
        for req in requests:
            for queue in self.queues:
                queue.run(req.arrival_time)
            
            queue_idx, _ = min([(i, len(q.work_queue) + q.get_num_busy_servers()) \
                               for i, q in enumerate(self.queues)], key=lambda x: x[1])
            self.queues[queue_idx].put_request(req)
        self.drain()
        return self.summary()

    def simulate_rr(self, requests: list[Request], num_queues: int, num_servers_per_queue: int):
        # round-robin algorithm
        self.queues = [Queue(i, num_servers_per_queue) for i in range(num_queues)]
        queue_idx = 0
        for req in requests:
            for queue in self.queues:
                queue.run(req.arrival_time)
            self.queues[queue_idx].put_request(req)
            queue_idx = (queue_idx + 1) % len(self.queues)
        self.drain()
        return self.summary()
    
    def simulate_prio(self, requests: list[Request], num_servers_short_req: int, num_servers_long_req: int):
        # round-robin algorithm
        self.queues = [Queue(0, num_servers_short_req), Queue(1, num_servers_long_req)]
        for req in requests:
            for queue in self.queues:
                queue.run(req.arrival_time)
            self.queues[0 if req.type == RequestType.Short else 1].put_request(req)
        self.drain()
        return self.summary()

    def summary(self):
        requests: list[Request] = []
        utilizations: list[float] = []
        for q in self.queues:
            for s in q.servers:
                requests += s.complete_queue
            utilizations.append(np.mean([s.busy_clock / s.clock for s in q.servers]))
        
        rsp_time = [r.response_time for r in requests]
        rsp_time_long = [r.response_time for r in requests if r.type == RequestType.Long]
        rsp_time_short = [r.response_time for r in requests if r.type == RequestType.Short]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            metrics = {
                "rsp_time_mean": (np.mean(rsp_time), np.mean(rsp_time_short), np.mean(rsp_time_long)),
                "rsp_time_stddev": (np.std(rsp_time), np.std(rsp_time_short), np.std(rsp_time_long)),
                "sys_util": np.mean(utilizations),
                "queue_util": utilizations
            }
            print("[SYS] %s" % metrics)
            return metrics

def generate_requests(num: int):
    requests: list[Request] = []
    arrival_time_intervals = np.random.poisson(lam=5, size=num-1)
    arrival_times = [0] + list(np.cumsum(arrival_time_intervals))
    for i in range(num):
        if np.random.rand() < 0.9:
            req_type = RequestType.Short
            proc_time = np.random.randint(low=3, high=20)
        else:
            req_type = RequestType.Long
            proc_time = np.random.randint(low=200, high=1000)
        requests.append(Request(arrival_times[i], proc_time, req_type))
    return requests

requests = generate_requests(N_REQUESTS)

def simulate(n: int):
    reqs = copy.deepcopy(requests)
    system = System()
    
    return {
        "sqms": system.simulate_rr(reqs, 1, n),
        "mqms_sq": system.simulate_sq(reqs, n, 1),
        "mqms_rr": system.simulate_rr(reqs, n, 1),
        "prio_short": system.simulate_prio(reqs, n, 50),
        "prio_long": system.simulate_prio(reqs, 50, n),
    }

def sol_b_c_d_e():
    n_servers = [i for i in range(1, MAX_N_SERVERS)]
    with Pool() as p:
        results = p.map(simulate, n_servers)
        with open("results.json", "w") as f:
            f.write(json.dumps(results))

def verify():
    reqs = copy.deepcopy(requests)
    system = System()
    system.simulate_rr(reqs, 1, 25) # q5.c
    system.simulate_sq(reqs, 28, 1) # q5.d
    system.simulate_rr(reqs, 192, 1) # q5.e
    system.simulate_prio(reqs, 3, 13) # q5.f

# sol_b_c_d_e()
verify()