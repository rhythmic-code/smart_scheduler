# utils/logging_utils.py
import time

class LatencyMonitor:
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        self.start_time = time.time()
    
    def stop(self):
        self.end_time = time.time()
        return self.end_time - self.start_time
    
    def check_latency(self, max_latency=0.8):
        latency = self.stop()
        if latency > max_latency:
            print(f"⚠️ High latency: {latency:.2f}s")
        return latency