// EcoSwap Main Application Frontend Controller

let currentUser = null;
let allUsers = [];
let marketplaceItems = [];
let myWardrobeItems = [];
let activeSwaps = [];
let ecoHubsList = [];
let activeTradeFilter = 'all';
let currentTargetItem = null;
let selectedOfferItemId = null;
let activeChatSwapId = null;
let searchDebounceTimer = null;

const CATEGORIES = [
    'All',
    'Jackets & Coats',
    'Sweaters & Knits',
    'Tops & Shirts',
    'Pants & Jeans',
    'Dresses & Jumpsuits',
    'Shoes',
    'Accessories'
];

let activeCategory = 'All';

// Curated preset photography for quick testing in "Add Clothes"
const PRESET_PHOTOS = [
    'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1542272604-780c96856592?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1548883354-7622d03aca27?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=800&auto=format&fit=crop&q=80'
];
let presetPhotoIdx = 0;

document.addEventListener('DOMContentLoaded', async () => {
    renderCategoryPills();
    await loadCurrentUser();
    await loadAllUsers();
    await loadMarketplaceItems();
    await loadMyWardrobe();
    await loadSwaps();
    await loadEcoHubs();
    await loadEcoImpact();
    lucide.createIcons();
});

// ==========================================
// USER & PERSONA SWITCHING
// ==========================================

async function loadCurrentUser() {
    try {
        const res = await fetch('/api/me');
        if (!res.ok) throw new Error('Failed to fetch user');
        currentUser = await res.json();
        
        document.getElementById('user-name').innerText = currentUser.name;
        document.getElementById('user-avatar').src = currentUser.avatar_url;
        document.getElementById('user-eco-credits').innerText = currentUser.eco_credits;
    } catch (err) {
        console.error('Error loading current user:', err);
    }
}

async function loadAllUsers() {
    try {
        const res = await fetch('/api/users');
        allUsers = await res.json();
        renderUserDropdown();
    } catch (err) {
        console.error('Error loading users list:', err);
    }
}

function renderUserDropdown() {
    const list = document.getElementById('user-switcher-list');
    if (!list) return;

    list.innerHTML = allUsers.map(u => `
        <button onclick="switchUserPersona(${u.id})" class="w-full text-left px-4 py-2 hover:bg-slate-50 flex items-center gap-3 transition-colors ${u.id === currentUser?.id ? 'bg-emerald-50/70 font-semibold' : ''}">
            <img src="${u.avatar_url}" class="w-7 h-7 rounded-lg object-cover">
            <div class="flex-grow min-w-0">
                <div class="text-xs text-slate-800 truncate">${u.name}</div>
                <div class="text-[10px] text-slate-400">${u.address.split(',')[0]} • ${u.eco_credits} Credits</div>
            </div>
            ${u.id === currentUser?.id ? '<i data-lucide="check" class="w-3.5 h-3.5 text-emerald-600"></i>' : ''}
        </button>
    `).join('');
    lucide.createIcons();
}

function toggleUserDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    dropdown.classList.toggle('hidden');
}

document.addEventListener('click', (e) => {
    const menuBtn = document.getElementById('user-menu-btn');
    const dropdown = document.getElementById('user-dropdown');
    if (menuBtn && dropdown && !menuBtn.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.add('hidden');
    }
});

async function switchUserPersona(newUserId) {
    try {
        const res = await fetch('/api/switch-user', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: newUserId })
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById('user-dropdown').classList.add('hidden');
            showToast(`Switched active profile to ${data.user.name}`, 'info');
            await loadCurrentUser();
            renderUserDropdown();
            await loadMarketplaceItems();
            await loadMyWardrobe();
            await loadSwaps();
            await loadEcoImpact();
        }
    } catch (err) {
        showToast('Failed to switch persona', 'error');
    }
}

// ==========================================
// TABS NAVIGATION
// ==========================================

function switchTab(tabName) {
    const tabs = ['marketplace', 'map', 'tradehub', 'wardrobe', 'impact'];
    tabs.forEach(t => {
        const el = document.getElementById(`tab-${t}`);
        const navBtn = document.getElementById(`nav-btn-${t}`);
        if (el) el.classList.toggle('hidden', t !== tabName);
        if (navBtn) navBtn.classList.toggle('active', t !== tabName ? false : true);
    });

    if (tabName === 'map') {
        initMap(currentUser?.latitude, currentUser?.longitude);
        updateMapMarkers(marketplaceItems, ecoHubsList);
    } else if (tabName === 'tradehub') {
        loadSwaps();
    } else if (tabName === 'wardrobe') {
        loadMyWardrobe();
    } else if (tabName === 'impact') {
        loadEcoImpact();
    }
    lucide.createIcons();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==========================================
// MARKETPLACE & FILTERING
// ==========================================

function renderCategoryPills() {
    const container = document.getElementById('category-pills');
    if (!container) return;

    container.innerHTML = CATEGORIES.map(cat => `
        <button onclick="selectCategory('${cat}')" class="category-pill ${cat === activeCategory ? 'active' : ''} px-4 py-2 rounded-xl text-xs font-semibold">
            ${cat}
        </button>
    `).join('');
}

function selectCategory(cat) {
    activeCategory = cat;
    renderCategoryPills();
    applyFilters();
}

function debounceSearch() {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
        applyFilters();
    }, 300);
}

