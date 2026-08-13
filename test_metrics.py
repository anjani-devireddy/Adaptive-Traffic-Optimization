from metrics import calculate_metrics


test_counts = {
    "bicycle": 2,
    "motorcycle": 3,
    "car": 10,
    "bus": 1,
    "truck": 2,
}


metrics = calculate_metrics(test_counts)

print()
print("Traffic Metrics")
print("=" * 40)

for key, value in metrics.items():
    print(f"{key}: {value}")