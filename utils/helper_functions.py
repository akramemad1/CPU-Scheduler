# utils.py

import time

def sleep_or_mwait(live, time_unit):
    if live:
        time.sleep(time_unit)
    else:
        time.sleep(0.02)  # 20 ms

def calculate_stats(processes, executed_time):
    waiting_times = []
    turnaround_times = []

    for proc in processes:
        completion_time = executed_time.get(proc['name'], 0)
        if completion_time > 0:
            tat = completion_time - proc['arrival']
            wt = tat - proc['burst']
            turnaround_times.append(tat)
            waiting_times.append(wt)

    avg_wt = sum(waiting_times) / len(waiting_times) if waiting_times else 0
    avg_tat = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0

    return avg_wt, avg_tat

def get_live_table(processes, run_time):
    table = []
    for p in processes:
        ran_time = run_time.get(p['name'], 0)
        remaining = max(0, p['burst'] - ran_time)
        table.append({
            'name': p['name'],
            'arrival': p['arrival'],
            'burst': p['burst'],
            'remaining': remaining
        })
    return table