function updateDistanceLabel(val) {
    document.getElementById('distance-val').innerText = `${val} mi`;
}

async function loadMarketplaceItems() {
    const gender = document.getElementById('filter-gender')?.value || 'All';
    const size = document.getElementById('filter-size')?.value || 'All';
    const condition = document.getElementById('filter-condition')?.value || 'All';
    const distance = document.getElementById('filter-distance')?.value || '25';
    const sort = document.getElementById('filter-sort')?.value || 'newest';
    const search = document.getElementById('filter-search')?.value || '';

    const params = new URLSearchParams({
        category: activeCategory,
        gender: gender,
        size: size,
        condition: condition,
        max_distance: distance,
        sort: sort,
        search: search
    });

    try {
        const res = await fetch(`/api/items?${params.toString()}`);
        marketplaceItems = await res.json();
        renderMarketplaceGrid(marketplaceItems);
        if (mapInstance) {
            updateMapMarkers(marketplaceItems, ecoHubsList);
        }
    } catch (err) {
        console.error('Failed to load marketplace items:', err);
    }
}

function applyFilters() {
    loadMarketplaceItems();
}

function renderMarketplaceGrid(items) {
    const grid = document.getElementById('items-grid');
    const countDisplay = document.getElementById('items-count-display');
    if (!grid) return;

    countDisplay.innerText = items.length;

    if (items.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center bg-white rounded-3xl border border-slate-200">
                <div class="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-3">
                    <i data-lucide="search-x" class="w-8 h-8"></i>
                </div>
                <h3 class="font-display font-bold text-lg text-slate-800">No items match your filters</h3>
                <p class="text-xs text-slate-500 max-w-sm mx-auto mt-1">Try expanding your distance radius or changing category/size preferences.</p>
                <button onclick="resetFilters()" class="mt-4 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl transition-all">
                    Reset All Filters
                </button>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    grid.innerHTML = items.map(item => `
        <div class="group bg-white rounded-3xl overflow-hidden border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col">
            <!-- Card Image Container -->
            <div class="relative h-64 overflow-hidden bg-slate-100 cursor-pointer" onclick="openItemDetailModal(${item.id})">
                <img src="${item.image_url}" alt="${item.title}" class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
                
                <!-- Barter Score Pill -->
                <div class="absolute top-3 left-3 bg-slate-900/80 backdrop-blur-md text-emerald-400 font-display font-extrabold text-xs px-2.5 py-1 rounded-xl flex items-center gap-1 shadow-md">
                    <i data-lucide="sparkles" class="w-3 h-3 text-emerald-400"></i>
                    <span>${item.barter_score}</span>
                    <span class="text-[10px] text-slate-400 font-medium">Barter</span>
                </div>

                <!-- Distance Pill -->
                <div class="absolute top-3 right-3 bg-white/90 backdrop-blur-md text-slate-700 font-bold text-[11px] px-2.5 py-1 rounded-xl shadow-sm flex items-center gap-1">
                    <i data-lucide="map-pin" class="w-3 h-3 text-emerald-600"></i>
                    <span>${item.distance_miles} mi</span>
                </div>

                <!-- Condition Badge -->
                <div class="absolute bottom-3 left-3 bg-emerald-600/90 text-white font-semibold text-[10px] px-2.5 py-0.5 rounded-lg backdrop-blur-sm">
                    ${item.condition}
                </div>
            </div>

            <!-- Card Content Body -->
            <div class="p-5 flex-grow flex flex-col justify-between">
                <div>
                    <!-- Category & Size row -->
                    <div class="flex items-center justify-between text-xs text-slate-400 font-medium mb-1">
                        <span>${item.category}</span>
                        <span class="bg-slate-100 text-slate-700 font-bold px-2 py-0.5 rounded-md text-[11px]">Size ${item.size}</span>
                    </div>

                    <!-- Title -->
                    <h3 onclick="openItemDetailModal(${item.id})" class="font-display font-bold text-base text-slate-900 hover:text-emerald-700 cursor-pointer line-clamp-1">
                        ${item.title}
                    </h3>

                    <!-- Material / Brand -->
                    <p class="text-xs text-slate-500 mt-1 line-clamp-1">
                        ${item.brand ? `<strong class="text-slate-700 font-semibold">${item.brand}</strong> • ` : ''}${item.material || 'Sustainable weave'}
                    </p>

                    <!-- Swap Wishlist Snippet -->
                    <div class="mt-3 bg-slate-50 border border-slate-100 rounded-xl p-2.5 text-[11px] text-slate-600 flex items-start gap-1.5">
                        <i data-lucide="repeat" class="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5"></i>
                        <span class="line-clamp-2"><strong>ISO:</strong> ${item.swap_preference || 'Open to fair trades'}</span>
                    </div>
                </div>

                <!-- Card Footer: Swapper & Action -->
                <div class="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2 min-w-0">
                        <img src="${item.owner_avatar}" alt="${item.owner_name}" class="w-7 h-7 rounded-lg object-cover ring-1 ring-slate-200">
                        <div class="min-w-0 text-left">
                            <span class="block text-xs font-bold text-slate-800 truncate">${item.owner_name}</span>
                            <span class="text-[10px] text-slate-400">★ ${item.owner_rating} (${item.owner_swaps} swaps)</span>
                        </div>
                    </div>

                    <button onclick="openProposeSwapModal(${item.id})" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-3.5 py-2 rounded-xl shadow-sm hover:shadow transition-all flex items-center gap-1.5 flex-shrink-0">
                        <span>Swap</span>
                        <i data-lucide="arrow-right-left" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    lucide.createIcons();
}

function resetFilters() {
    activeCategory = 'All';
    document.getElementById('filter-gender').value = 'All';
    document.getElementById('filter-size').value = 'All';
    document.getElementById('filter-condition').value = 'All';
    document.getElementById('filter-distance').value = '25';
    updateDistanceLabel(25);
    document.getElementById('filter-sort').value = 'newest';
    document.getElementById('filter-search').value = '';
    renderCategoryPills();
    applyFilters();
}

// ==========================================
// VALUE-BASED SWAP PROPOSAL ENGINE
// ==========================================

async function openProposeSwapModal(targetItemId) {
    try {
        const res = await fetch(`/api/fair-match/${targetItemId}`);
        if (!res.ok) {
            const err = await res.json();
            showToast(err.error || 'Failed to match items', 'error');
            return;
        }

        const data = await res.json();
        currentTargetItem = data.target_item;
        const matches = data.matches;

        // Render Target Garment Card
        const targetContainer = document.getElementById('propose-target-card');
        targetContainer.innerHTML = `
            <img src="${currentTargetItem.image_url}" class="w-20 h-24 object-cover rounded-xl flex-shrink-0">
            <div class="min-w-0 flex-grow">
                <span class="text-[10px] bg-slate-200 font-bold px-2 py-0.5 rounded text-slate-700 uppercase">${currentTargetItem.category}</span>
                <h4 class="font-display font-bold text-sm text-slate-900 mt-1 truncate">${currentTargetItem.title}</h4>
                <p class="text-xs text-slate-500">${currentTargetItem.brand || ''} • Size ${currentTargetItem.size}</p>
                <div class="mt-2 flex items-center gap-2">
                    <span class="text-xs font-extrabold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded">Score: ${currentTargetItem.barter_score}</span>
                    <span class="text-[11px] text-slate-400">Owner: ${currentTargetItem.owner_name || 'Community Swapper'}</span>
                </div>
            </div>
        `;

        // Render Wardrobe Selector List
        const listContainer = document.getElementById('propose-wardrobe-list');
        if (matches.length === 0) {
            listContainer.innerHTML = `
                <div class="p-6 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                    <p class="text-xs text-slate-500">You don't have any items available in your wardrobe to barter!</p>
                    <button onclick="closeModal('modal-propose-swap'); openAddItemModal();" class="mt-2 text-xs font-bold text-emerald-600 hover:underline">
                        + List Clothes to Your Wardrobe
                    </button>
                </div>
            `;
            document.getElementById('equivalence-box').classList.add('hidden');
        } else {
            document.getElementById('equivalence-box').classList.remove('hidden');
            // Auto-select best match (first one)
            selectedOfferItemId = matches[0].my_item.id;

            listContainer.innerHTML = matches.map((m, idx) => `
                <div onclick="selectOfferItem(${m.my_item.id}, ${JSON.stringify(m.fairness).replace(/"/g, '&quot;')})" 
                     id="offer-item-${m.my_item.id}"
                     class="offer-item-card p-3 rounded-2xl border ${idx === 0 ? 'border-emerald-500 bg-emerald-50/50' : 'border-slate-200 hover:border-slate-300'} cursor-pointer transition-all flex items-center gap-3">
                    <img src="${m.my_item.image_url}" class="w-12 h-14 object-cover rounded-xl flex-shrink-0">
                    <div class="flex-grow min-w-0">
                        <div class="text-xs font-bold text-slate-900 truncate">${m.my_item.title}</div>
                        <div class="text-[11px] text-slate-500">Size ${m.my_item.size} • Score: <strong>${m.my_item.barter_score}</strong></div>
                    </div>
                    <div class="text-right flex-shrink-0">
                        <span class="inline-block text-xs font-extrabold px-2 py-1 rounded-lg ${m.fairness.fairness_pct >= 85 ? 'bg-emerald-600 text-white' : 'bg-amber-100 text-amber-800'}">
                            ${m.fairness.fairness_pct}% Match
                        </span>
                        <span class="block text-[10px] text-slate-400 mt-0.5">${m.fairness.verdict}</span>
                    </div>
                </div>
            `).join('');

            updateEquivalenceDisplay(matches[0].fairness);
        }

        openModal('modal-propose-swap');
        lucide.createIcons();
    } catch (err) {
        console.error(err);
        showToast('Error preparing trade proposal', 'error');
    }
}

function selectOfferItem(itemId, fairness) {
    selectedOfferItemId = itemId;
    document.querySelectorAll('.offer-item-card').forEach(card => {
        card.classList.remove('border-emerald-500', 'bg-emerald-50/50');
        card.classList.add('border-slate-200');
    });
    const selected = document.getElementById(`offer-item-${itemId}`);
    if (selected) {
        selected.classList.add('border-emerald-500', 'bg-emerald-50/50');
        selected.classList.remove('border-slate-200');
    }
    updateEquivalenceDisplay(fairness);
}

function updateEquivalenceDisplay(fairness) {
    const badge = document.getElementById('fairness-pct-badge');
    const bar = document.getElementById('fairness-bar');
    const advice = document.getElementById('fairness-advice');
    const creditInput = document.getElementById('propose-credits');

    badge.innerText = `${fairness.fairness_pct}% Fair Match (${fairness.verdict})`;
    bar.style.width = `${fairness.fairness_pct}%`;
    advice.innerText = fairness.advice;

    if (fairness.suggested_credit > 0 && creditInput) {
        creditInput.value = fairness.suggested_credit;
    }
}

async function submitSwapProposal() {
    if (!currentTargetItem || !selectedOfferItemId) {
        showToast('Please select an item to offer in barter', 'error');
        return;
    }

    const credits = document.getElementById('propose-credits').value;
    const location = document.getElementById('propose-location').value;
    const note = document.getElementById('propose-note').value;

    try {
        const res = await fetch('/api/swaps/propose', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                requested_item_id: currentTargetItem.id,
                offered_item_id: selectedOfferItemId,
                additional_credits: credits,
                meet_location: location,
                note: note
            })
        });

        const data = await res.json();
        if (data.success) {
            closeModal('modal-propose-swap');
            showToast('Swap proposal sent successfully!', 'success');
            await loadSwaps();
            switchTab('tradehub');
        } else {
            showToast(data.error || 'Failed to send proposal', 'error');
        }
    } catch (err) {
        showToast('Network error while proposing swap', 'error');
    }
}

// ==========================================
// TRADE HUB & ACTIONS
// ==========================================

async function loadSwaps() {
    try {
        const res = await fetch('/api/swaps');
        activeSwaps = await res.json();
        
        // Update badge count
        const pendingCount = activeSwaps.filter(s => !s.is_requester && s.status === 'pending').length;
        const badge = document.getElementById('nav-trade-badge');
        if (badge) {
            if (pendingCount > 0) {
                badge.innerText = pendingCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
        
        renderTradesList();
    } catch (err) {
        console.error('Failed to load swaps:', err);
    }
}

function filterTrades(filterType) {
    activeTradeFilter = filterType;
    ['all', 'incoming', 'outgoing'].forEach(t => {
        const btn = document.getElementById(`trade-filter-${t}`);
        if (btn) btn.classList.toggle('active', t === filterType);
    });
    renderTradesList();
}

function renderTradesList() {
    const container = document.getElementById('trades-list');
    if (!container) return;

    let filtered = activeSwaps;
    if (activeTradeFilter === 'incoming') {
        filtered = activeSwaps.filter(s => !s.is_requester);
    } else if (activeTradeFilter === 'outgoing') {
        filtered = activeSwaps.filter(s => s.is_requester);
    }

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="py-16 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <i data-lucide="arrow-left-right" class="w-8 h-8 text-slate-300 mx-auto mb-2"></i>
                <p class="text-sm font-bold text-slate-700">No ${activeTradeFilter !== 'all' ? activeTradeFilter : ''} trade proposals yet</p>
                <p class="text-xs text-slate-400 mt-1">Browse the marketplace and propose your first clothing swap!</p>
                <button onclick="switchTab('marketplace')" class="mt-4 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-sm">
                    Explore Marketplace
                </button>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    container.innerHTML = filtered.map(swap => {
        const isIncoming = !swap.is_requester;
        const otherParty = isIncoming ? swap.requester_name : swap.receiver_name;
        const otherAvatar = isIncoming ? swap.requester_avatar : swap.receiver_avatar;

        const statusBadges = {
            'pending': 'bg-amber-100 text-amber-800 border-amber-200',
            'accepted': 'bg-emerald-100 text-emerald-800 border-emerald-200',
            'completed': 'bg-blue-100 text-blue-800 border-blue-200',
            'declined': 'bg-red-100 text-red-800 border-red-200',
            'cancelled': 'bg-slate-100 text-slate-600 border-slate-200'
        };

        return `
            <div class="bg-white rounded-2xl p-5 border border-slate-200 hover:shadow-md transition-all space-y-4">
                <!-- Top Status Header -->
                <div class="flex flex-wrap items-center justify-between gap-2 pb-3 border-b border-slate-100">
                    <div class="flex items-center gap-2">
                        <img src="${otherAvatar}" class="w-8 h-8 rounded-lg object-cover">
                        <div>
                            <span class="text-xs font-bold text-slate-900">${isIncoming ? `Proposal from ${otherParty}` : `Proposed to ${otherParty}`}</span>
                            <span class="block text-[10px] text-slate-400">${swap.created_at}</span>
                        </div>
                    </div>

                    <div class="flex items-center gap-2">
                        <span class="text-xs font-bold border px-2.5 py-1 rounded-xl uppercase tracking-wider text-[10px] ${statusBadges[swap.status] || 'bg-slate-100'}">
                            ${swap.status}
                        </span>
                        <span class="text-xs font-extrabold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-lg">
                            ${swap.fairness_pct}% Match
                        </span>
                    </div>
                </div>

                <!-- Visual Barter Exchange Comparison -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl items-center">
                    <!-- Offered Item -->
                    <div class="flex items-center gap-3">
                        <img src="${swap.offered_image}" class="w-14 h-16 object-cover rounded-xl shadow-sm">
                        <div class="min-w-0">
                            <span class="text-[10px] font-bold text-emerald-700 uppercase">${isIncoming ? "THEY OFFER" : "YOU OFFER"}</span>
                            <h4 class="font-bold text-xs text-slate-900 truncate">${swap.offered_title}</h4>
                            <p class="text-[11px] text-slate-500">Size ${swap.offered_size} • Score: <strong>${swap.offered_score}</strong></p>
                        </div>
                    </div>

                    <!-- Requested Item -->
                    <div class="flex items-center gap-3">
                        <img src="${swap.requested_image}" class="w-14 h-16 object-cover rounded-xl shadow-sm">
                        <div class="min-w-0">
                            <span class="text-[10px] font-bold text-blue-700 uppercase">${isIncoming ? "FOR YOUR" : "FOR THEIR"}</span>
                            <h4 class="font-bold text-xs text-slate-900 truncate">${swap.requested_title}</h4>
                            <p class="text-[11px] text-slate-500">Size ${swap.requested_size} • Score: <strong>${swap.requested_score}</strong></p>
                        </div>
                    </div>
                </div>

                <!-- Terms & Location -->
                <div class="flex flex-wrap items-center justify-between text-xs text-slate-600 gap-2">
                    <div class="flex items-center gap-4">
                        <span class="flex items-center gap-1">
                            <i data-lucide="map-pin" class="w-3.5 h-3.5 text-emerald-600"></i>
                            <strong>Meetup:</strong> ${swap.meet_location}
                        </span>
                        ${swap.additional_credits > 0 ? `
                            <span class="flex items-center gap-1 text-emerald-700 font-bold bg-emerald-50 px-2 py-0.5 rounded">
                                +${swap.additional_credits} Eco-Credits Sweetener
                            </span>
                        ` : ''}
                    </div>

                    <!-- Action Buttons -->
                    <div class="flex items-center gap-2">
                        <!-- Chat Button -->
                        <button onclick="openSwapChatModal(${swap.id}, '${otherParty}')" class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold flex items-center gap-1">
                            <i data-lucide="message-circle" class="w-3.5 h-3.5"></i> Chat
                        </button>

                        ${isIncoming && swap.status === 'pending' ? `
                            <button onclick="handleSwapAction(${swap.id}, 'accept')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold">
                                Accept Barter
                            </button>
                            <button onclick="handleSwapAction(${swap.id}, 'decline')" class="px-3 py-1.5 bg-slate-200 hover:bg-red-100 hover:text-red-700 text-slate-600 rounded-xl text-xs font-bold">
                                Decline
                            </button>
                        ` : ''}

                        ${swap.status === 'accepted' ? `
                            <button onclick="handleSwapAction(${swap.id}, 'complete')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold flex items-center gap-1 shadow-sm">
                                <i data-lucide="qr-code" class="w-3.5 h-3.5"></i> Handshake Complete (+25 Credits)
                            </button>
                        ` : ''}

                        ${swap.status === 'pending' && !isIncoming ? `
                            <button onclick="handleSwapAction(${swap.id}, 'cancel')" class="px-3 py-1.5 text-slate-400 hover:text-red-600 text-xs font-semibold">
                                Cancel
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    lucide.createIcons();
}

async function handleSwapAction(swapId, action) {
    try {
        const res = await fetch(`/api/swaps/${swapId}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`Swap updated: ${action.toUpperCase()}`, 'success');
            await loadCurrentUser();
            await loadSwaps();
            await loadMarketplaceItems();
            await loadMyWardrobe();
            await loadEcoImpact();
        } else {
            showToast(data.error || 'Action failed', 'error');
        }
    } catch (err) {
        showToast('Error performing action', 'error');
    }
}

