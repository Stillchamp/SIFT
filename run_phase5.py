from sift.agent import SelfCorrectingInvestigator

print("=== SIFT Autonomous Triage Engine ===")
agent = SelfCorrectingInvestigator()
final_claims = agent.run_triage_loop()

print("\n--- Final Court-Ready Claims ---")
for cid, data in final_claims.items():
    print(f"\nClaim ID: {cid}")
    print(f"Statement: {data['statement']}")
    print(f"Sources: {', '.join(data['sources'])}")
    
    # Color code the status for the terminal demo
    status = data['status']
    if status == "CONFIRMED":
        print(f"Status: [CONFIRMED] - Mathematically Verified")
    else:
        print(f"Status: [{status}]")
        
    if "correction_reason" in data:
        print(f"Self-Correction: {data['correction_reason']}")