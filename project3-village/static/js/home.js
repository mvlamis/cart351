document.addEventListener('DOMContentLoaded', () => {
    const drawer = document.getElementById("edit-drawer");
    const gear = document.getElementById("edit-gear");
    const closeBtn = document.getElementById("close-drawer");
    const shopContent = document.getElementById("shop-content");
    const coinDisplay = document.getElementById("user-coins");

    let catalog = {};
    let userInventory = [];
    let userEquipped = {};
    let userCoins = 0;

    // initial Load
    Promise.all([
        fetch('/api/furniture/catalog').then(r => r.json()),
        fetch('/api/user/furniture').then(r => r.json())
    ]).then(([catalogData, userData]) => {
        catalog = catalogData;
        userInventory = userData.inventory;
        userEquipped = userData.equipped;
        userCoins = userData.coins;
        
        updateCoinDisplay();
        renderRoom();
        renderShop();
    });

    if (gear) {
        gear.addEventListener("click", () => {
            drawer.classList.remove("hidden");
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener("click", () => {
            drawer.classList.add("hidden");
        });
    }

    function updateCoinDisplay() {
        if (coinDisplay) {
            coinDisplay.textContent = userCoins;
        }
    }

    function renderRoom() {
        // hide all first
        document.querySelectorAll('.furniture').forEach(el => el.style.display = 'none');

        // show equipped
        for (const [category, itemId] of Object.entries(userEquipped)) {
            const imgEl = document.getElementById(`furniture-${category}`);
            if (imgEl && itemId) {
                // find src from catalog
                let src = "";
                if (catalog[category]) {
                    const item = catalog[category].find(i => i.id === itemId);
                    if (item) src = item.src;
                }
                
                if (src) {
                    imgEl.src = `/static/images/${src}`;
                    imgEl.style.display = 'block';
                }
            }
        }
    }

    function createShopItemElement(item, category) {
        const container = document.createElement('div');
        container.className = 'shop-item';

        const img = document.createElement('img');
        img.src = `/static/images/${item.src}`;
        img.className = 'preview-thumb';
        container.appendChild(img);

        const btn = document.createElement('button');
        btn.className = 'shop-btn';
        
        const isOwned = userInventory.includes(item.id);
        const isEquipped = userEquipped[category] === item.id;

        if (isEquipped) {
            if (category === 'exterior') {
                btn.textContent = "Current";
                btn.disabled = true;
                btn.classList.add('btn-equipped');
            } else {
                btn.textContent = "Remove";
                btn.classList.add('btn-remove');
                btn.onclick = () => unequipItem(category);
            }
        } else if (isOwned) {
            btn.textContent = "Equip";
            btn.classList.add('btn-equip');
            btn.onclick = () => equipItem(category, item.id);
        } else {
            btn.innerHTML = `${item.price} <img src="/static/images/coin.png" class="coin-icon-small">`;
            btn.classList.add('btn-buy');
            if (userCoins < item.price) btn.disabled = true;
            btn.onclick = () => buyItem(item.id, item.price);
        }

        container.appendChild(btn);
        return container;
    }

    function renderShop() {
        if (!shopContent) return;
        shopContent.innerHTML = '';

        // Furniture Section Header
        const furnHeader = document.createElement('h4');
        furnHeader.textContent = "Furniture";
        shopContent.appendChild(furnHeader);

        // create rows for each category EXCEPT exterior
        for (const [category, items] of Object.entries(catalog)) {
            if (category === 'exterior') continue;

            const row = document.createElement('div');
            row.className = 'furniture-row';
            
            const label = document.createElement('span');
            label.textContent = category.charAt(0).toUpperCase() + category.slice(1) + ":";
            row.appendChild(label);

            items.forEach(item => {
                row.appendChild(createShopItemElement(item, category));
            });

            shopContent.appendChild(row);
        }

        // Exterior Section Header
        const extHeader = document.createElement('h4');
        extHeader.textContent = "Exterior";
        shopContent.appendChild(extHeader);

        if (catalog['exterior']) {
            const items = catalog['exterior'];
            const category = 'exterior';
            
            const row = document.createElement('div');
            row.className = 'furniture-row';
            
            items.forEach(item => {
                row.appendChild(createShopItemElement(item, category));
            });
            shopContent.appendChild(row);
        }
    }

    function buyItem(itemId, price) {
        fetch('/api/furniture/buy', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item_id: itemId })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                userCoins = data.new_balance;
                userInventory.push(itemId);
                updateCoinDisplay();
                renderShop();
            } else {
                alert(data.error);
            }
        });
    }

    function equipItem(category, itemId) {
        fetch('/api/furniture/equip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: category, item_id: itemId })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                userEquipped[category] = itemId;
                renderRoom();
                renderShop();
            }
        });
    }

    function unequipItem(category) {
        fetch('/api/furniture/equip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ category: category, item_id: null })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                delete userEquipped[category];
                renderRoom();
                renderShop();
            }
        });
    }
});
