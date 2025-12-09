// slime_extended.js
document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('slime-grid');
    const scoreEl = document.getElementById('score');
    const livesEl = document.getElementById('lives-display');
    const coinsTotalEl = document.getElementById('coins-total');
    const restartBtn = document.getElementById('restart-btn');
    const leaveBtn = document.getElementById('leave-btn');
    const restartOverBtn = document.getElementById('restart-over-btn');

    let score = 0;
    let lives = 3;
    let coinsEarned = 0;
    let activeIndex = null;
    let popInterval = null;
    const POP_RATE = 800;      // interval between new pops (ms)
    const POP_DURATION = 700;  // how long a slime stays up (ms)
    const heartsEl = document.getElementById("hearts");
    const scoreDisplay = document.getElementById("game-score");

    function renderHearts() {
        heartsEl.innerHTML = "";
        for (let i = 0; i < lives; i++) {
            const heart = document.createElement("img");
            heart.src = "/static/images/life.png"; // put a 30x30 png in this folder!
            heart.alt = "life";
            heartsEl.appendChild(heart);
        }
    }

    // create holes
    for (let i = 0; i < 9; i++) {
        const hole = document.createElement('div');
        hole.className = 'slime-hole';

        const slime = document.createElement('div');
        slime.className = 'slime';
        // make element use your slime PNG - ensure path exists
        slime.style.backgroundImage = "url('/static/images/slime.png')";

        // click handler
        slime.addEventListener('click', (e) => {
            if (slime.style.display === 'flex') {
                // whacked
                score++;
                scoreDisplay.textContent = "Score: " + score;
                coinsEarned++;
                scoreEl.textContent = 'Score: ' + score;
                slime.style.display = 'none';
                if (slime._missTimer) {
                    clearTimeout(slime._missTimer);
                    slime._missTimer = null;
                }
            }
        });

        hole.appendChild(slime);
        grid.appendChild(hole);
    }

    const slimes = Array.from(document.querySelectorAll('.slime'));

    function showRandomSlime() {
        // hide previous if any (if it was still visible, count as miss)
        if (activeIndex !== null) {
            const prev = slimes[activeIndex];
            if (prev && prev.style.display === 'flex') {
                // missed last one
                prev.style.display = 'none';
                if (prev._missTimer) {
                    clearTimeout(prev._missTimer);
                    prev._missTimer = null;
                }
                loseLife();
            }
        }

        // pick new random index
        const idx = Math.floor(Math.random() * slimes.length);
        activeIndex = idx;
        const slime = slimes[idx];
        slime.style.display = 'flex';

        // set a timeout for this slime to auto-hide if not clicked (miss)
        slime._missTimer = setTimeout(() => {
            if (slime.style.display === 'flex') {
                slime.style.display = 'none';
                slime._missTimer = null;
                loseLife();
            }
        }, POP_DURATION);
    }

    function loseLife() {
        lives--;
        renderHearts();
        livesEl.textContent = 'Lives: ' + lives;
        if (lives <= 0) {
            endGame();
        }
    }

    function startGame() {
        // full reset
        score = 0;
        lives = 3;
        coinsEarned = 0;
        activeIndex = null;

        // update displays AFTER resetting values
        scoreEl.textContent = 'Score: ' + score;
        scoreDisplay.textContent = "Score: " + score;
        livesEl.textContent = 'Lives: ' + lives;
        renderHearts();

        // hide all slimes + wipe timers
        slimes.forEach(s => {
            s.style.display = 'none';
            if (s._missTimer) {
                clearTimeout(s._missTimer);
                s._missTimer = null;
            }
        });

        // hide game over screen if visible
        document.getElementById("game-over-screen").classList.add("hidden");

        // restart interval
        clearInterval(popInterval);
        popInterval = setInterval(showRandomSlime, POP_RATE);

        // show first slime immediately
        showRandomSlime();
    }

    function endGame() {
        clearInterval(popInterval);

        // hide active slime
        if (activeIndex !== null) {
            const s = slimes[activeIndex];
            if (s) s.style.display = 'none';
        }

        // send coins to server
        if (coinsEarned > 0) {
            fetch('/api/user/coins/add', {
                method: 'POST',
                credentials: 'same-origin',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ amount: coinsEarned })
            })
                .then(resp => resp.json())
                .then(data => {
                    if (data.coins !== undefined) {
                        coinsTotalEl.textContent = 'Coins: ' + data.coins;
                    }
                })
                .catch(err => console.error('Failed to save coins', err));
        }

        // show game over screen
        document.getElementById("final-coins").textContent = score;
        document.getElementById("game-over-screen").classList.remove("hidden");
    }

    // attach start handler to main restart button if present
    if (restartBtn) restartBtn.addEventListener('click', startGame);
    // attach start handler to game-over restart button if present
    if (restartOverBtn) restartOverBtn.addEventListener('click', startGame);

    // fetch user coins on load (moved inside DOMContentLoaded so coinsTotalEl is defined)
    fetch('/api/user/coins', { credentials: 'same-origin' })
        .then(r => r.json())
        .then(data => {
            if (data.coins !== undefined) {
                coinsTotalEl.textContent = 'Coins: ' + data.coins;
            } else {
                coinsTotalEl.textContent = 'Coins: 0';
            }
        })
        .catch(() => coinsTotalEl.textContent = 'Coins: —');
});


// fetch user coins on load
fetch('/api/user/coins', { credentials: 'same-origin' })
    .then(r => r.json())
    .then(data => {
        if (data.coins !== undefined) {
            coinsTotalEl.textContent = 'Coins: ' + data.coins;
        } else {
            coinsTotalEl.textContent = 'Coins: 0';
        }
    })
    .catch(() => coinsTotalEl.textContent = 'Coins: —');

