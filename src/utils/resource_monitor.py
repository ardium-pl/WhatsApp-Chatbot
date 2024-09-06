import psutil
import time
from threading import Thread


class ResourceMonitor(Thread):
    def __init__(self, interval=5, cpu_threshold=80, memory_threshold=80):
        super().__init__()
        self.interval = interval
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.running = True

    def run(self):
        while self.running:
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent

            print(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")

            if cpu_usage > self.cpu_threshold or memory_usage > self.memory_threshold:
                print("High resource usage detected. Consider scaling or optimizing.")

            time.sleep(self.interval)

    def stop(self):
        self.running = False

    def is_overloaded(self):
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        return cpu_usage > self.cpu_threshold or memory_usage > self.memory_threshold
