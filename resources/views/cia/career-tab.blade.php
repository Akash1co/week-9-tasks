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

<section class="cia-career-recommendations" aria-labelledby="cia-career-recommendations-title">
    <h2 id="cia-career-recommendations-title">Career recommendations</h2>
    <form id="cia-career-recommendations-form">
        @csrf
        <label for="cia-career-skills">Your skills (comma separated)</label>
        <input id="cia-career-skills" name="skills" type="text" maxlength="1000">

        <label for="cia-career-gaps">Skills to improve (comma separated)</label>
        <input id="cia-career-gaps" name="skill_gaps" type="text" maxlength="1000">

        <label for="cia-career-target-role">Career goal</label>
        <input id="cia-career-target-role" name="target_role" type="text" maxlength="120" required>

        <button type="submit">Recommend career paths</button>
    </form>
    <p id="cia-career-recommendations-status" role="status" aria-live="polite"></p>
    <div id="cia-career-recommendations-results" class="cia-career-paths"></div>
</section>

<style>
    .cia-career-recommendations {
        margin-block: 2rem;
    }

    .cia-career-recommendations form {
        display: grid;
        gap: 0.75rem;
        max-width: 42rem;
    }

    .cia-career-recommendations input {
        padding: 0.6rem;
    }

    .cia-career-recommendations button {
        justify-self: start;
        padding: 0.65rem 1rem;
    }

    .cia-career-paths {
        display: grid;
        gap: 1rem;
        grid-template-columns: repeat(auto-fit, minmax(min(100%, 18rem), 1fr));
        margin-top: 1rem;
    }

    .cia-career-path {
        border: 1px solid #d1d5db;
        border-radius: 0.5rem;
        padding: 1rem;
    }
</style>

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
<script>
    (() => {
        const form = document.getElementById('cia-career-recommendations-form');
        const status = document.getElementById('cia-career-recommendations-status');
        const results = document.getElementById('cia-career-recommendations-results');

        const splitList = (value) => value
            .split(',')
            .map((item) => item.trim())
            .filter(Boolean);

        const appendText = (parent, tag, text) => {
            const element = document.createElement(tag);
            element.textContent = text;
            parent.appendChild(element);
            return element;
        };

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            status.textContent = 'Building your career recommendations...';
            results.replaceChildren();

            try {
                const response = await fetch('/candidate/cia/career/recommendations', {
                    method: 'POST',
                    headers: {
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'X-CSRF-TOKEN': form.querySelector('[name="_token"]').value,
                    },
                    body: JSON.stringify({
                        target_role: form.elements.target_role.value.trim(),
                        skills: splitList(form.elements.skills.value),
                        skill_gaps: splitList(form.elements.skill_gaps.value),
                    }),
                });
                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.message || 'Career recommendations could not be generated.');
                }

                result.career_paths.forEach((path) => {
                    const card = document.createElement('article');
                    card.className = 'cia-career-path';
                    appendText(card, 'h3', path.title);
                    appendText(card, 'p', path.overview);
                    appendText(card, 'h4', 'Required competencies');
                    const competencies = document.createElement('ul');
                    path.required_competencies.forEach((competency) => {
                        appendText(competencies, 'li', competency);
                    });
                    card.appendChild(competencies);
                    appendText(card, 'h4', `Estimated timeframe: ${path.estimated_timeframe}`);
                    appendText(card, 'h4', 'Milestones');
                    const milestones = document.createElement('ol');
                    path.milestones.forEach((milestone) => {
                        appendText(
                            milestones,
                            'li',
                            `${milestone.name} — ${milestone.action} (${milestone.timeframe})`
                        );
                    });
                    card.appendChild(milestones);
                    results.appendChild(card);
                });
                status.textContent = 'Three career paths are ready.';
            } catch (error) {
                status.textContent = error.message;
            }
        });
    })();
</script>
