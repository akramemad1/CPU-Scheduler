class priority_preem:
    is_preemptive = True
    def schedule(self , processes):
        """
        Returns a list of dicts:
        Each dict contains: name, arrival, burst, duration, start time
        """
        processes = sorted(processes, key=lambda p: (p['arrival'], p['priority'])) # Sort by arrival time then priority(if same arrival time)
        current_time = 0
        timeline = []
        current_process = None
        ready_queue = []
        # remaining time of processes
        remaining = {p['name']: p['burst'] for p in processes}
        
        while processes or current_process or ready_queue:
            # choose the process with highest priority and proper arrival time
            arrived_now = [p for p in processes if p['arrival'] <= current_time]
            processes = [p for p in processes if p['arrival'] > current_time]
            ready_queue.extend(arrived_now)
            # sort the ready queue by priority and arrival time (if two processes have same priority then earlier arrival time have higher hand)      
            ready_queue.sort(key=lambda x: (x['priority'], x['arrival']))
            current_process = ready_queue.pop(0)
            # execute the current process for one time unit
            remaining[current_process['name']] -= 1
            current_time += 1
            # append the current process to the timeline
            timeline.append({
                'name': current_process['name'],
                'arrival': current_process['arrival'],
                'burst': current_process['burst'],
                'duration': 1,
                'start': current_time - 1,
                'priority': current_process['priority']
            })
            # if the current process is finished, remove it from the remaining time
            if remaining[current_process['name']] == 0:
                del remaining[current_process['name']]
                current_process = None
            else:
                # if the current process is not finished, add it back to the ready queue
                ready_queue.append(current_process)
                current_process = None
            
        return sorted(timeline, key=lambda p: p['priority'])  # Return the scheduled list with updated start times
    
"""
# Example usage:
processes = [
    {'name': 'P1', 'arrival': 0, 'burst': 4, 'priority': 3},
    {'name': 'P2', 'arrival': 1, 'burst': 3, 'priority': 2},
    {'name': 'P3', 'arrival': 3, 'burst': 2, 'priority': 1},
    {'name': 'P4', 'arrival': 5, 'burst': 3, 'priority': 2},
    {'name': 'P5', 'arrival': 6, 'burst': 1, 'priority': 3},
]

scheduler = priority_preem()
timeline = scheduler.schedule(processes)
for entry in timeline:
    print(entry)"""
