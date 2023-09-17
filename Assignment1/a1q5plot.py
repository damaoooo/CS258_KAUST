import json
import numpy as np
import matplotlib.pyplot as plt

with open("results.json", "r") as f:
    results = json.loads(f.read())

N_SERVERS = 100
fig, ax = plt.subplots()
x = np.arange(1, N_SERVERS + 1)
x_ticks = np.arange(0, N_SERVERS, 10)
ax.set_yscale("log")
ax.set_xlabel("Number of Servers")
ax.set_ylabel("Average Response Time (ms)")
ax.set_xticks(x_ticks)
ax.plot(x, [r["sqms"]["rsp_time_mean"][0] for r in results[:N_SERVERS]], color="r", label='SQMS')
ax.plot(x, [r["mqms_sq"]["rsp_time_mean"][0] for r in results[:N_SERVERS]], color="g", label='MQMS/SQ')
ax.plot(x, [r["mqms_rr"]["rsp_time_mean"][0] for r in results[:N_SERVERS]], color="b", label='MQMS/RR')

ax.axhline(y=30, label="Target Response Time", linestyle="--", color="grey")
ax.legend(loc="lower right")
fig.savefig("fig1.pdf")

N_SERVERS = 100
fig, ax = plt.subplots()
x = np.arange(1, N_SERVERS + 1)
x_ticks = np.arange(0, N_SERVERS, 10)
ax.set_yscale("log")
ax.set_xlabel("Number of Servers")
ax.set_ylabel("Average Response Time (ms)")
ax.set_xticks(x_ticks)
ax.plot(x, [r["sqms"]["rsp_time_mean"][1] for r in results[:N_SERVERS]], color="r", linestyle=":", label='SQMS (Short)')
ax.plot(x, [r["mqms_sq"]["rsp_time_mean"][1] for r in results[:N_SERVERS]], color="g", linestyle=":", label='MQMS/SQ (Short)')
ax.plot(x, [r["mqms_rr"]["rsp_time_mean"][1] for r in results[:N_SERVERS]], color="b", linestyle=":", label='MQMS/RR (Short)')
ax.plot(x, [r["sqms"]["rsp_time_mean"][2] for r in results[:N_SERVERS]], color="r", linestyle="-", label='SQMS (Long)')
ax.plot(x, [r["mqms_sq"]["rsp_time_mean"][2] for r in results[:N_SERVERS]], color="g", linestyle="-", label='MQMS/SQ (Long)')
ax.plot(x, [r["mqms_rr"]["rsp_time_mean"][2] for r in results[:N_SERVERS]], color="b", linestyle="-", label='MQMS/RR (Long)')

ax.axhline(y=30, label="Target Response Time", linestyle="--", color="grey")
ax.legend(loc="lower right")
fig.savefig("fig1a.pdf")

N_SERVERS = 280
fig, ax = plt.subplots()
x = np.arange(1, N_SERVERS + 1)
x_ticks = np.arange(0, N_SERVERS, 20)
ax.set_yscale("log")
ax.set_xlabel("Number of Servers")
ax.set_ylabel("Stddev of Response Time (ms)")
ax.set_xticks(x_ticks)
ax.plot(x, [r["sqms"]["rsp_time_stddev"][0] for r in results[:N_SERVERS]], color="r", label='SQMS')
ax.plot(x, [r["mqms_sq"]["rsp_time_stddev"][0] for r in results[:N_SERVERS]], color="g", label='MQMS/SQ')
ax.plot(x, [r["mqms_rr"]["rsp_time_stddev"][0] for r in results[:N_SERVERS]], color="b", label='MQMS/RR')
ax.axhline(y=3, label="Target Response Time", linestyle="--", color="grey")
ax.legend(loc="lower right")
fig.savefig("fig2.pdf")

