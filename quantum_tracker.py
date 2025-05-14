"""
Quantum Project Tracker & Manager ⚡φ∞ 🌟 ॐ
Tracks progress, coherence, and celebration states for all quantum projects and subsystems.
"""

import datetime

class QuantumProjectTracker:
    def __init__(self):
        self.projects = []

    def add_project(self, name, status='Planned'):
        self.projects.append({'name': name, 'status': status, 'created': datetime.datetime.now()})
        print(f"[Tracker] Project '{name}' added with status '{status}'")

    def update_status(self, name, status):
        for p in self.projects:
            if p['name'] == name:
                p['status'] = status
                print(f"[Tracker] Project '{name}' status updated to '{status}'")
                return
        print(f"[Tracker] Project '{name}' not found")

    def show_projects(self):
        print("\n=== Quantum Project Tracker ===")
        for p in self.projects:
            print(f"- {p['name']} | Status: {p['status']} | Created: {p['created']}")

if __name__ == '__main__':
    qpt = QuantumProjectTracker()
    qpt.add_project('Fusion Tokamak')
    qpt.update_status('Fusion Tokamak', 'Active')
    qpt.show_projects()
