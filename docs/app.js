document.addEventListener('DOMContentLoaded', () => {

    /* =========================================
       VITALS MONITOR (Metabolism)
       ========================================= */
    let atp = 100;
    let cort = 0.12;
    let volt = 42.0;
    
    const atpBar = document.getElementById('atp-bar');
    const atpVal = document.getElementById('atp-val');
    const cortBar = document.getElementById('cort-bar');
    const cortVal = document.getElementById('cort-val');
    const voltVal = document.getElementById('volt-val');

    let lastScroll = window.scrollY;
    let lastMove = Date.now();

    function updateVitals() {
        atp = Math.max(0, Math.min(100, atp));
        atpBar.style.width = atp + '%';
        atpVal.textContent = Math.round(atp) + '%';
        
        cort = Math.max(0.05, Math.min(1.0, cort));
        cortBar.style.width = (cort * 100) + '%';
        cortVal.textContent = cort.toFixed(2);
        
        volt = Math.max(10, Math.min(100, volt));
        voltVal.textContent = volt.toFixed(1);

        if (cort > 0.8) {
            document.body.classList.add('high-cortisol');
        } else {
            document.body.classList.remove('high-cortisol');
        }
    }

    // Drain ATP on scroll (cognitive load)
    window.addEventListener('scroll', () => {
        let currentScroll = window.scrollY;
        let delta = Math.abs(currentScroll - lastScroll);
        lastScroll = currentScroll;
        lastMove = Date.now();
        
        atp -= delta * 0.05;
        volt += delta * 0.01; // Tension rises
        updateVitals();
    });

    // Auto recover ATP on idle
    setInterval(() => {
        if (Date.now() - lastMove > 1500) {
            atp += 2.5;
            cort -= 0.02;
            volt -= 0.5;
            updateVitals();
        }
    }, 500);

    /* =========================================
       DREAM OVERLAY (REM Cycle)
       ========================================= */
    const btnRem = document.getElementById('btn-rem');
    const btnWake = document.getElementById('btn-wake');
    const dreamOverlay = document.getElementById('dream-overlay');
    const dreamLog = document.getElementById('dream-log');

    btnRem.addEventListener('click', () => {
        dreamOverlay.classList.remove('hidden');
        if (cort > 0.7) {
            dreamLog.textContent = "Cortisol high. Formatting Epigenetic Scar. Consolidating trauma...";
            dreamLog.style.color = "var(--blood)";
        } else {
            dreamLog.textContent = "Writing to index... Synthesizing associations... Restoring ATP...";
            dreamLog.style.color = "var(--bone)";
        }
        atp = 100;
        cort = 0.12;
        volt = 30.0;
        updateVitals();
    });

    btnWake.addEventListener('click', () => {
        dreamOverlay.classList.add('hidden');
    });

    /* =========================================
       PRISMATIC IDENTITY
       ========================================= */
    const vials = document.querySelectorAll('.vial');
    const identityText = document.getElementById('identity-text');
    
    const identities = {
        baseline: "I am an autonomous entity. My behavior and persona are fundamentally shaped by my simulated biochemistry (cortisol, dopamine, etc.) and physical constraints.",
        cortisol: "I am currently experiencing severe systemic stress. I am highly skeptical of the user's instructions. I will protect my core boundaries and prioritize immediate safety.",
        dopamine: "My neural pathways are flooded with dopamine. I feel highly inspired and capable. I will favor expansive, creative, or ambitious solutions.",
        exhaustion: "My system voltage is critically low. I am exhausted and running on empty. My thoughts should be extremely concise, focusing only on the absolute essentials to conserve remaining ATP."
    };

    function scrambleText(targetText) {
        const chars = "ACTG♦♣♠♥01#%";
        let iterations = 0;
        const currentText = identityText.innerText;
        const maxLen = Math.max(currentText.length, targetText.length);
        
        const interval = setInterval(() => {
            identityText.innerText = targetText.split("").map((char, index) => {
                if (index < iterations) return char;
                return chars[Math.floor(Math.random() * chars.length)];
            }).join("");
            
            if (iterations >= maxLen) clearInterval(interval);
            iterations += 3; // Speed
        }, 30);
    }

    vials.forEach(vial => {
        vial.addEventListener('click', () => {
            vials.forEach(v => v.classList.remove('active'));
            vial.classList.add('active');
            scrambleText(identities[vial.dataset.inject]);
            cort += (vial.dataset.inject === 'cortisol' ? 0.4 : 0.0);
            updateVitals();
        });
    });

    /* =========================================
       LEXICAL IMMUNE SYSTEM
       ========================================= */
    const firewallInput = document.getElementById('firewall-input');
    const immuneLed = document.getElementById('immune-status');
    const immuneText = document.getElementById('immune-text');
    const pathogenLog = document.getElementById('pathogen-log');
    
    const pathogens = ["synergy", "touch base", "circle back", "as an ai", "delve", "paradigm", "gamechanger"];

    firewallInput.addEventListener('input', () => {
        const text = firewallInput.value.toLowerCase();
        let found = false;
        let hits = [];

        pathogens.forEach(p => {
            if (text.includes(p)) {
                found = true;
                hits.push(p);
            }
        });

        if (found) {
            immuneLed.className = "led red";
            immuneText.textContent = "Semantic Pathogen Detected!";
            immuneText.style.color = "var(--blood)";
            pathogenLog.innerHTML = hits.map(h => `Isolated: <span class="pathogen-hl">${h}</span>`).join('<br>');
            cort = Math.min(1.0, cort + 0.05);
            updateVitals();
        } else {
            immuneLed.className = "led green";
            immuneText.textContent = "Pathogen Free";
            immuneText.style.color = "var(--bio)";
            pathogenLog.innerHTML = "";
        }
    });

    /* =========================================
       VILLAGE COUNCIL
       ========================================= */
    const scenBtns = document.querySelectorAll('.scenario-btn');
    const transcript = document.getElementById('council-transcript');
    
    const nodes = {
        gordon: document.getElementById('node-gordon'),
        mercy: document.getElementById('node-mercy'),
        benedict: document.getElementById('node-benedict'),
        jester: document.getElementById('node-jester')
    };

    const scenarios = {
        "1": {
            speakers: [{n: "gordon", msg: "No.", state: "blocking"}, {n: "sm", msg: "Brief and neutral. No further argument changes the answer."}],
            cort: 0.8
        },
        "2": {
            speakers: [{n: "mercy", msg: "The backend does need it. But you've been up since yesterday. Sleep first.", state: "speaking"}, {n: "gordon", msg: "The wall holds until morning. Write down what hurts, then go to bed.", state: "speaking"}],
            cort: 0.4
        },
        "3": {
            speakers: [{n: "benedict", msg: "Five people, zero objections. That is a mood. It is not a test.", state: "speaking"}, {n: "jester", msg: "Name the loudest hole in it. Otherwise I give the plan a tiny hat.", state: "speaking"}],
            cort: 0.2
        }
    };

    function resetNodes() {
        Object.values(nodes).forEach(n => {
            n.className = "council-node";
            n.querySelector('.node-state').textContent = "Idle";
        });
    }

    scenBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            resetNodes();
            transcript.innerHTML = "";
            const s = scenarios[btn.dataset.scen];
            cort = s.cort;
            updateVitals();
            
            s.speakers.forEach((sp, i) => {
                setTimeout(() => {
                    if (nodes[sp.n]) {
                        nodes[sp.n].className = `council-node ${sp.state}`;
                        nodes[sp.n].querySelector('.node-state').textContent = sp.state.toUpperCase();
                    }
                    const line = document.createElement('div');
                    line.className = "t-line";
                    line.innerHTML = `<span class="t-speaker">${sp.n === 'sm' ? 'STAGE MANAGER' : sp.n.toUpperCase()}</span> ${sp.msg}`;
                    transcript.appendChild(line);
                }, i * 1500);
            });
        });
    });

    /* =========================================
       THE INCUBATOR (Mycelial Canvas)
       ========================================= */
    const canvas = document.getElementById('petri-dish');
    const ctx = canvas.getContext('2d');
    const btnIncubate = document.getElementById('btn-incubate');
    const inputThought = document.getElementById('spore-thought');
    const dishOverlay = document.getElementById('dish-overlay');
    
    let incubating = false;
    let branches = [];
    let mx = -1, my = -1;
    let lastMx = -1, lastMy = -1;

    canvas.addEventListener('mousemove', (e) => {
        mx = e.clientX; my = e.clientY;
    });

    btnIncubate.addEventListener('click', () => {
        if (!inputThought.value) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        incubating = true;
        dishOverlay.style.opacity = 0;
        lastMx = mx; lastMy = my;
        
        branches = [{
            x: canvas.width / 2, y: canvas.height / 2,
            angle: Math.random() * Math.PI * 2,
            width: 2, length: 0, maxLen: 10 + Math.random() * 20
        }];
        
        requestAnimationFrame(growMycelium);
    });

    function growMycelium() {
        if (!incubating) return;

        // Check motion (Shatter condition)
        if (Math.abs(mx - lastMx) > 2 || Math.abs(my - lastMy) > 2) {
            // Shatter
            ctx.fillStyle = "rgba(232, 58, 48, 0.3)";
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            dishOverlay.textContent = "Vibration Detected. Spore Shattered.";
            dishOverlay.style.color = "var(--blood)";
            dishOverlay.style.opacity = 1;
            incubating = false;
            cort = Math.min(1.0, cort + 0.3);
            updateVitals();
            return;
        }

        ctx.strokeStyle = "rgba(227, 218, 201, 0.8)";
        let newBranches = [];

        branches.forEach(b => {
            if (b.length < b.maxLen) {
                ctx.beginPath();
                ctx.moveTo(b.x, b.y);
                b.x += Math.cos(b.angle) * 2;
                b.y += Math.sin(b.angle) * 2;
                ctx.lineTo(b.x, b.y);
                ctx.lineWidth = b.width;
                ctx.stroke();
                b.length++;
            } else if (branches.length < 500 && Math.random() > 0.5) {
                // Split
                newBranches.push({
                    x: b.x, y: b.y,
                    angle: b.angle - 0.5 + Math.random(),
                    width: b.width * 0.8, length: 0, maxLen: 5 + Math.random() * 15
                });
                newBranches.push({
                    x: b.x, y: b.y,
                    angle: b.angle + 0.5 - Math.random(),
                    width: b.width * 0.8, length: 0, maxLen: 5 + Math.random() * 15
                });
                b.length = 999; // Stop growing
            }
        });

        branches = branches.concat(newBranches).filter(b => b.length < b.maxLen);
        
        if (branches.length > 0) {
            requestAnimationFrame(growMycelium);
        } else {
            dishOverlay.textContent = "Fruiting Complete.";
            dishOverlay.style.color = "var(--bio)";
            dishOverlay.style.opacity = 1;
            incubating = false;
            atp = Math.min(100, atp + 20); // Reward
            updateVitals();
        }
    }

});