N_SERVERS = 280
fig, ax = plt.subplots()
x = np.arange(1, N_SERVERS + 1)
x_ticks = np.arange(0, N_SERVERS, 20)
ax.set_yscale("log")
ax.set_xlabel("Number of Servers")
ax.set_ylabel("Stddev of Response Time (ms)")
ax.set_xticks(x_ticks)
ax.plot(x, [r["sqms"]["rsp_time_stddev"][1] for r in results[:N_SERVERS]], color="r", linestyle=":", label='SQMS (Short)')
ax.plot(x, [r["mqms_sq"]["rsp_time_stddev"][1] for r in results[:N_SERVERS]], color="g", linestyle=":", label='MQMS/SQ (Short)')
ax.plot(x, [r["mqms_rr"]["rsp_time_stddev"][1] for r in results[:N_SERVERS]], color="b", linestyle=":", label='MQMS/RR (Short)')
ax.plot(x, [r["sqms"]["rsp_time_stddev"][2] for r in results[:N_SERVERS]], color="r", linestyle="-", label='SQMS (Long)')
ax.plot(x, [r["mqms_sq"]["rsp_time_stddev"][2] for r in results[:N_SERVERS]], color="g", linestyle="-", label='MQMS/SQ (Long)')
ax.plot(x, [r["mqms_rr"]["rsp_time_stddev"][2] for r in results[:N_SERVERS]], color="b", linestyle="-", label='MQMS/RR (Long)')
ax.axhline(y=3, label="Target Response Time", linestyle="--", color="grey")
ax.legend(loc="lower right")
fig.savefig("fig2a.pdf")
print([(i+1, "%.2f" % r["mqms_rr"]["rsp_time_stddev"][0]) for i, r in enumerate(results[:N_SERVERS])])

N_SERVERS = 100
fig, ax = plt.subplots()
x = np.arange(1, N_SERVERS + 1)
x_ticks = np.arange(0, N_SERVERS, 20)
# ax.set_yscale("log")
ax.set_xlabel("Number of Servers")
ax.set_ylabel("Utilization of Servers")
ax.set_xticks(x_ticks)
ax.plot(x, [r["sqms"]["sys_util"] for r in results[:N_SERVERS]], label='SQMS')
ax.plot(x, [r["mqms_sq"]["sys_util"] for r in results[:N_SERVERS]], label='MQMS/SQ')
ax.plot(x, [r["mqms_rr"]["sys_util"] for r in results[:N_SERVERS]], label='MQMS/RR')
ax.legend(loc="lower right")
fig.savefig("fig3.pdf")

N_SERVERS = 30
fig, ax = plt.subplots()
x = np.arange(1, N_SERVERS + 1)
x_ticks = np.arange(0, N_SERVERS, 2)
ax.set_yscale("log")
ax.set_xlabel("Number of Servers")
ax.set_ylabel("Average Response Time (ms)")
ax.set_xticks(x_ticks)
ax.plot(x, [r["prio_short"]["rsp_time_mean"][1] for r in results[:N_SERVERS]], label='Queue (Short)')
ax.plot(x, [r["prio_long"]["rsp_time_mean"][2] for r in results[:N_SERVERS]], label='Queue (Long)')
ax.axhline(y=15, label="Target Response Time (Short)", linestyle=":", color="grey")
ax.axhline(y=800, label="Target Response Time (Long)", linestyle="--", color="grey")
ax.legend(loc="lower right")
fig.savefig("fig4.pdf")

N_SERVERS = 30
fig, ax = plt.subplots()
x = np.arange(1, N_SERVERS + 1)
x_ticks = np.arange(0, N_SERVERS, 2)
ax.set_yscale("log")
ax.set_xlabel("Number of Servers")
ax.set_ylabel("Stddev of Response Time (ms)")
ax.set_xticks(x_ticks)
ax.plot(x, [r["prio_short"]["rsp_time_stddev"][1] for r in results[:N_SERVERS]], label='Queue (Short)')
ax.plot(x, [r["prio_long"]["rsp_time_stddev"][2] for r in results[:N_SERVERS]], label='Queue (Long)')
ax.legend(loc="lower right")
fig.savefig("fig5.pdf")
# print("prio_short_rsp_time", [(i+1, "%.2f" % r["prio_short"]["rsp_time_mean"][1]) for i, r in enumerate(results[:N_SERVERS])]) # 3
# print("prio_long_rsp_time", [(i+1, "%.2f" % r["prio_long"]["rsp_time_mean"][2]) for i, r in enumerate(results[:N_SERVERS])]) # 12