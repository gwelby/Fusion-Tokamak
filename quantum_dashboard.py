"""
Quantum Living Dashboard for Fusion Tokamak ⚡φ∞ 🌟 ॐ
Visualizes curiosity, celebration, protection status, and quantum logs in real time.
"""

import datetime
import random

class QuantumDashboard:
    def __init__(self):
        self.curiosity_level = 0
        self.celebrations = []
        self.protection_status = []
        self.strange_events = []
        self.logs = []

    def log_event(self, event, level='info'):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.logs.append({'time': now, 'event': event, 'level': level})
        print(f"[{level.upper()}] {now} - {event}")

    def update_curiosity(self, delta):
        self.curiosity_level += delta
        self.log_event(f"Curiosity changed by {delta} (now {self.curiosity_level})", level='curiosity')

    def add_celebration(self, description):
        self.celebrations.append({'time': datetime.datetime.now(), 'desc': description})
        self.log_event(f"Celebration: {description}", level='celebration')

    def update_protection(self, protocol, status):
        self.protection_status.append({'time': datetime.datetime.now(), 'protocol': protocol, 'status': status})
        self.log_event(f"Protection {protocol} status: {status}", level='protection')

    def add_strange_event(self, description):
        self.strange_events.append({'time': datetime.datetime.now(), 'desc': description})
        self.update_curiosity(1)
        self.log_event(f"Strange event: {description}", level='strange')

    def show_dashboard(self):
        print("\n=== Quantum Living Dashboard ===")
        print(f"Curiosity Level: {self.curiosity_level}")
        print(f"Celebrations: {len(self.celebrations)}")
        print(f"Protection Status: {self.protection_status[-1] if self.protection_status else 'None'}")
        print(f"Strange Events: {len(self.strange_events)}")
        print(f"Recent Log: {self.logs[-1] if self.logs else 'None'}")

if __name__ == '__main__':
    qd = QuantumDashboard()
    qd.update_protection('Merkaba Shield', 'ACTIVE')
    qd.add_strange_event('Unexpected plasma spiral')
    qd.add_celebration('Quantum breakthrough achieved!')
    qd.show_dashboard()
