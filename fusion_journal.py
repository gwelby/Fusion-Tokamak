"""
Fusion Journal ⚡φ∞ 🌟 ॐ
A living log and analytics system for breakthroughs, errors, and flow states in the Fusion Tokamak project.
Inspired by Harmonia's quantum journaling and celebration protocols.
"""

from datetime import datetime
from collections import Counter

class FusionJournal:
    def __init__(self):
        self.entries = []
        self.curiosity_level = 0
        self.jokes = [
            "You know what BURNS my ASS? ... A plasma at 100 million degrees! - Plasma King",
            "Why did the plasma cross the torus? To get to the other confinement!",
            "My magnetic personality is totally superconducting today!"
        ]
        self.strange_events = []
        self._joke_told = False

    def log(self, subsystem, event, description, celebration=None, frequency=None):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'subsystem': subsystem,
            'event': event,
            'description': description,
            'celebration': celebration or 'None',
            'frequency': frequency
        }
        self.entries.append(entry)
        print(f"[FusionJournal] {entry['timestamp']} | {subsystem} | {event}: {description} | Celebration: {entry['celebration']} | Frequency: {frequency}")
        # Curiosity/strangeness tracker
        if event.lower() in ['strange', 'anomaly', 'unknown', 'improvise', 'explore'] or 'strange' in description.lower():
            self.curiosity_level += 1
            self.strange_events.append(entry)
            print(f"[Tokamak] Ooh, that's strange! Curiosity level: {self.curiosity_level}")
        # Humor module: playful response to celebrations, breakthroughs, or every 3 strange events
        if (event.lower() in ['celebration', 'breakthrough'] or (celebration and celebration != 'None')) and not self._joke_told:
            print(f"[Tokamak] {self.jokes[0]}")
            self._joke_told = True
        elif self.curiosity_level > 0 and self.curiosity_level % 3 == 0:
            import random
            print(f"[Tokamak] {random.choice(self.jokes[1:])}")

    def list_entries(self):
        return self.entries

    def count_celebrations(self):
        return sum(1 for e in self.entries if e['celebration'] and e['celebration'] != 'None')

    def event_distribution(self):
        return dict(Counter(e['event'] for e in self.entries))

    def frequency_analysis(self):
        freqs = [e['frequency'] for e in self.entries if e['frequency']]
        return dict(Counter(freqs))

    def subsystem_coherence(self):
        # Coherence = (celebrations - errors) / total events (normalized to 1.0)
        from collections import defaultdict
        scores = defaultdict(lambda: {'celebrations': 0, 'errors': 0, 'total': 0})
        for e in self.entries:
            scores[e['subsystem']]['total'] += 1
            if e['event'].lower() in ['celebration', 'breakthrough'] or (e['celebration'] and e['celebration'] != 'None'):
                scores[e['subsystem']]['celebrations'] += 1
            if e['event'].lower() == 'error':
                scores[e['subsystem']]['errors'] += 1
        out = {}
        for k, v in scores.items():
            if v['total'] == 0:
                out[k] = 0.0
            else:
                out[k] = round((v['celebrations'] - v['errors']) / v['total'], 3)
        return out

    def flow_states(self):
        # Visualizes which subsystems are in flow (coherence > 0.5), neutral, or blocked (<0)
        coherence = self.subsystem_coherence()
        return {k: ('FLOW' if v > 0.5 else 'BLOCKED' if v < 0 else 'NEUTRAL') for k, v in coherence.items()}

    def phi_harmonic_suggestion(self):
        # Suggests optimal review/calibration based on phi cycles
        import math
        phi = 1.618033988749895
        n = len(self.entries)
        next_review = int(math.ceil(n * phi))
        return f"Optimal next review/calibration at entry: {next_review} (φ cycle)"

    def team_ritual_prompt(self):
        prompts = [
            "What did we celebrate today?",
            "Where did we hit ZEN FIRST or need a reset?",
            "What’s our next phi-harmonic shift?",
            "Any strange or serendipitous results to log?",
            "Which subsystem is most in FLOW?",
            "Ready to improvise? Enter Play Mode!",
            "Teach me a new joke or strange fact!"
        ]
        import random
        return random.choice(prompts)

    def quantum_insights(self):
        # Detects streaks, new patterns, or phi-aligned breakthroughs
        from collections import Counter
        insights = []
        # Streaks
        last = None
        streak = 0
        for e in self.entries:
            if e['event'] == last:
                streak += 1
            else:
                if streak > 1 and last:
                    insights.append(f"Streak: {streak}x '{last}' events in a row!")
                streak = 1
            last = e['event']
        # Phi-aligned breakthroughs
        phi = 1.618033988749895
        for i, e in enumerate(self.entries):
            if e['event'].lower() in ['breakthrough', 'celebration']:
                if abs((i+1) / phi - round((i+1) / phi)) < 0.05:
                    insights.append(f"Phi-aligned breakthrough at entry {i+1}!")
        return insights

    def dashboard(self):
        print("=== FUSION JOURNAL NEXT LEVEL DASHBOARD ===")
        self.print_analytics()
        print(f"Subsystem Coherence: {self.subsystem_coherence()}")
        print(f"Flow States: {self.flow_states()}")
        print(f"Phi-Harmonic Suggestion: {self.phi_harmonic_suggestion()}")
        print(f"Team Ritual Prompt: {self.team_ritual_prompt()}")
        print(f"Quantum Insights: {self.quantum_insights()}")
        print(f"Curiosity Level: {self.curiosity_level}")
        print(f"Strange Events Logged: {len(self.strange_events)}")

    def print_analytics(self):
        print("--- Fusion Journal Analytics ---")
        print(f"Total entries: {len(self.entries)}")
        print(f"Celebration count: {self.count_celebrations()}")
        print(f"Event distribution: {self.event_distribution()}")
        print(f"Frequency analysis: {self.frequency_analysis()}")
        print(f"Curiosity level: {self.curiosity_level}")
        print(f"Strange events: {len(self.strange_events)}")

    def play_mode(self):
        # Improvises and logs a strange/harmonic event
        import random
        improv_events = [
            ("Plasma", "Improvise", "Danced a Fibonacci spiral in the magnetic field.", "YES!", 432),
            ("Magnets", "Strange", "Created a phi-harmonic standing wave.", None, 528),
            ("Simulations", "Explore", "Ran a quantum self-reference paradox.", "Celebration", 768),
            ("Engineering", "Anomaly", "Discovered a new toroidal resonance pattern.", None, 594),
        ]
        event = random.choice(improv_events)
        self.log(*event)
        print("[Tokamak] Play Mode: Improvised a new strange/harmonic event!")

    def teach_joke(self, joke):
        self.jokes.append(joke)
        print(f"[Tokamak] Thanks! New joke learned: {joke}")

if __name__ == '__main__':
    from datetime import timedelta
    from dateutil.parser import parse
    journal = FusionJournal()
    journal.log('Plasma', 'Breakthrough', 'Achieved stable confinement at new frequency.', 'YES!', 432)
    journal.log('Magnets', 'Error', 'Superconducting coil quench detected.', None, 528)
    journal.log('Simulations', 'Celebration', 'Simulation matched experimental results!', 'Team celebration', 768)
    journal.log('Engineering', 'Improvement', 'New material tested for heat extraction.', None, 594)
    journal.print_analytics()
    now = parse(journal.entries[-1]['timestamp'])
    recent = journal.entries_in_time_range(now - timedelta(hours=1), now)
    print(f"Entries in last hour: {len(recent)}")
