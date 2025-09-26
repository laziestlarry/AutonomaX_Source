
from orchestrator.orchestrator import Orchestrator
from orchestrator.schemas import Task

def test_routes():
    orch = Orchestrator()
    t = Task(type="lead_score", payload={"email":"a@b.c"})
    out = orch.run(t)
    assert isinstance(out, dict)
if __name__ == "__main__":
    test_routes()
    print("OK")
