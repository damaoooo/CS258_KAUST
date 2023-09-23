



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
