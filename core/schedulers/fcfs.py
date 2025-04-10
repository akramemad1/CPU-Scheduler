class FCFSScheduler:
    def schedule(self, processes):
        """
        Returns a list of dicts:
        Each dict contains: name, arrival, burst, duration, start time
        """
        processes = sorted(processes, key=lambda p: p['arrival'])  # Sort processes by arrival time
        current_time = 0
        timeline = []

        for p in processes:
            start = max(p['arrival'], current_time)  # Start after arrival or current_time, whichever is later
            timeline.append({
                'name': p['name'],
                'arrival': p['arrival'],
                'burst': p['burst'],
                'duration': p['burst'],
                'start': start
            })
            current_time = start + p['burst']  # Update current time after process finishes

        return timeline  # Return the scheduled list with updated start times
