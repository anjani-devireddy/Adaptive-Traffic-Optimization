import config


def calculate_traffic_metrics(vehicle_counts):
    """
    Calculate traffic metrics for one camera.

    Parameters
    ----------
    vehicle_counts : dict
        Example:
        {
            "bicycle": 2,
            "motorcycle": 3,
            "car": 10,
            "bus": 1,
            "truck": 2
        }

    Returns
    -------
    dict
        Traffic metrics.
    """

    # ---------------------------------------------------------
    # Total number of vehicles
    # ---------------------------------------------------------

    vehicle_count = sum(
        vehicle_counts.values()
    )

    # ---------------------------------------------------------
    # Weighted traffic score
    # ---------------------------------------------------------

    weighted_score = 0

    for vehicle_type, count in vehicle_counts.items():

        weight = config.VEHICLE_WEIGHTS.get(
            vehicle_type,
            1
        )

        weighted_score += (
            count * weight
        )

    # ---------------------------------------------------------
    # Density
    #
    # Normalized approximately against a
    # 1280 x 720 camera frame.
    # ---------------------------------------------------------

    density = (
        weighted_score / 21.5
        if weighted_score > 0
        else 0
    )

    density = round(
        density,
        3
    )

    # ---------------------------------------------------------
    # Queue score
    #
    # For now the weighted traffic score
    # represents the queue pressure.
    # We can improve this later using
    # vehicle tracking and speed.
    # ---------------------------------------------------------

    queue_score = weighted_score

    # ---------------------------------------------------------
    # Return metrics
    # ---------------------------------------------------------

    return {
        "vehicle_count": vehicle_count,
        "weighted_score": weighted_score,
        "density": density,
        "queue_score": queue_score,
        "vehicle_counts": vehicle_counts.copy(),
    }


# =============================================================
# Simple standalone test
# =============================================================

if __name__ == "__main__":

    test_counts = {
        "bicycle": 2,
        "motorcycle": 3,
        "car": 10,
        "bus": 1,
        "truck": 2,
    }

    metrics = calculate_traffic_metrics(
        test_counts
    )

    print()
    print("# Traffic Metrics")
    print()

    for key, value in metrics.items():

        print(
            f"{key}: {value}"
        )