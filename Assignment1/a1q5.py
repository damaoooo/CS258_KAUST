import numpy as np
from dataclasses import dataclass
from typing import List, Union, Callable
from enum import Enum

class ServiceType(Enum):
    Fast = 1
    Slow = 2

@dataclass
class Client:
    arrival_time: int = 0
    service_time: int = 0
    service_type: ServiceType = ServiceType.Fast
    waiting_time: int = 0
    service_start_time: int = 0
    service_end_time: int = 0

SingleQueue = List[Client]

robin = 0

def shortest_queue(queue: List[SingleQueue]) -> int:
    queue_length = [len(i) for i in queue]
    return np.argmin(queue_length)

def round_robin_queue(queue: List[SingleQueue]) -> int:
    global robin
    robin += 1
    return robin % len(queue)

class Queue:
    def __init__(self, size: int = 1000, server_num: int = 1, queue_num: int = 1):
        self.size = size
        self.clients: SingleQueue = []
        
        self.queue: List[SingleQueue] = [[] for _ in range(queue_num)]
        
        self.server_num = server_num
        self._fill_client()
        
    def _generate_service_time(self):
            if np.random.rand() < 0.9:
                service_type = ServiceType.Fast
            else:
                service_type = ServiceType.Slow
                
            if service_type == ServiceType.Fast:
                return np.random.randint(low=3, high=20), service_type
            else:
                return np.random.randint(low=200, high=1000), service_type
        
    def _fill_client(self):
        arrival_time_interval = np.random.poisson(lam=5, size=self.size-1)
        service_time, service_type = self._generate_service_time()
        self.clients.append(Client(arrival_time=0, service_time=service_time, service_type=service_type))
        
        for i in range(self.size-1):
            arrival_time = np.cumsum(arrival_time_interval)[i]
            service_time, service_type = self._generate_service_time()
            self.clients.append(Client(arrival_time=arrival_time, service_time=service_time, service_type=service_type))
            
    def _start_serve_one_server(self):
        self.clients: SingleQueue
        for i in range(len(self.clients)):
            if i == 0:
                self.clients[i].service_start_time = self.clients[i].arrival_time
                self.clients[i].service_end_time = self.clients[i].service_start_time + self.clients[i].service_time
                self.clients[i].waiting_time = 0
            else:
                self.clients[i].service_start_time = max(self.clients[i].arrival_time, self.clients[i-1].service_end_time)
                self.clients[i].service_end_time = self.clients[i].service_start_time + self.clients[i].service_time
                self.clients[i].waiting_time = self.clients[i].service_start_time - self.clients[i].arrival_time
                
    def _start_serve_multi_server(self):
        server_buffer: List[Client] = []
        self.clients: SingleQueue
        for i in range(len(self.clients)):
            
            if server_buffer:
                server_buffer.sort(key=lambda x: x.service_end_time)
                pop_list = [j for j in range(len(server_buffer)) if server_buffer[j].service_end_time < self.clients[i].arrival_time]
                pop_list.sort(reverse=True)
                for j in pop_list:
                    server_buffer.pop(j)
            
            if len(server_buffer) < self.server_num:
                self.clients[i].service_start_time = self.clients[i].arrival_time
                self.clients[i].service_end_time = self.clients[i].service_start_time + self.clients[i].service_time
                self.clients[i].waiting_time = 0
                server_buffer.append(self.clients[i])
            else:
                # Find the server that will be available first
                server_buffer.sort(key=lambda x: x.service_end_time)
                self.clients[i].service_start_time = server_buffer[0].service_end_time
                self.clients[i].service_end_time = self.clients[i].service_start_time + self.clients[i].service_time
                self.clients[i].waiting_time = self.clients[i].service_start_time - self.clients[i].arrival_time
                server_buffer[0] = self.clients[i]    
                
    def _start_serve_single_server_with_multiple_queue(self, queue_algorithm: Callable[[List[SingleQueue]], int]):
        wait_list = list(range(len(self.clients)))
        # while there are still clients in the wait list and there are still clients in the queue
        while wait_list and np.sum([len(i) for i in self.queue]) > 0:
            # Find the shortest queue
            shortest_queue_index = queue_algorithm(self.queue)
            # If the shortest queue is empty, serve the first client in the wait list
            if not self.queue[shortest_queue_index]:
                self.queue[shortest_queue_index].append(self.clients[wait_list[0]])
                wait_list.pop(0)

        

                
    def start_serve(self, sort_function: Callable[[SingleQueue], Union[Client, None]] = None):
        if len(self.queue) == 1:
            if self.server_num == 1:
                self._start_serve_one_server()
            else:
                self._start_serve_multi_server()     
        else:
            if self.server_num == 1:
                self._start_serve_single_server_with_multiple_queue(queue_algorithm=sort_function)
                
    def get_average_waiting_time(self):
        return np.mean([i.waiting_time for i in self.clients])
    
    def get_std_waiting_time(self):
        return np.std([i.waiting_time for i in self.clients])
    
    def get_server_utilization(self):
        return np.sum([i.service_time for i in self.clients]) / np.max([i.service_end_time for i in self.clients])
    
    def get_response_time_mean(self):
        return np.mean([(i.service_end_time - i.arrival_time) for i in self.clients])
    
    def get_response_time_std(self):
        return np.std([(i.service_end_time - i.arrival_time) for i in self.clients])
    
    def get_slow_response_time_mean_and_std(self):
        return np.mean([(i.service_end_time - i.arrival_time) for i in self.clients if i.service_type == ServiceType.Slow]), np.std([(i.service_end_time - i.arrival_time) for i in self.clients if i.service_type == ServiceType.Slow])
    
    def get_fast_response_time_mean_and_std(self):
        return np.mean([(i.service_end_time - i.arrival_time) for i in self.clients if i.service_type == ServiceType.Fast]), np.std([(i.service_end_time - i.arrival_time) for i in self.clients if i.service_type == ServiceType.Fast])
    
    def summary(self):
        print(f"Waiting time mean and std: {self.get_average_waiting_time()}, {self.get_std_waiting_time()}")
        print(f"Server utilization: {self.get_server_utilization()}")
        print(f"Response time mean and std: {self.get_response_time_mean()}, {self.get_response_time_std()}")
        print(f"Slow response time mean and std: {self.get_slow_response_time_mean_and_std()}")
        print(f"Fast response time mean and std: {self.get_fast_response_time_mean_and_std()}")
    
    def __repr__(self) -> str:
        result = ""
        for i in self.clients:
            result += str(i)
            result += '\n'
        return result


if __name__ == "__main__":
    np.random.seed(6)
    
    event_size = 1000
    
    print("-"*50)
    
    print("Single server, single queue")
    q = Queue(event_size, server_num=1, queue_num=1)
    q.start_serve()
    q.summary()
    
    print("-"*50)
    
    print("Finding Necessary number of servers")
    for i in range(event_size):
        q = Queue(event_size, server_num=i, queue_num=1)
        q.start_serve()
        mean, std = q.get_average_waiting_time(), q.get_std_waiting_time()
        if mean < 30 and std < 0.1:
            print(f"Number of servers: {i}")
            break
    
    print("-"*50)
    
    print("Single server, multiple queue, shortest queue first")
    q = Queue(event_size, server_num=1, queue_num=2)
    q.start_serve(sort_function=shortest_queue)