// ==========================================
// SWAP CHAT & MESSAGING
// ==========================================

async function openSwapChatModal(swapId, otherPartyName) {
    activeChatSwapId = swapId;
    document.getElementById('chat-modal-title').innerText = `Chat with ${otherPartyName}`;
    document.getElementById('chat-modal-subtitle').innerText = `Coordinating clothing swap #${swapId}`;
    await loadChatMessages();
    openModal('modal-swap-chat');
}

async function loadChatMessages() {
    if (!activeChatSwapId) return;
    try {
        const res = await fetch(`/api/swaps/${activeChatSwapId}/messages`);
        const messages = await res.json();
        const container = document.getElementById('chat-messages-container');

        if (messages.length === 0) {
            container.innerHTML = `
                <div class="py-12 text-center text-xs text-slate-400">
                    No messages yet. Send a message to coordinate the meetup time and location!
                </div>
            `;
            return;
        }

        container.innerHTML = messages.map(m => `
            <div class="flex flex-col ${m.is_me ? 'items-end' : 'items-start'}">
                <span class="text-[10px] text-slate-400 mb-1 px-1">${m.sender_name} • ${m.created_at.split(' ')[1] || ''}</span>
                <div class="max-w-md px-4 py-2.5 rounded-2xl text-xs ${m.is_me ? 'bg-emerald-600 text-white rounded-br-xs' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-xs shadow-sm'}">
                    ${m.message}
                </div>
            </div>
        `).join('');

        container.scrollTop = container.scrollHeight;
    } catch (err) {
        console.error('Failed to load chat messages:', err);
    }
}

