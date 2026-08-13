console.log("Dashboard JavaScript loaded.");

async function updateTrafficData() {

    try {

        const response = await fetch("/traffic-data?t=" + Date.now());

        if (!response.ok) {
            throw new Error("HTTP " + response.status);
        }

        const result = await response.json();

        console.log("API RESPONSE:", result);

        const cameras = result.cameras || [];

        let totalVehicles = 0;
        let totalScore = 0;

        let highestScore = -1;
        let highestCamera = "--";


        cameras.forEach(camera => {

            const id = camera.camera_id;

            const vehicles = Number(camera.vehicle_count || 0);
            const score = Number(camera.weighted_score || 0);
            const density = Number(camera.density || 0);
            const greenTime = Number(camera.green_time || 0);
            const signal = camera.signal_color || "Red";

            console.log(
                "Camera",
                id,
                "Vehicles:",
                vehicles,
                "Score:",
                score
            );


            totalVehicles += vehicles;
            totalScore += score;


            if (score > highestScore) {
                highestScore = score;
                highestCamera = camera.name || ("Camera " + id);
            }


            const card = document.querySelector(
                '.camera-card[data-camera-id="' + id + '"]'
            );

            if (!card) {
                console.error("CARD NOT FOUND:", id);
                return;
            }


            const vehicleElement =
                card.querySelector(".vehicle-count");

            const scoreElement =
                card.querySelector(".traffic-score");

            const densityElement =
                card.querySelector(".density");

            const greenElement =
                card.querySelector(".green-time");

            const signalElement =
                card.querySelector(".signal");


            if (vehicleElement) {
                vehicleElement.textContent = vehicles;
            }

            if (scoreElement) {
                scoreElement.textContent = score;
            }

            if (densityElement) {
                densityElement.textContent = density.toFixed(3);
            }

            if (greenElement) {
                greenElement.textContent = greenTime + "s";
            }

            if (signalElement) {
                signalElement.textContent = signal;

                signalElement.className =
                    "signal " + signal.toLowerCase();
            }

        });


        document.getElementById("total-vehicles").textContent =
            totalVehicles;

        document.getElementById("total-score").textContent =
            totalScore;

        document.getElementById("highest-traffic").textContent =
            highestScore >= 0
                ? highestCamera + " (" + highestScore + ")"
                : "--";


    } catch (error) {

        console.error(
            "TRAFFIC DATA ERROR:",
            error
        );

    }
}


// Run immediately
updateTrafficData();

// Update every second
setInterval(updateTrafficData, 1000);