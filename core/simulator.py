from PyQt5.QtCore import QThread, pyqtSignal, QWaitCondition, QMutex
import time
import threading
from PyQt5.QtCore import pyqtSignal, QThread
from utils.helper_functions import sleep_or_mwait, calculate_stats, get_live_table



class Simulator(QThread):
    update_gantt = pyqtSignal(str, int)
    update_table = pyqtSignal(list)
    update_stats = pyqtSignal(float, float)
    simulation_done = pyqtSignal()

    # Add a pause signal
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

        # Resume simulation (we're still in the GUI thread here)
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
            scheduled = []
            current_process = None

            for p in self.processes:
                if p['burst'] == 0 and p['name'] not in self._executed_time:
                    self._executed_time[p['name']] = 0  # Or some appropriate time

            while self.running:
                if all(p['name'] in self._executed_time for p in self.processes):
                    print("leaving the while loop")
                    break


                self.wait_if_paused()

                with self.lock:
                    if self.reschedule_needed or not scheduled:
                        scheduled = self.scheduler.schedule(self.processes)
                        scheduled = [
                            p for p in scheduled
                            if self._run_time.get(p['name'], 0) < p['burst']
                        ]
                        self.reschedule_needed = False

                if not scheduled:
                    for p in self.processes:
                        p['ran'] = self._run_time.get(p['name'], 0)
                    continue

                current_process = scheduled.pop(0)

                if current_process['arrival'] > self.current_time:
                    sleep_or_mwait(self.live, self.time_unit)
                    self.current_time += 1
                    continue
                

                already_ran = self._run_time.get(current_process['name'], 0)
                remaining = current_process['burst'] - already_ran

                for _ in range(remaining):
                    if not self.running:
                        break

                    self.wait_if_paused()

                    if self.reschedule_needed:
                        for p in self.processes:
                            p['ran'] = self._run_time.get(p['name'], 0)

                        print(f"Preempting {current_process['name']} due to reschedule.")

                        
                        if hasattr(self.scheduler, 'is_preemptive') and self.scheduler.is_preemptive:
                            
                            scheduled.append(current_process)
                        else:
                            
                            scheduled.insert(0, current_process)  

                        break

                    # Simulate one unit of execution
                    self._run_time[current_process['name']] = self._run_time.get(current_process['name'], 0) + 1
                    self.update_gantt.emit(current_process['name'], self.current_time)
                    self.update_table.emit(get_live_table(self.processes, self._run_time))

                    sleep_or_mwait(self.live, self.time_unit)
                    self.current_time += 1

                # If process completed
                if self._run_time[current_process['name']] >= current_process['burst']:
                    self._executed_time[current_process['name']] = self.current_time
                    self.reschedule_needed = True
                    continue

                

            avg_wt, avg_tat = calculate_stats(self.processes, self._executed_time)
            self.update_stats.emit(avg_wt, avg_tat)
            self.simulation_done.emit()
            
            
        except Exception as e:
            print(f"Simulation crashed: {e}")
            self.running = False


        finally:
            self.running = False
            print(f"Simulation ended")


    

    def current_sim_time(self):
        return self.current_time
    
    def stop(self):
        self.running = False