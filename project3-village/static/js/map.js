document.addEventListener('DOMContentLoaded', () => {
    const grid = document.querySelector('.map-grid');
    grid.style.position = 'relative';

    // svg layer for drawing connection lines
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    Object.assign(svg.style, {
        position: 'absolute',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        pointerEvents: 'none', // let clicks pass through to houses
        zIndex: '0'
    });
    grid.appendChild(svg);

    // Load users from database
    fetch('/api/users')
        .then(response => response.json())
        .then(users => {
            // Map database fields to the structure expected by the renderer
            const houseData = users.map(user => ({
                id: user._id,
                name: user.username,
                friends: user.friends || [],
                house: user.house || '1'
            }));

            houseData.forEach(house => {
                const houseDiv = document.createElement('div');
                houseDiv.className = 'house-placeholder';
                houseDiv.dataset.id = house.id;
                houseDiv.style.zIndex = '1';
                houseDiv.style.cursor = 'pointer';

                houseDiv.addEventListener('click', () => {
                    window.location.href = `/visit/${house.id}`;
                });

                const img = document.createElement('img');
                img.src = `/static/images/houses/house${house.house}.png`;
                img.className = 'house-img';
                img.alt = 'House';
                houseDiv.appendChild(img);

                const label = document.createElement('span');
                label.className = 'house-label';
                label.textContent = house.name;

                houseDiv.appendChild(label);
                grid.appendChild(houseDiv);
            });

            // after layout, draw connections
            setTimeout(() => {
                const drawnConnections = new Set();

                houseData.forEach(house => {
                    const houseEl = grid.querySelector(`[data-id='${house.id}']`);
                    
                    house.friends.forEach(friendId => {
                        // create a unique key (smaller-larger) to avoid drawing the same line twice
                        const key = [house.id, friendId].sort().join('-');
                        if (drawnConnections.has(key)) return;
                        drawnConnections.add(key);

                        const friendEl = grid.querySelector(`[data-id='${friendId}']`);
                        if (houseEl && friendEl) {
                            drawLine(svg, houseEl, friendEl, grid);
                        }
                    });
                });
            }, 100);
        })
        .catch(err => console.error('Error loading map data:', err));
});

function drawLine(svg, el1, el2, container) {
    const rect1 = el1.getBoundingClientRect();
    const rect2 = el2.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();

    // calculate centers relative to the container
    const x1 = rect1.left + rect1.width / 2 - containerRect.left;
    const y1 = rect1.top + rect1.height / 2 - containerRect.top;
    const x2 = rect2.left + rect2.width / 2 - containerRect.left;
    const y2 = rect2.top + rect2.height / 2 - containerRect.top;

    const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('stroke', '#555');
    line.setAttribute('stroke-width', '4');
    
    svg.appendChild(line);
}
