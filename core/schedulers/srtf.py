import heapq
 
class SRTFScheduler:

    def schedule(self, processes):
        """
        Returns a list of dicts:
        Each dict contains: name, arrival, burst, duration, start
        """
        # Sort by arrival initially
        processes = sorted(processes, key=lambda p: p['arrival'])
        time = 0
        i = 0
        ready_queue = []
        result = []
        # To track remaining burst per process
        remaining = {p['name']: p['burst'] for p in processes}
        current_process = None
        current_start = None
        while i < len(processes) or ready_queue or current_process:
            # Add all processes that arrive at this time
            while i < len(processes) and processes[i]['arrival'] <= time:
                p = processes[i]
                heapq.heappush(ready_queue, (remaining[p['name']], p['arrival'], p['name'], p))
                i += 1
            # If we have a current process, check if it should be preempted
            if current_process:
                # Check if there's a shorter burst process in the queue
                if ready_queue and ready_queue[0][0] < remaining[current_process['name']]:
                    # End current slice
                    result.append({
                        'name': current_process['name'],
                        'arrival': current_process['arrival'],
                        'burst': remaining[current_process['name']] + (time - current_start),
                        'start': current_start,
                        'duration': time - current_start
                    })
                    heapq.heappush(ready_queue, (remaining[current_process['name']], current_process['arrival'], current_process['name'], current_process))
                    current_process = None
            # If no process is running, pick the one with smallest remaining time
            if not current_process and ready_queue:
                _, _, _, current_process = heapq.heappop(ready_queue)
                current_start = time
            if current_process:
                # Execute current process for 1 time unit
                remaining[current_process['name']] -= 1
                # If it's done, finalize it
                if remaining[current_process['name']] == 0:
                    result.append({
                        'name': current_process['name'],
                        'arrival': current_process['arrival'],
                        'burst': remaining[current_process['name']] + (time - current_start + 1),
                        'start': current_start,
                        'duration': time - current_start + 1
                    })
                    current_process = None
            # If nothing is running and nothing in queue, just idle forward
            time += 1
        return result
    
'''
# Example usage
processes = [
    {'name': 'X', 'arrival': 0, 'burst': 5},
    {'name': 'Y', 'arrival': 1, 'burst': 3},
    {'name': 'Z', 'arrival': 2, 'burst': 6},
    {'name': 'W', 'arrival': 4, 'burst': 2}
]
scheduler = SRTFScheduler()
timeline = scheduler.schedule(processes)
 
for entry in timeline:
    print(entry)
'''
