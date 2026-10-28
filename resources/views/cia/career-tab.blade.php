<section class="cia-skill-gap" aria-labelledby="cia-skill-gap-title">
    <h2 id="cia-skill-gap-title">Skill gap analysis</h2>

    <form id="cia-skill-gap-form">
        @csrf
        <label for="cia-target-role">Target role</label>
        <input
            id="cia-target-role"
            name="target_role"
            type="text"
            value="Full Stack Developer"
            maxlength="120"
            required
        >
        <button type="submit">Analyze skill gap</button>
    </form>

    <p id="cia-skill-gap-status" role="status" aria-live="polite"></p>
    <p id="cia-skill-gap-score"></p>
    <ul id="cia-skill-gap-list"></ul>
    <div style="max-width: 640px;">
        <canvas id="cia-skill-gap-radar" aria-label="Candidate skills compared with target-role benchmarks"></canvas>
    </div>
</section>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
    (() => {
        const form = document.getElementById('cia-skill-gap-form');
        const status = document.getElementById('cia-skill-gap-status');
        const score = document.getElementById('cia-skill-gap-score');
        const gaps = document.getElementById('cia-skill-gap-list');
        const canvas = document.getElementById('cia-skill-gap-radar');
        let radarChart = null;

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            status.textContent = 'Analyzing your skill profile...';
            score.textContent = '';
            gaps.replaceChildren();

            try {
                const response = await fetch('/candidate/cia/career/skill-gap', {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': form.querySelector('[name="_token"]').value,
                    },
                    body: JSON.stringify({
                        target_role: form.elements.target_role.value,
                    }),
                });
                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.message || 'Skill-gap analysis failed.');
                }

                score.textContent = `Readiness score: ${result.score}/100`;
                (result.gaps || []).forEach((gap) => {
                    const item = document.createElement('li');
                    item.textContent = gap;
                    gaps.appendChild(item);
                });

                if (!window.Chart) {
                    throw new Error('Chart.js did not load, so the radar chart cannot be displayed.');
                }

                if (radarChart) {
                    radarChart.destroy();
                }

                radarChart = new Chart(canvas, {
                    type: 'radar',
                    data: {
                        labels: result.radar_data.labels,
                        datasets: [
                            {
                                label: 'Candidate',
                                data: result.radar_data.candidate_scores,
                                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                                borderColor: 'rgb(54, 162, 235)',
                            },
                            {
                                label: 'Target role',
                                data: result.radar_data.target_scores,
                                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                                borderColor: 'rgb(255, 99, 132)',
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        scales: {
                            r: {
                                min: 0,
                                max: 100,
                                ticks: { stepSize: 20 },
                            },
                        },
                    },
                });
                status.textContent = 'Analysis complete.';
            } catch (error) {
                status.textContent = error.message;
            }
        });
    })();
</script>
