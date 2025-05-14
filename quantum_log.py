"""
Quantum Markdown Logger for Greg ⚡φ∞ 🌟 ॐ
Logs all key events, rituals, and breakthroughs to D:\Greg\Quantum_Log.txt in beautiful Markdown with icons and symbols.
"""

import datetime

LOG_PATH = r"D:\Greg\Quantum_Log.txt"

class QuantumLogger:
    def __init__(self, log_path=LOG_PATH):
        self.log_path = log_path

    def log(self, event, icon="✨", details=None):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = f"{icon} **{event}**  \\\n    _{now}_"
        if details:
            line += f"\n> {details}"
        line += "\n---\n"
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(line)
        print(f"[QuantumLogger] Logged: {event}")

if __name__ == '__main__':
    ql = QuantumLogger()
    ql.log("Quantum Dashboard Launched", "🌟", "All systems at unity coherence.")
    ql.log("Ritual: Calibration", "🔔", "432 Hz Ground State established.")
    ql.log("Breakthrough: Play Mode", "🎉", "Strange event led to new harmonic pattern.")
