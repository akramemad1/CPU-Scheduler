# core/simulator.py
import threading
from PyQt5.QtCore import QThread, pyqtSignal
import time

class Simulator(QThread):
    update_gantt = pyqtSignal(str, int)
    update_table = pyqtSignal(list)
    update_stats = pyqtSignal(float, float)
    simulation_done = pyqtSignal()
    process_added = pyqtSignal()  

    def __init__(self, scheduler, processes, time_unit=1, live=True):
        super().__init__()
        self.current_time = 0
        self.scheduler = scheduler
        self.processes = processes.copy()
        self.time_unit = time_unit
        self.live = live
        self.running = True
        self.lock = threading.Lock()
        self.new_processes = []
        self._executed_time = {}
        self._run_time = {}
        self.reschedule_needed = True  

        self.process_added.connect(self.on_new_process)

    def on_new_process(self):
        self.reschedule_needed = True

    def add_process(self, process):
        with self.lock:
            print(f"Checking for duplicate: {process['name']}")

            all_processes = self.processes + self.new_processes
            if any(p['name'] == process['name'] for p in all_processes):
                print(f"Duplicate found: {process['name']}")
                return False

            print(f"Adding new process: {process}")
            self.new_processes.append(process)
            self.update_table.emit(self.get_live_table())
            self.process_added.emit()  
            return True

    def run(self):
        try:
            scheduled = []

            while self.running:
                # Merge new processes
                with self.lock:
                    if self.new_processes:
                        self.processes.extend(self.new_processes)
                        self.new_processes.clear()
                        self.reschedule_needed = True

                #  Reschedule if triggered
                if self.reschedule_needed or not scheduled:
                    scheduled = self.scheduler.schedule(self.processes)
                    scheduled = [
                        step for step in scheduled
                        if self._run_time.get(step['name'], 0) < step['burst']
                    ]
                    self.reschedule_needed = False

                if not scheduled:
                    if self.live:
                        time.sleep(self.time_unit)
                    else:
                        self.msleep(20)
                    self.current_time += 1
                    continue

                step = scheduled.pop(0)
                if not self.running:
                    break

                if step['arrival'] > self.current_time:
                    # wait
                    if self.live:
                        time.sleep(self.time_unit)
                    else:
                        self.msleep(20)
                    self.current_time += 1
                    continue

                for t in range(step['duration']):
                    if not self.running:
                        break

                    self._run_time[step['name']] = self._run_time.get(step['name'], 0) + 1
                    self.update_gantt.emit(step['name'], self.current_time)
                    self.update_table.emit(self.get_live_table())

                    if self.live:
                        time.sleep(self.time_unit)
                    else:
                        self.msleep(20)

                    self.current_time += 1

                if self._run_time.get(step['name'], 0) >= step['burst']:
                    self._executed_time[step['name']] = self.current_time

                # If all done, stop
                if all(p['name'] in self._executed_time for p in self.processes):
                    break

            # Final stats
            avg_wt, avg_tat = self.calculate_stats()
            self.update_stats.emit(avg_wt, avg_tat)
            self.simulation_done.emit()

        finally:
            self.running = False

    def get_live_table(self):
        table = []
        for p in self.processes:
            ran_time = self._run_time.get(p['name'], 0)
            remaining = max(0, p['burst'] - ran_time)
            table.append({
                'name': p['name'],
                'arrival': p['arrival'],
                'burst': p['burst'],
                'remaining': remaining
            })
        return table

    def start(self):
        print("Simulator thread starting...")
        super().start()
        print(f"Thread running: {self.isRunning()}")

    def stop(self):
        self.running = False

    def calculate_stats(self):
        waiting_times = []
        turnaround_times = []

        all_processes = self.processes + self.new_processes
        for proc in all_processes:
            completion_time = self._executed_time.get(proc['name'], 0)
            print(f"{proc['name']}: Arrival={proc['arrival']}, Burst={proc['burst']}, Completion={completion_time}")
            if completion_time > 0:
                tat = completion_time - proc['arrival']
                wt = tat - proc['burst']
                turnaround_times.append(tat)
                waiting_times.append(wt)

        avg_wt = sum(waiting_times) / len(waiting_times) if waiting_times else 0
        avg_tat = sum(turnaround_times) / len(turnaround_times) if turnaround_times else 0

        print(f"Stats for {len(waiting_times)} processes: "
              f"WT sum {sum(waiting_times)}, TAT sum {sum(turnaround_times)}")
        return avg_wt, avg_tat