function handleChatKey(e) {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
}

async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    if (!text || !activeChatSwapId) return;

    try {
        const res = await fetch(`/api/swaps/${activeChatSwapId}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        if (data.success) {
            input.value = '';
            await loadChatMessages();
        }
    } catch (err) {
        showToast('Failed to send message', 'error');
    }
}

// ==========================================
// MY WARDROBE & LIST NEW ITEM
// ==========================================

async function loadMyWardrobe() {
    try {
        const res = await fetch('/api/wardrobe');
        myWardrobeItems = await res.json();
        renderWardrobeGrid(myWardrobeItems);
    } catch (err) {
        console.error('Failed to load wardrobe:', err);
    }
}

function renderWardrobeGrid(items) {
    const grid = document.getElementById('wardrobe-grid');
    if (!grid) return;

    if (items.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <i data-lucide="shirt" class="w-8 h-8 text-slate-300 mx-auto mb-2"></i>
                <p class="text-sm font-bold text-slate-700">Your wardrobe is empty</p>
                <p class="text-xs text-slate-400 mt-1">List items you don't wear anymore and earn +15 Eco-Credits!</p>
                <button onclick="openAddItemModal()" class="mt-4 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-sm">
                    + List an Item
                </button>
            </div>
        `;
        lucide.createIcons();
        return;
    }

    grid.innerHTML = items.map(item => `
        <div class="bg-white rounded-3xl overflow-hidden border border-slate-200 shadow-sm flex flex-col">
            <div class="relative h-56 overflow-hidden bg-slate-100">
                <img src="${item.image_url}" class="w-full h-full object-cover">
                <div class="absolute top-3 left-3 bg-slate-900/80 text-emerald-400 font-extrabold text-xs px-2.5 py-1 rounded-xl">
                    Score: ${item.barter_score}
                </div>
                <div class="absolute top-3 right-3 text-xs font-bold px-2 py-0.5 rounded-lg ${item.status === 'available' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
                    ${item.status}
                </div>
            </div>
            <div class="p-4 flex-grow flex flex-col justify-between">
                <div>
                    <span class="text-[10px] text-slate-400 font-bold uppercase">${item.category}</span>
                    <h4 class="font-display font-bold text-sm text-slate-900 truncate mt-0.5">${item.title}</h4>
                    <p class="text-xs text-slate-500">${item.brand || ''} • Size ${item.size}</p>
                </div>
                <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                    <span class="text-[11px] text-emerald-600 font-bold">🌱 ${item.water_saved_l}L Water Saved</span>
                    <button onclick="deleteWardrobeItem(${item.id})" class="text-slate-400 hover:text-red-600 p-1 rounded-lg transition-colors" title="Delete garment">
                        <i data-lucide="trash-2" class="w-4 h-4"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    lucide.createIcons();
}

async function deleteWardrobeItem(itemId) {
    if (!confirm('Are you sure you want to remove this garment from your wardrobe?')) return;
    try {
        const res = await fetch(`/api/items/${itemId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showToast('Garment removed from wardrobe', 'info');
            await loadMyWardrobe();
            await loadMarketplaceItems();
            await loadEcoImpact();
        }
    } catch (err) {
        showToast('Error removing item', 'error');
    }
}

