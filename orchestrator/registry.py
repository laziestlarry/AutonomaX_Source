from agents.customer_service.agent import CustomerServiceAgent

def get_agent(name: str):
    if name == "customer_service":
        return CustomerServiceAgent(policy_path="config/policies/customer_service.yml")
    raise ValueError(f"Unknown agent: {name}")
