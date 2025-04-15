class FCFSScheduler:
    is_preemptive = False

    def schedule(self, processes):
        # Sort by arrival
        processes = sorted(processes, key=lambda p: p['arrival'])

        current_time = max([p.get('ran', 0) + p['arrival'] for p in processes], default=0)

        for p in processes:
            ran = p.get('ran', 0)
            if ran < p['burst']:
                return [{
                    'name': p['name'],
                    'arrival': p['arrival'],
                    'burst': p['burst'],
                    'duration': 1,
                    'start': None
                }]

        return []
