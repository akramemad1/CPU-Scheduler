import heapq
 
class SJFScheduler:
    is_preemptive = False
    def schedule(self, processes):
        """
        Returns a list of dicts:
        Each dict contains: name, arrival, burst, duration, start time
        """
        n = len(processes)
        processes = sorted(processes, key=lambda p: p['arrival'])  # Sort by arrival time once
 
        heap = []
        result = []
        current_time = 0
        i = 0  # Index to track which processes have been added to heap
 
        while i < n or heap:
            # Add all processes that have arrived to the heap
            while i < n and processes[i]['arrival'] <= current_time:
                heapq.heappush(heap, (processes[i]['burst'], i, processes[i]))
                i += 1
 
            if heap:
                burst, idx, p = heapq.heappop(heap)
                start_time = max(current_time, p['arrival'])
 
                result.append({
                    'name': p['name'],
                    'arrival': p['arrival'],
                    'burst': p['burst'],
                    'duration': p['burst'],
                    'start': start_time
                })
 
                current_time = start_time + p['burst']
            else:
                # Jump to next process arrival if heap is empty
                if i < n:
                    current_time = processes[i]['arrival']
 
        return result
    

'''
# Example usage:
processes = [
    {'name': 'P1', 'arrival': 0,  'burst': 10},
    {'name': 'P2', 'arrival': 2,  'burst': 4},
    {'name': 'P3', 'arrival': 3,  'burst': 2},
    {'name': 'P4', 'arrival': 20, 'burst': 1},  # Arrives after a big gap
    {'name': 'P5', 'arrival': 1,  'burst': 8},
    {'name': 'P6', 'arrival': 4,  'burst': 1}   # Very short but late
]

scheduler = SJFScheduler()
timeline = scheduler.schedule(processes)
 
for entry in timeline:
    print(entry)

'''
