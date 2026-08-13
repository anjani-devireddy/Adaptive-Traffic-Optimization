from signal_controller import SignalController


controller = SignalController(4)

controller.update_traffic([
    10,   # North
    50,   # East
    20,   # South
    5,    # West
])

state = controller.get_state()

print()
print("Adaptive Intersection Test")
print("=" * 40)

print(
    "Camera scores:",
    [10, 50, 20, 5]
)

print(
    "Phase scores:",
    state["phase_scores"]
)

print(
    "Green times:",
    state["green_times"]
)

controller.set_phase(0)

print(
    "North/South:",
    controller.get_state()["signal_colors"]
)

controller.set_phase(1)

print(
    "East/West:",
    controller.get_state()["signal_colors"]
)