function openAddItemModal() {
    calculateLiveScore();
    openModal('modal-add-item');
}

function cycleSamplePhoto() {
    presetPhotoIdx = (presetPhotoIdx + 1) % PRESET_PHOTOS.length;
    document.getElementById('add-image').value = PRESET_PHOTOS[presetPhotoIdx];
}

function calculateLiveScore() {
    const value = parseFloat(document.getElementById('add-value')?.value || 45);
    const condition = document.getElementById('add-condition')?.value || 'Like New';
    const material = document.getElementById('add-material')?.value || '';

    const condMultipliers = {
        'Brand New with Tags': 1.0,
        'Like New': 0.88,
        'Gently Used': 0.75,
        'Vintage / Well Loved': 0.65
    };

    const sustainable = ['wool', 'cotton', 'linen', 'denim', 'cashmere', 'silk'];
    const bonus = sustainable.some(s => material.toLowerCase().includes(s)) ? 1.15 : 1.0;
    const condMult = condMultipliers[condition] || 0.75;
    const base = Math.min(Math.max(value, 10), 300);

    const score = Math.round(Math.min(Math.max((base * 0.35 + 10) * condMult * bonus, 10), 100) * 10) / 10;
    const el = document.getElementById('live-barter-score');
    if (el) el.innerText = score.toFixed(1);
}

