from PyQt5.QtCore import QThread, pyqtSignal, QWaitCondition, QMutex
import time
import threading
from utils.helper_functions import sleep_or_mwait, calculate_stats, get_live_table

class SimulatorPreemitives(QThread):
    update_gantt = pyqtSignal(str, int)
    update_table = pyqtSignal(list)
    update_stats = pyqtSignal(float, float)
    simulation_done = pyqtSignal()
    pause_simulation = pyqtSignal()

    def __init__(self, scheduler, processes, time_unit=1, live=True):
        super().__init__()
        self.scheduler = scheduler
        self.processes = processes.copy()
        self.time_unit = time_unit
        self.live = live

        self.running = True
        self.paused = False
        self.current_time = 0
        self.new_processes = []
        self._executed_time = {}
        self._run_time = {}

        self.lock = threading.Lock()
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()

        self.process_lock = threading.Lock()  





        self.reschedule_needed = True

    def add_process(self, process):
        print(f"Request to add: {process['name']}")

        self.mutex.lock()
        self.paused = True
        self.mutex.unlock()

        
        self.process_lock.acquire()
        try:
            if any(p['name'] == process['name'] for p in self.processes + self.new_processes):
                print(f"Duplicate: {process['name']}")
                self.mutex.lock()
                self.paused = False
                self.pause_condition.wakeAll()
                self.mutex.unlock()
                return False

            print(f"Added: {process['name']}")
            self.new_processes.append(process)
            self.processes.extend(self.new_processes)
            self.new_processes.clear()
            self.reschedule_needed = True
            self.update_table.emit(get_live_table(self.processes, self._run_time))
        finally:
            self.process_lock.release()

        self.mutex.lock()
        self.paused = False
        self.pause_condition.wakeAll()
        self.mutex.unlock()
        return True

    

    def wait_if_paused(self):
        self.mutex.lock()
        while self.paused:
            print("Simulation paused. Waiting...")
            self.pause_condition.wait(self.mutex)
        self.mutex.unlock()

    def run(self):
        def update_process_run(process):
            name = process['name']
            self._run_time[name] = self._run_time.get(name, 0) + 1
            self.update_gantt.emit(name, self.current_time)
            self.update_table.emit(get_live_table(self.processes, self._run_time))

        try:
            scheduled = []
            self.current_time = 0
            print("Simulation started.")

            while self.running:
                self.wait_if_paused()

                # Exit when all processes are done
                if all(self._run_time.get(p['name'], 0) >= p['burst'] for p in self.processes):
                    print("All processes completed. Exiting loop.")
                    break

                with self.lock:
                    print(f"Current time: {self.current_time}, Reschedule needed: {self.reschedule_needed}, Scheduled: {scheduled}")
                    if self.reschedule_needed or not scheduled:
                        # Get all arrived and not completed processes
                        available_processes = [
                            p for p in self.processes
                            if p['arrival'] <= self.current_time and self._run_time.get(p['name'], 0) < p['burst']
                        ]

                        if available_processes:
                            # Sort by remaining burst time (Shortest Remaining Time First)
                            available_processes.sort(key=lambda p: p['burst'] - self._run_time.get(p['name'], 0))
                            scheduled = available_processes
                            print(f"  Scheduler returned (SRTF): {[s['name'] for s in scheduled]}")
                        else:
                            scheduled = []
                            print("  No available processes for scheduling.")
                        self.reschedule_needed = False

                    if not scheduled:
                        print("  No processes in scheduled list.")
                        self.sleep_or_mwait()
                        self.current_time += 1
                        continue

                    current_process = scheduled[0]
                    print(f"  Selected process: {current_process['name']}")

                    already_ran = self._run_time.get(current_process['name'], 0)
                    remaining = current_process['burst'] - already_ran
                    print(f"  Process {current_process['name']} remaining time: {remaining}")

                    executed_this_cycle = False
                    for _ in range(1):  # Execute for one time unit at a time for preemption
                        if not self.running:
                            break

                        self.wait_if_paused()

                        update_process_run(current_process)
                        self.sleep_or_mwait()
                        self.current_time += 1
                        executed_this_cycle = True

                        # Check for preemption after each time unit
                        available_processes_for_preemption = [
                            p for p in self.processes
                            if p['arrival'] <= self.current_time and self._run_time.get(p['name'], 0) < p['burst'] and p != current_process
                        ]
                        if available_processes_for_preemption:
                            available_processes_for_preemption.sort(key=lambda p: p['burst'] - self._run_time.get(p['name'], 0))
                            shortest_remaining = available_processes_for_preemption[0]['burst'] - self._run_time.get(available_processes_for_preemption[0]['name'], 0)
                            current_remaining = current_process['burst'] - self._run_time.get(current_process['name'], 0)

                            if shortest_remaining < current_remaining:
                                print(f"  Preempting {current_process['name']} due to {available_processes_for_preemption[0]['name']} at time {self.current_time}")
                                self.reschedule_needed = True
                                break # Break out of the inner loop to reschedule

                    if self._run_time[current_process['name']] >= current_process['burst']:
                        print(f"  Process {current_process['name']} completed at time {self.current_time}")
                        self._executed_time[current_process['name']] = self.current_time
                        self.reschedule_needed = True

            avg_wt, avg_tat = calculate_stats(self.processes, self._executed_time)
            self.update_stats.emit(avg_wt, avg_tat)
            self.simulation_done.emit()

        except Exception as e:
            print(f"Simulation crashed: {e}")
            self.running = False

        finally:
            self.running = False
            print("Simulation ended.")

    def sleep_or_mwait(self):
        if self.live:
            time.sleep(self.time_unit)
        else:
            self.msleep(20)

    

    

    def current_sim_time(self):
        return self.current_time

    def stop(self):
        self.running = False
