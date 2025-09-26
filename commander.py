"""CLI helper for AutonomaX Orchestrator."""
import argparse
import json

from orchestrator.orchestrator import Orchestrator


def main() -> None:
    parser = argparse.ArgumentParser(description="Run AutonomaX command agent")
    parser.add_argument("message", nargs="*", help="Command payload to route")
    args = parser.parse_args()
    msg = " ".join(args.message) or "status"
    orch = Orchestrator()
    result = orch.handle(msg)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