async function handleAddItemSubmit(e) {
    e.preventDefault();
    const payload = {
        title: document.getElementById('add-title').value,
        category: document.getElementById('add-category').value,
        size: document.getElementById('add-size').value,
        brand: document.getElementById('add-brand').value,
        condition: document.getElementById('add-condition').value,
        material: document.getElementById('add-material').value,
        estimated_value: document.getElementById('add-value').value,
        swap_preference: document.getElementById('add-preference').value,
        image_url: document.getElementById('add-image').value,
        description: document.getElementById('add-description').value
    };

    try {
        const res = await fetch('/api/items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            closeModal('modal-add-item');
            showToast(`Listed! You earned +${data.earned_credits} Eco-Credits 🌱`, 'success');
            await loadCurrentUser();
            await loadMyWardrobe();
            await loadMarketplaceItems();
            await loadEcoImpact();
            switchTab('wardrobe');
        } else {
            showToast(data.error || 'Failed to add item', 'error');
        }
    } catch (err) {
        showToast('Error listing item', 'error');
    }
}

// ==========================================
// ITEM DETAIL MODAL
// ==========================================

async function openItemDetailModal(itemId) {
    try {
        const res = await fetch(`/api/items/${itemId}`);
        if (!res.ok) throw new Error('Item not found');
        const item = await res.json();

        const content = document.getElementById('item-detail-content');
        content.innerHTML = `
            <div class="relative h-72 sm:h-96 bg-slate-900">
                <img src="${item.image_url}" class="w-full h-full object-cover">
                <button onclick="closeModal('modal-item-detail')" class="absolute top-4 right-4 bg-slate-900/60 hover:bg-slate-900 text-white p-2 rounded-xl backdrop-blur-sm transition-all">
                    <i data-lucide="x" class="w-5 h-5"></i>
                </button>
                <div class="absolute bottom-4 left-4 bg-slate-900/80 backdrop-blur-md text-emerald-400 font-extrabold text-xs px-3 py-1.5 rounded-xl">
                    ★ ${item.barter_score} Barter Value Score
                </div>
            </div>

            <div class="p-6 sm:p-8 space-y-6">
                <div>
                    <div class="flex items-center justify-between text-xs text-slate-500">
                        <span>${item.category} • Size <strong>${item.size}</strong></span>
                        <span class="bg-emerald-50 text-emerald-700 font-bold px-2.5 py-1 rounded-lg">${item.condition}</span>
                    </div>
                    <h3 class="font-display font-extrabold text-2xl text-slate-900 mt-2">${item.title}</h3>
                    <p class="text-xs text-slate-500 mt-1">Brand: <strong>${item.brand || 'Independent'}</strong> • Material: <strong>${item.material || 'Cotton'}</strong></p>
                </div>

                <!-- Story & Description -->
                <div class="space-y-2">
                    <h4 class="font-bold text-xs uppercase tracking-wider text-slate-400">Garment Story & Fit</h4>
                    <p class="text-sm text-slate-700 leading-relaxed">${item.description || 'Pre-loved garment in wonderful condition looking for a new circular life!'}</p>
                </div>

                <!-- Swap Preference -->
                <div class="bg-emerald-50 border border-emerald-200 rounded-2xl p-4">
                    <span class="text-xs font-bold text-emerald-900 block mb-1">What the owner wants in exchange (ISO):</span>
                    <p class="text-xs text-emerald-800">${item.swap_preference || 'Open to all fair balanced trades'}</p>
                </div>

                <!-- Owner Card -->
                <div class="flex items-center justify-between p-4 rounded-2xl bg-slate-50 border border-slate-100">
                    <div class="flex items-center gap-3">
                        <img src="${item.owner_avatar}" class="w-10 h-10 rounded-xl object-cover">
                        <div>
                            <span class="text-xs font-bold text-slate-900 block">${item.owner_name}</span>
                            <span class="text-[11px] text-slate-500">📍 ${item.address} (${item.distance_miles} mi away)</span>
                        </div>
                    </div>
                    <div class="text-right">
                        <span class="text-xs font-bold text-slate-800">★ ${item.owner_rating}</span>
                        <span class="text-[10px] text-slate-400 block">${item.owner_swaps} completed swaps</span>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
                    <button onclick="closeModal('modal-item-detail')" class="px-5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-600">Close</button>
                    <button onclick="closeModal('modal-item-detail'); openProposeSwapModal(${item.id});" class="px-6 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-md shadow-emerald-600/20 flex items-center gap-1.5">
                        <i data-lucide="repeat-2" class="w-4 h-4"></i> Propose Barter
                    </button>
                </div>
            </div>
        `;
        openModal('modal-item-detail');
        lucide.createIcons();
    } catch (err) {
        showToast('Error opening item details', 'error');
    }
}

