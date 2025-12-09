document.addEventListener('DOMContentLoaded', () => {
    const icons = [
        'coin.png', 'coin_stack.png', 'flower.png', 'gear.png',
        'key.png', 'life.png', 'slime.png', 'strawberry.png'
    ];
    console.log("Icons loaded:", icons);

    const deck = icons.concat(icons)
        .map(src => ({ src }))
        .sort(() => Math.random() - 0.5);

    const grid = document.getElementById('cards-grid');
    let firstCard = null, secondCard = null;
    let lock = false;
    let matchedPairs = 0;

    function createCard(cardData) {
        const card = document.createElement('div');
        card.className = 'card';
        card.dataset.src = cardData.src;

        const inner = document.createElement('div');
        inner.className = 'card-inner';

        const back = document.createElement('div');
        back.className = 'card-back';

        const front = document.createElement('div');
        front.className = 'card-front';
        front.style.backgroundImage = `url('/static/images/icons/${cardData.src}')`;

        inner.append(back, front);
        card.append(inner);
        card.addEventListener('click', flipCard);
        return card;
    }

    deck.forEach(cardData => grid.append(createCard(cardData)));

    function flipCard() {
        if (lock || this.classList.contains('flipped')) return;
        this.classList.add('flipped');

        if (!firstCard) {
            firstCard = this;
        } else {
            secondCard = this;
            lock = true;

            // check match
            if (firstCard.dataset.src === secondCard.dataset.src) {
                matchedPairs++;
                resetTurn();
                if (matchedPairs === icons.length) gameWon();
            } else {
                setTimeout(() => {
                    firstCard.classList.remove('flipped');
                    secondCard.classList.remove('flipped');
                    resetTurn();
                }, 800);
            }
        }
    }

    function resetTurn() {
        [firstCard, secondCard] = [null, null];
        lock = false;
    }

    function gameWon() {
        const overlay = document.getElementById('win-overlay');
        overlay.classList.remove('hidden');

        fetch('/api/user/coins/add', {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount: 10 })
        }).catch(console.error);

        document.getElementById('win-restart').onclick = () => location.reload();
        document.getElementById('win-exit').onclick = () => window.location.href = '/games';
    }
});
