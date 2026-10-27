"""
cli.py - Single Command CLI Entrypoint for CodeShift

Usage:
  python src/cli.py sample_project        # Runs full multi-agent migration
  python src/cli.py sample_project --web  # Runs migration and launches Web Dashboard
"""

import sys
import os
import argparse
import subprocess

src_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(src_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from agents.orchestrator import MigrationOrchestrator
from agents.evaluator import BehavioralEvaluator


def main():
    parser = argparse.ArgumentParser(description="CodeShift - Multi-Agent Java to Python Project Migration CLI")
    parser.add_argument("repo_path", nargs="?", default="sample_project", help="Path to input Java project folder.")
    parser.add_argument("--web", action="store_true", help="Launch interactive Web Dashboard.")

    args = parser.parse_args()

    print("==================================================================")
    print(" [CODESHIFT] MULTI-AGENT MIGRATION CLI")
    print("==================================================================")

    abs_repo = os.path.abspath(os.path.join(root_dir, args.repo_path))
    if not os.path.exists(abs_repo):
        abs_repo = os.path.abspath(args.repo_path)

    output_dir = os.path.join(root_dir, "output")

    print(f"Target Java Repository Path: '{abs_repo}'")
    print(f"Target Python Output Directory: '{output_dir}'")

    # Run ADK Migration Orchestrator
    orchestrator = MigrationOrchestrator(repo_dir=abs_repo, output_dir=output_dir)
    report = orchestrator.run_full_migration()

    print("\n[CLI MIGRATION SUMMARY]")
    summary = report.manifest_summary if hasattr(report, "manifest_summary") else report.get("manifest_summary", {})
    print(f"Translated: {summary.get('TRANSLATE', 0)} files")
    print(f"Transformed: {summary.get('TRANSFORM', 0)} files")
    print(f"Dropped:     {summary.get('DROP', 0)} files")

    if args.web:
        print("\n[Launching CodeShift Web Dashboard on http://localhost:8080 ...]")
        dashboard_script = os.path.join(src_dir, "web", "dashboard.py")
        subprocess.run([sys.executable, dashboard_script])


if __name__ == "__main__":
    main()