// ==========================================
// ECO HUBS & IMPACT METRICS
// ==========================================

async function loadEcoHubs() {
    try {
        const res = await fetch('/api/eco-hubs');
        ecoHubsList = await res.json();

        const grid = document.getElementById('eco-hubs-grid');
        if (grid) {
            grid.innerHTML = ecoHubsList.map(hub => `
                <div class="p-4 rounded-2xl bg-slate-50 border border-slate-200 hover:border-emerald-500 transition-colors flex flex-col justify-between">
                    <div>
                        <span class="text-[10px] bg-blue-100 text-blue-700 font-bold px-2 py-0.5 rounded uppercase">${hub.hub_type}</span>
                        <h4 class="font-display font-bold text-sm text-slate-900 mt-2">${hub.name}</h4>
                        <p class="text-xs text-slate-600 mt-1">${hub.address}</p>
                    </div>
                    <div class="mt-3 pt-2 border-t border-slate-200/60 text-[11px] text-emerald-700 font-medium">
                        🕒 ${hub.hours}
                    </div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error('Failed to load eco hubs:', err);
    }
}

async function loadEcoImpact() {
    try {
        const res = await fetch('/api/eco-impact');
        const data = await res.json();
        const p = data.platform;

        document.getElementById('stat-water').innerText = `${p.water_saved_l.toLocaleString()} L`;
        document.getElementById('stat-co2').innerText = `${p.co2_saved_kg.toLocaleString()} kg`;
        document.getElementById('stat-swaps').innerText = p.completed_swaps.toLocaleString();
        document.getElementById('stat-landfill').innerText = `${p.equivalencies.landfill_kg} kg`;
        document.getElementById('stat-showers').innerText = p.equivalencies.showers_saved.toLocaleString();
        document.getElementById('stat-car-miles').innerText = `${p.equivalencies.car_miles_offset.toLocaleString()} mi`;
        document.getElementById('stat-trees').innerText = `${p.equivalencies.trees_day_equivalent.toLocaleString()} days`;
    } catch (err) {
        console.error('Failed to load eco impact:', err);
    }
}

// ==========================================
// MODALS & TOAST UTILITIES
// ==========================================

function openModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) {
        el.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const el = document.getElementById(modalId);
    if (el) {
        el.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const colors = {
        'success': 'bg-emerald-900 text-emerald-100 border-emerald-700',
        'error': 'bg-red-900 text-red-100 border-red-700',
        'info': 'bg-slate-900 text-slate-100 border-slate-700'
    };

    const toast = document.createElement('div');
    toast.className = `p-4 rounded-2xl shadow-xl border text-xs font-semibold flex items-center gap-2 animate-slide-up pointer-events-auto ${colors[type] || colors.info}`;
    toast.innerHTML = `
        <i data-lucide="${type === 'success' ? 'check-circle' : type === 'error' ? 'alert-circle' : 'info'}" class="w-4 h-4"></i>
        <span>${message}</span>
    `;

    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
