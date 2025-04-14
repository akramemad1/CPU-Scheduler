class PriorityNonPreemptiveScheduler:
    is_preemptive = False
    def schedule(self, processes):
        # Step 1: Sort by arrival time, then priority
        processes.sort(key=lambda p: (p['arrival'], p['priority']))
        
        timeline = []
        timer = 0
        remaining_processes = processes.copy()
        
        while remaining_processes:
            # Step 2 & 3: Find arrived processes and sort by priority (then arrival)
            ready = [p for p in remaining_processes if p['arrival'] <= timer]
            ready.sort(key=lambda p: (p['priority'], p['arrival']))
            
            if not ready:
                # No processes ready, advance timer
                timer += 1
                continue
                
            current = ready[0]
            
            # Step 4 & 5: Execute process and update timer
            start_time = max(timer, current['arrival'])
            finish_time = start_time + current['burst']
            timer = finish_time
            
            # Step 6: Add to timeline
            timeline.append({
                'name': current['name'],
                'arrival': current['arrival'],
                'burst': current['burst'],
                'duration': current['burst'],
                'start_time': start_time
            })

            # Remove from remaining
            remaining_processes.remove(current)
            # Return to step 2
        
        return timeline
