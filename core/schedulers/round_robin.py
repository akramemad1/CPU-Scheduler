from collections import deque

class RoundRobinScheduler:
    def __init__(self, quantum=2):
        self.quantum = quantum
    
    def schedule(self, processes):
        processes = sorted(processes, key=lambda p: p['arrival'])
        queue = deque()
        timeline = []
        remaining_burst = {p['name']: p['burst'] for p in processes}
        current_time = 0
        process_index = 0
        
        while True:
            # Add arriving processes to queue
            while process_index < len(processes) and processes[process_index]['arrival'] <= current_time:
                queue.append(processes[process_index])
                process_index += 1
            
            if not queue:
                if process_index < len(processes):
                    # Jump to next arrival time if queue is empty
                    current_time = processes[process_index]['arrival']
                    continue
                else:
                    break  # All processes completed
            
            # Get next process
            current_process = queue.popleft()
            name = current_process['name']
            exec_time = min(self.quantum, remaining_burst[name])
            
            # Record execution
            timeline.append({
                'name': name,
                'arrival': current_process['arrival'],
                'burst': remaining_burst[name]- exec_time,
                'duration': exec_time,
                'start': current_time
            })
            
            # Update tracking
            current_time += exec_time
            remaining_burst[name] -= exec_time
            
            # Re-add to queue if not finished
            if remaining_burst[name] > 0:
                queue.append(current_process)
        
        return timeline
    

'''
        Example usage
def main():
    processes = [
            {'name': 'P1', 'arrival': 0, 'burst': 5},
            {'name': 'P2', 'arrival': 1, 'burst': 11},
            {'name': 'P3', 'arrival': 2, 'burst': 8}
        ]
    quantum = 2
    scheduler = RoundRobinScheduler(quantum)
    timeline = scheduler.schedule(processes)
    for entry in timeline:
        print(entry)
if __name__ == "__main__":
    main()
''' 
