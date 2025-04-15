import threading
from PyQt5.QtCore import QThread, pyqtSignal
import time
from utils.helper_functions import calculate_stats, get_live_table

class SimulatorPreem(QThread):
    update_gantt = pyqtSignal(str, int)
    update_table = pyqtSignal(list)
    update_stats = pyqtSignal(float, float)
    simulation_done = pyqtSignal()
    process_added = pyqtSignal()

    def __init__(self, scheduler, processes, time_unit=1, live=True, quantum=4):
        super().__init__()
        self.current_time = 0
        self.scheduler = scheduler
        self.processes = processes.copy()
        self.time_unit = time_unit
        self.live = live
        self.quantum = quantum  # Round Robin time quantum
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
            self.update_table.emit(get_live_table(self.processes, self._run_time))
            self.process_added.emit()
            return True

    def run(self):
        try:
            ready_queue = []  # Queue for Round Robin scheduling
            current_process = None
            quantum_counter = 0

            while self.running:
                print(f"Looping: running={self.running}, time={self.current_time}")

                # Check for loop termination BEFORE picking a new process
                all_finished = all(self._run_time.get(p['name'], 0) >= p['burst'] for p in self.processes)
                queue_empty = not ready_queue
                no_current = current_process is None

                print(f"  Termination Check (Start of Loop): all_finished={all_finished}, ready_empty={queue_empty}, no_current={no_current}")

                if all_finished and queue_empty and no_current:
                    print("All processes finished, breaking loop.")
                    break

                # Merge new processes
                with self.lock:
                    if self.new_processes:
                        self.processes.extend(self.new_processes)
                        self.new_processes.clear()
                        self.reschedule_needed = True

                # Add processes to the ready queue based on arrival time
                for proc in self.processes:
                    if(proc['arrival'] <= self.current_time and 
                        proc['name'] not in [p['name'] for p in ready_queue] and 
                        proc['name'] != (current_process['name'] if current_process else None) and 
                        self._run_time.get(proc['name'], 0) < proc['burst']):
                        ready_queue.append(proc)

                if not ready_queue and current_process is None:
                    if self.live:
                        time.sleep(self.time_unit)
                    else:
                        self.msleep(20)
                    self.current_time += 1
                    continue

                if current_process is None and ready_queue:
                    current_process = ready_queue.pop(0)
                    quantum_counter = 0

                if current_process:
                    if not self.running:
                        break

                    print(f"  Executing: {current_process['name']}, burst={current_process['burst']}, run_time={self._run_time.get(current_process['name'], 0)}")

                    # Check if the current process has already finished
                    if self._run_time.get(current_process['name'], 0) >= current_process['burst']:
                        print(f"  {current_process['name']} finished at time {self.current_time}")
                        self._executed_time[current_process['name']] = self.current_time
                        current_process = None
                        quantum_counter = 0
                        continue

                    self._run_time[current_process['name']] = self._run_time.get(current_process['name'], 0) + 1
                    self.update_gantt.emit(current_process['name'], self.current_time)
                    self.update_table.emit(get_live_table(self.processes, self._run_time))

                    if self.live:
                        time.sleep(self.time_unit)
                    else:
                        self.msleep(20)

                    self.current_time += 1
                    quantum_counter += 1

                    if quantum_counter == self.quantum:
                        print(f"  {current_process['name']} quantum expired, adding back to queue.")
                        ready_queue.append(current_process)
                        current_process = None
                        quantum_counter = 0
                        continue
                    elif self._run_time[current_process['name']] == current_process['burst']:
                        print(f"  {current_process['name']} finished at end of quantum.")
                        self._executed_time[current_process['name']] = self.current_time
                        current_process = None
                        quantum_counter = 0

            print("Exited the main loop.")
            # Final stats
            avg_wt, avg_tat = calculate_stats(self.processes, self._executed_time)
            self.update_stats.emit(avg_wt, avg_tat)
            self.simulation_done.emit()
            print("Emitted final stats and simulation done signals.")

        except Exception as e:
            print(f"An error occurred in the run method: {e}")
        finally:
            self.running = False
            print("Run method finished.")


    def start(self):
        print("Simulator thread starting...")
        super().start()
        print(f"Thread running: {self.isRunning()}")

    def stop(self):
        self.running = False

    