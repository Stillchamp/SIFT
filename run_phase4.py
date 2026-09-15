from sift.clock_drift import ClockDriftNormalizer

print("[*] Initializing Clock Drift Normalizer...")
normalizer = ClockDriftNormalizer()

# 1. Simulate a Network Connection log (The Reference Time)
# The C2 beacon to IP 203.0.113.50 happened at epoch 1788098000
normalizer.add_observation(source="network_log", anchor_value="203.0.113.50", timestamp_epoch=1788098000)

# 2. Simulate a Windows EVTX Logon Event (The Target Time)
# The server logged a connection from that same IP, but its clock is slow!
# It logged it at 1788097880 (120 seconds earlier)
normalizer.add_observation(source="windows_evtx", anchor_value="203.0.113.50", timestamp_epoch=1788097880)

# 3. Calculate the Drift
drift_result = normalizer.detect_and_calculate_drift(reference_source="network_log", target_source="windows_evtx")

if drift_result:
    print("\n--- Clock Drift Analysis ---")
    print(f"[*] Anchor Matched: {drift_result['anchor_matched']}")
    print(f"[*] Reference Time (Network): {drift_result['reference_time']}")
    print(f"[*] Target Time (EVTX): {drift_result['target_time']}")
    print(f"[*] Calculated Delta: +{drift_result['delta_seconds']} seconds")
    print(f"[*] Action: SIFT will automatically add {drift_result['delta_seconds']}s to all EVTX logs to align the timeline.")