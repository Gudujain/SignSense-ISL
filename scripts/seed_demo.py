"""Seed fictional demo history. Use only for developer presentations."""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.engine.demo_seed import seed_demo_history

if __name__ == "__main__":
    result = seed_demo_history()
    print(f"Seeded {result['sessions']} demo sessions and {result['attempts']} fictional demo attempts.")
    print("Demo rows are tagged and isolated from ordinary learner progress.")
