



## Q1

**For Device A:**

$100\mathrm{Gb/s} = 12.5\mathrm{GB/s}$

Transmission Latency: $\frac{128\mathrm{B}}{12.5\mathrm{GB/s}}=10.24ns$

Total Latency: $10.24ns+5ms=5010.24ns$

**For Device B:**

$125\mathrm{Gb/s} = 15.625\mathrm{GB/s}$

Transmission Latency: $\frac{128\mathrm{B}}{15.625\mathrm{GB/s}}=8.192ns$

Total Latency: $8.192\mathrm{ns}+6\mathrm{ms}=6008.192\mathrm{ns}$

Thus, **Device A is better**, because its total latency is smaller.

## Q2

We could build a 5-stage pipelined processor. In this case, the latency is determined by the component took the longest time.

We noticed `Operand fetch` may become the most time-consuming stage, which took up to 500ps if fetching an operand from the cache.

However, for the processor, it is much more frequent to operate on registers compared to caches. Thus, we could let `Operand fetch from cache` take 2 cycles to complete. So, right now, `Instruction decode` and `Execution unit` determine the processing frequency, which is

$f = \frac{1}{400\mathrm{ps}} = 2.5\mathrm{GHz}$

## Q3

Since the webserver speed most of the time on waiting connection if the webserver is idle. Here we simulate this scenario.

1. We measure the time starting at the server start
2. We generate 1000 requests in POST method to avoid cache used in GET and simulate the requests.
3. We measure the time when the server finished all the requests and quit.
4. We manually set a time counter to compare the running time of the server with/without profiler.

The result of default output is shown in `q3_output.txt`, and the svg is shown below

![q3](q3.svg)

From the text result, it's not clear about the invoking relationship. But in the flame graph, it's more clear. There's the result analysis

1. The overhead time (socket initial time) is trivial, which is 0.15% of the total time.
2. The server spend 20% of the time on `select` function, which is used to wait for the connection.
3. We there's a request, the server spend 53.75% of the time on `parse_request` function, which is used to read the request and parse the header. The time for handling the request is only 11.68%, compared with the time for parsing the request, it's much smaller. So the header parser is the bottleneck of the server.
4. If we enable the profiler, the execution time is 9.48s, but without the profiler, the execution time is 2.39s. The profiler takes 7.09s, which is 296.23% of the execution time. The overhead is huge, but it's acceptable since the profiler is used for debugging only once or twice.


## Q4

Juyi 

####  数据依赖

L2 和L1 

L4 和L2, L3 

L5 和L4 

L9 和L8控制依赖

假设不用经过ALU可以直接bypass到mem.

| IF         | ID   | read REG          | ALU                                | MEM  | Write back |
| ---------- | ---- | ----------------- | ---------------------------------- | ---- | ---------- |
| L1         |      |                   |                                    |      |            |
| L3         | L1   |                   |                                    |      |            |
| L2         | L3   | L1,r1; (floating) |                                    |      |            |
| L6         | L2   | L3,r2 (floating)  |                                    | L1   |            |
| L7         | L6   | L2, f0            |                                    | L3   | L1,f2      |
| L8         | L7   | L2,f2             |                                    |      | L3,f6      |
|            | L8   | L6,r1             | L2,mul f4, f2, f0(float, 7个cycle) |      |            |
|            |      | L7,r2             | L6, (int , 1cycle)                 |      |            |
|            |      | L8,r3             | L7, (int , 1cycle)                 |      | L6, r1     |
|            |      |                   | L8, (int , 1cycle)                 |      | L7, r2     |
|            |      |                   |                                    |      | L8, r3     |
| L4,        |      | L9,r0             |                                    |      |            |
|            | L4,  |                   | L9,bnz                             |      |            |
| L1(rename) |      | L4,               |                                    |      | L2,f4      |
| L3         | L1   |                   | L4, add f6, f4, f6( float, 4cycle) |      |            |
| L2         | L3   | L1,r1; (floating) |                                    |      |            |
| L6         | L2   | L3,r2 (floating)  |                                    | L1   |            |
| L5         | L6   | L2, f0            |                                    | L3   | L1,f2      |
|            | L5   |                   |                                    |      | L4, f6     |
|            |      | L5,f6             |                                    |      |            |
|            |      | L5,r2             |                                    |      |            |
|            |      |                   |                                    | L5   |            |
|            |      |                   |                                    |      |            |

9N instructions in 13N+ 9 cycles

IPC = (9N)/(13N+9) ~ 0.69
