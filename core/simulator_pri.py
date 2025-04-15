# core/simulator.py
import threading
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QWaitCondition
import time
from utils.helper_functions import sleep_or_mwait, calculate_stats, get_live_table

class SimulatorPriority(QThread):
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
        self.paused = False
        self.lock = threading.Lock()
        self.new_processes = []
        self._executed_time = {}
        self._run_time = {}
        self.reschedule_needed = True

        # For pause/resume functionality
        self.mutex = QMutex()
        self.pause_condition = QWaitCondition()

        self.process_added.connect(self.on_new_process)

    def on_new_process(self):
        self.reschedule_needed = True

    def add_process(self, process):
        print(f"Request to add: {process['name']}")
        self.paused = True
        with self.lock:
            if any(p['name'] == process['name'] for p in self.processes + self.new_processes):
                print(f"Duplicate: {process['name']}")
                self.paused = False
                self.pause_condition.wakeAll()
                return False

            print(f"Added: {process['name']}")
            self.new_processes.append(process)
            self.processes.extend(self.new_processes)
            self.new_processes.clear()
            self.reschedule_needed = True
            self.update_table.emit(get_live_table(self.processes, self._run_time))

        self.paused = False
        self.pause_condition.wakeAll()
        return True

    def wait_if_paused(self):
        self.mutex.lock()
        while self.paused:
            print("Simulation paused. Waiting...")
            self.pause_condition.wait(self.mutex)
        self.mutex.unlock()

    def run(self):
        try:
            ready_queue = []
            self.current_process = None

            while self.running:
                self.wait_if_paused()

                # Add new processes to the ready queue
                with self.lock:
                    for proc in self.new_processes:
                        ready_queue.append(proc)
                    self.new_processes.clear()

                # Add arrived processes to the ready queue
                for proc in self.processes:
                    if proc not in ready_queue and self._run_time.get(proc['name'], 0) < proc['burst'] and proc['arrival'] <= self.current_time:
                        ready_queue.append(proc)

                if self.reschedule_needed or self.current_process is None:
                    if ready_queue:
                        ready_queue.sort(key=lambda p: p.get('priority', float('inf')))
                        if (self.scheduler.is_preemptive and self.current_process is not None and
                             ready_queue[0].get('priority', float('inf')) < self.current_process.get('priority', float('inf')) and
                             self._run_time.get(self.current_process['name'], 0) < self.current_process['burst']):
                            print(f"Preempting {self.current_process['name']} for {ready_queue[0]['name']} at time {self.current_time}")
                            ready_queue.append(self.current_process)
                            self.current_process = ready_queue.pop(0)
                        elif self.current_process is None and ready_queue:
                            self.current_process = ready_queue.pop(0)
                        elif ready_queue and self.current_process and self._run_time.get(self.current_process['name'], 0) >= self.current_process['burst']:
                            self.current_process = None
                            continue
                        elif self.current_process is None and not ready_queue:
                            pass
                        elif self.current_process and not ready_queue and self._run_time.get(self.current_process['name'], 0) < self.current_process['burst']:
                            pass
                        elif ready_queue and self.current_process and ready_queue[0] == self.current_process:
                            pass
                        elif ready_queue and not self.current_process:
                            self.current_process = ready_queue.pop(0)
                    self.reschedule_needed = False

                if self.current_process:
                    # Check if the current process has finished BEFORE executing the next time unit
                    if self._run_time.get(self.current_process['name'], 0) >= self.current_process['burst']:
                        self._executed_time[self.current_process['name']] = self.current_time
                        self.current_process = None
                        self.reschedule_needed = True
                        continue # Skip the execution part for this iteration

                    # Execute the current process
                    self._run_time[self.current_process['name']] = self._run_time.get(self.current_process['name'], 0) + 1
                    self.update_gantt.emit(self.current_process['name'], self.current_time)
                    self.update_table.emit(get_live_table(self.processes, self._run_time))
                    sleep_or_mwait(self.live, self.time_unit)
                    self.current_time += 1
                    self.reschedule_needed = True

                else:
                    sleep_or_mwait(self.live, self.time_unit)
                    self.current_time += 1

                if all(self._run_time.get(p['name'], 0) >= p['burst'] for p in self.processes) and not ready_queue and self.current_process is None:
                    print("All processes completed.")
                    break

            avg_wt, avg_tat = calculate_stats(self.processes, self._executed_time)
            self.update_stats.emit(avg_wt, avg_tat)
            self.simulation_done.emit()

        except Exception as e:
            print(f"Simulation crashed: {e}")
            self.running = False
        finally:
            self.running = False
            print("Simulation ended")


    def start(self):
        print("Simulator thread starting...")
        super().start()
        print(f"Thread running: {self.isRunning()}")

    def stop(self):
        self.running = False

  
