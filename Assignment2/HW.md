



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
2. We generate 1000 requests in POST method to avoid cache.
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

ld f1  1cycle 

mul f4,f2,f0  7 cycle

ld f6 1 cycle  

add f6   4 cycle 写后读, 不能改. 

st f6 1 cycle

add r1, r1, 8  1 cycle

add r2, r2, 8 1 cycle

add r3, -1  1 cycle

bnz  1cycle, 但是可以都预测为跳转,  循环次数很大的时候 约等于0 

总共17个cycle, 9个instruction 

不能同时读取两个浮点数.  我们也不能重命名寄存器.

IPC :  17/9=1.88888888889 

这样可能不对? 需要excel 一个个stage算吗?  
