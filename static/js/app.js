// EcoSwap India - Simple & Intuitive Frontend Controller

let currentUser = null;
let marketplaceItems = [];
let wardrobeItems = [];
let userSwaps = [];
let hubsList = [];

let activeCategory = 'All';
let activeTradeFilter = 'all';
let currentTargetItem = null;
let selectedOfferItemId = null;
let activeChatSwapId = null;
let searchDebounce = null;

const CATEGORIES = [
    'All',
    'Ethnic & Traditional',
    'T-Shirts & Tops',
    'Shirts & Kurtas',
    'Jeans & Trousers',
    'Jackets & Hoodies',
    'Footwear & Shoes',
    'Bags & Accessories'
];

const SAMPLE_PHOTOS = [
    'https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1544441893-675973e31985?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1542272604-780c96856592?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80',
    'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=800&auto=format&fit=crop&q=80'
];
let photoIdx = 0;

document.addEventListener('DOMContentLoaded', async () => {
    renderCategoryPills();
    await checkCurrentUser();
    await loadMarketplace();
    await loadHubs();
});

// ==========================================
// USER AUTHENTICATION & LOGIN
// ==========================================

async function checkCurrentUser() {
    try {
        const res = await fetch('/api/me');
        const data = await res.json();
        currentUser = data.logged_in ? data.user : null;
        renderAuthHeader();

        if (currentUser) {
            await loadWardrobe();
            await loadSwaps();
        }
    } catch (err) {
        console.error('Error checking user session:', err);
    }
}

function renderAuthHeader() {
    const container = document.getElementById('auth-header-container');
    if (!container) return;

    if (currentUser) {
        container.innerHTML = `
            <div class="flex items-center gap-2 bg-slate-100 border border-slate-200 px-3 py-1.5 rounded-xl">
                <img src="${currentUser.avatar_url || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=200&auto=format&fit=crop&q=80'}" class="w-7 h-7 rounded-lg object-cover">
                <div class="text-left hidden sm:block">
                    <span class="block text-xs font-bold text-slate-900 leading-tight">${currentUser.name}</span>
                    <span class="text-[10px] text-emerald-700 font-semibold">${currentUser.area || currentUser.city}</span>
                </div>
                <button onclick="handleLogout()" class="ml-2 text-xs font-bold text-slate-400 hover:text-red-600 transition-colors" title="Logout">
                    Sign Out
                </button>
            </div>
        `;
    } else {
        container.innerHTML = `
            <button onclick="openAuthModal('login')" class="bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs px-4 py-2 rounded-xl transition-all">
                Sign In / Register
            </button>
        `;
    }
}

function openAuthModal(tab = 'login') {
    setAuthTab(tab);
    openModal('modal-auth');
}

function setAuthTab(tab) {
    const isLogin = tab === 'login';
    document.getElementById('form-login').classList.toggle('hidden', !isLogin);
    document.getElementById('form-register').classList.toggle('hidden', isLogin);

    document.getElementById('tab-btn-login').className = isLogin
        ? 'flex-1 py-3 border-b-2 border-emerald-600 text-emerald-800 bg-white'
        : 'flex-1 py-3 border-b-2 border-transparent text-slate-500';

    document.getElementById('tab-btn-register').className = !isLogin
        ? 'flex-1 py-3 border-b-2 border-emerald-600 text-emerald-800 bg-white'
        : 'flex-1 py-3 border-b-2 border-transparent text-slate-500';
}

async function quickDemoLogin(userId) {
    try {
        const res = await fetch(`/api/demo-login/${userId}`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            currentUser = data.user;
            closeModal('modal-auth');
            showToast(`Logged in as ${currentUser.name}!`, 'success');
            renderAuthHeader();
            await loadMarketplace();
            await loadWardrobe();
            await loadSwaps();
        }
    } catch (err) {
        showToast('Login failed', 'error');
    }
}

async function handleLoginSubmit(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (data.success) {
            currentUser = data.user;
            closeModal('modal-auth');
            showToast(`Welcome back, ${currentUser.name}!`, 'success');
            renderAuthHeader();
            await loadMarketplace();
            await loadWardrobe();
            await loadSwaps();
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (err) {
        showToast('Login error', 'error');
    }
}

async function handleRegisterSubmit(e) {
    e.preventDefault();
    const payload = {
        name: document.getElementById('reg-name').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value,
        city: document.getElementById('reg-city').value,
        area: document.getElementById('reg-area').value,
        phone: document.getElementById('reg-phone').value
    };

    try {
        const res = await fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            currentUser = data.user;
            closeModal('modal-auth');
            showToast(`Account created! Welcome, ${currentUser.name}!`, 'success');
            renderAuthHeader();
            await loadMarketplace();
            await loadWardrobe();
            await loadSwaps();
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (err) {
        showToast('Registration error', 'error');
    }
}

async function handleLogout() {
    await fetch('/api/logout', { method: 'POST' });
    currentUser = null;
    showToast('Signed out successfully', 'info');
    renderAuthHeader();
    await loadMarketplace();
    wardrobeItems = [];
    userSwaps = [];
    renderWardrobeGrid();
    renderTradesList();
}

function handleUploadClick() {
    if (!currentUser) {
        openAuthModal('login');
        showToast('Please sign in or use 1-click Demo login first!', 'info');
        return;
    }
    openModal('modal-upload-item');
}

// ==========================================
// TABS & NAVIGATION
// ==========================================

function switchTab(tabName) {
    ['marketplace', 'tradehub', 'wardrobe', 'hubs'].forEach(t => {
        const el = document.getElementById(`tab-${t}`);
        const btn = document.getElementById(`nav-btn-${t}`);
        if (el) el.classList.toggle('hidden', t !== tabName);
        if (btn) btn.classList.toggle('active', t === tabName);
    });

    if (tabName === 'wardrobe') {
        if (!currentUser) {
            openAuthModal('login');
            showToast('Sign in to view your wardrobe', 'info');
        } else {
            loadWardrobe();
        }
    } else if (tabName === 'tradehub') {
        if (!currentUser) {
            openAuthModal('login');
            showToast('Sign in to view your swaps', 'info');
        } else {
            loadSwaps();
        }
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ==========================================
// MARKETPLACE & FILTERING
// ==========================================

function renderCategoryPills() {
    const container = document.getElementById('category-pills');
    if (!container) return;

    container.innerHTML = CATEGORIES.map(cat => `
        <button onclick="selectCategory('${cat}')" class="category-pill ${cat === activeCategory ? 'active' : ''} px-4 py-2 rounded-xl text-xs font-bold transition-all">
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
    clearTimeout(searchDebounce);
    searchDebounce = setTimeout(applyFilters, 300);
}

async function loadMarketplace() {
    const gender = document.getElementById('filter-gender')?.value || 'All';
    const condition = document.getElementById('filter-condition')?.value || 'All';
    const sort = document.getElementById('filter-sort')?.value || 'newest';
    const search = document.getElementById('filter-search')?.value || '';

    const params = new URLSearchParams({
        category: activeCategory,
        gender: gender,
        condition: condition,
        sort: sort,
        search: search
    });

    try {
        const res = await fetch(`/api/items?${params.toString()}`);
        marketplaceItems = await res.json();
        renderMarketplaceGrid();
    } catch (err) {
        console.error('Failed to load items:', err);
    }
}

function applyFilters() {
    loadMarketplace();
}

function resetFilters() {
    activeCategory = 'All';
    document.getElementById('filter-gender').value = 'All';
    document.getElementById('filter-condition').value = 'All';
    document.getElementById('filter-sort').value = 'newest';
    document.getElementById('filter-search').value = '';
    renderCategoryPills();
    applyFilters();
}

function renderMarketplaceGrid() {
    const grid = document.getElementById('items-grid');
    const countDisplay = document.getElementById('items-count-display');
    if (!grid) return;

    countDisplay.innerText = marketplaceItems.length;

    if (marketplaceItems.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center bg-white rounded-3xl border border-slate-200">
                <p class="text-3xl mb-2">🔍</p>
                <h3 class="font-bold text-slate-800 text-base">No clothes match this filter</h3>
                <p class="text-xs text-slate-400 mt-1">Try resetting filters or searching another keyword.</p>
                <button onclick="resetFilters()" class="mt-4 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs rounded-xl">
                    Reset Filters
                </button>
            </div>
        `;
        return;
    }

    grid.innerHTML = marketplaceItems.map(item => `
        <div class="bg-white rounded-3xl overflow-hidden border border-slate-200 shadow-sm hover:shadow-lg transition-all flex flex-col justify-between">
            <div>
                <!-- Image Container -->
                <div class="relative h-64 overflow-hidden bg-slate-100">
                    <img src="${item.image_url}" class="w-full h-full object-cover">
                    <!-- Price Tag in Rupees -->
                    <div class="absolute top-3 left-3 bg-slate-900/90 text-white text-xs font-black px-3 py-1 rounded-xl shadow-md">
                        ₹${item.price_inr.toLocaleString('en-IN')}
                    </div>
                    <!-- Condition Tag -->
                    <div class="absolute bottom-3 left-3 bg-emerald-600/90 text-white font-bold text-[10px] px-2.5 py-0.5 rounded-lg">
                        ${item.condition}
                    </div>
                    <!-- City/Area -->
                    <div class="absolute top-3 right-3 bg-white/95 text-slate-700 font-bold text-[11px] px-2.5 py-1 rounded-xl shadow-sm">
                        📍 ${item.owner_area || item.city}
                    </div>
                </div>

                <!-- Content -->
                <div class="p-5 space-y-2">
                    <div class="flex items-center justify-between text-xs text-slate-400 font-semibold">
                        <span>${item.category}</span>
                        <span class="bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-bold">Size ${item.size}</span>
                    </div>

                    <h3 class="font-bold text-base text-slate-900 line-clamp-1">${item.title}</h3>

                    <p class="text-xs text-slate-500">
                        ${item.brand ? `<strong>${item.brand}</strong> • ` : ''}${item.material || 'Cotton'}
                    </p>

                    <!-- What the owner wants -->
                    <div class="bg-slate-50 border border-slate-100 p-2.5 rounded-xl text-[11px] text-slate-600">
                        <strong>Wants in return:</strong> ${item.swap_preference || 'Open to any fair swap'}
                    </div>
                </div>
            </div>

            <!-- Footer: Owner & Swap CTA -->
            <div class="p-5 pt-0">
                <div class="pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2 min-w-0">
                        <img src="${item.owner_avatar}" class="w-7 h-7 rounded-lg object-cover">
                        <div class="min-w-0">
                            <span class="block text-xs font-bold text-slate-800 truncate">${item.owner_name}</span>
                            <span class="text-[10px] text-slate-400">${item.owner_swaps} successful swaps</span>
                        </div>
                    </div>

                    <button onclick="handleProposeSwapClick(${item.id})" class="bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs px-4 py-2 rounded-xl shadow-sm transition-all whitespace-nowrap">
                        Swap 🤝
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// ==========================================
// PROPOSE SWAP (VALUE MATCH IN ₹)
// ==========================================

async function handleProposeSwapClick(targetItemId) {
    if (!currentUser) {
        openAuthModal('login');
        showToast('Please sign in to propose swaps!', 'info');
        return;
    }

    try {
        const res = await fetch(`/api/fair-match/${targetItemId}`);
        if (!res.ok) {
            const err = await res.json();
            showToast(err.error || 'Cannot match items', 'error');
            return;
        }

        const data = await res.json();
        currentTargetItem = data.target_item;
        const matches = data.matches;

        // Render target item
        document.getElementById('propose-target-card').innerHTML = `
            <img src="${currentTargetItem.image_url}" class="w-20 h-24 object-cover rounded-xl flex-shrink-0">
            <div class="min-w-0 flex-grow">
                <span class="text-[10px] bg-slate-200 font-bold px-2 py-0.5 rounded text-slate-700 uppercase">${currentTargetItem.category}</span>
                <h4 class="font-bold text-sm text-slate-900 mt-1 truncate">${currentTargetItem.title}</h4>
                <p class="text-xs text-slate-500">${currentTargetItem.brand || ''} • Size ${currentTargetItem.size}</p>
                <div class="mt-2 text-xs font-black text-emerald-800 bg-emerald-100 px-2 py-1 rounded inline-block">
                    Value: ₹${currentTargetItem.price_inr.toLocaleString('en-IN')}
                </div>
            </div>
        `;

        // Render your wardrobe list
        const list = document.getElementById('propose-wardrobe-list');
        if (matches.length === 0) {
            list.innerHTML = `
                <div class="p-6 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                    <p class="text-xs text-slate-500">Your wardrobe is empty! Add clothes first to swap.</p>
                    <button onclick="closeModal('modal-propose-swap'); openModal('modal-upload-item');" class="mt-2 text-xs font-bold text-emerald-600 hover:underline">
                        + Upload Clothes to Wardrobe
                    </button>
                </div>
            `;
            document.getElementById('propose-comparison-box').classList.add('hidden');
        } else {
            document.getElementById('propose-comparison-box').classList.remove('hidden');
            selectedOfferItemId = matches[0].my_item.id;

            list.innerHTML = matches.map((m, idx) => `
                <div onclick="selectOfferGarment(${m.my_item.id}, ${JSON.stringify(m.comparison).replace(/"/g, '&quot;')})" 
                     id="offer-card-${m.my_item.id}"
                     class="offer-garment-card p-3 rounded-2xl border ${idx === 0 ? 'border-emerald-500 bg-emerald-50/50' : 'border-slate-200 hover:border-slate-300'} cursor-pointer transition-all flex items-center gap-3">
                    <img src="${m.my_item.image_url}" class="w-12 h-14 object-cover rounded-xl flex-shrink-0">
                    <div class="flex-grow min-w-0">
                        <div class="text-xs font-bold text-slate-900 truncate">${m.my_item.title}</div>
                        <div class="text-[11px] text-slate-500">Size ${m.my_item.size} • Value: <strong>₹${m.my_item.price_inr.toLocaleString('en-IN')}</strong></div>
                    </div>
                    <div class="text-right flex-shrink-0">
                        <span class="inline-block text-xs font-bold px-2 py-0.5 rounded-lg ${m.comparison.difference_inr <= 250 ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'}">
                            ${m.comparison.match_pct}% Match
                        </span>
                    </div>
                </div>
            `).join('');

            updateComparisonDisplay(matches[0].comparison);
        }

        openModal('modal-propose-swap');
    } catch (err) {
        showToast('Error loading swap details', 'error');
    }
}

function selectOfferGarment(itemId, comparison) {
    selectedOfferItemId = itemId;
    document.querySelectorAll('.offer-garment-card').forEach(c => {
        c.classList.remove('border-emerald-500', 'bg-emerald-50/50');
        c.classList.add('border-slate-200');
    });
    const card = document.getElementById(`offer-card-${itemId}`);
    if (card) {
        card.classList.add('border-emerald-500', 'bg-emerald-50/50');
        card.classList.remove('border-slate-200');
    }
    updateComparisonDisplay(comparison);
}

function updateComparisonDisplay(comp) {
    document.getElementById('comp-verdict').innerText = comp.verdict;
    document.getElementById('comp-advice').innerText = comp.advice;

    const extraCashInput = document.getElementById('propose-extra-cash');
    if (extraCashInput && comp.suggested_extra_inr > 0) {
        extraCashInput.value = comp.suggested_extra_inr;
    }
}

async function submitSwapProposal() {
    if (!currentTargetItem || !selectedOfferItemId) {
        showToast('Please pick an item from your wardrobe to swap', 'error');
        return;
    }

    const extraCash = document.getElementById('propose-extra-cash').value;
    const meetup = document.getElementById('propose-meetup').value;
    const note = document.getElementById('propose-note').value;

    try {
        const res = await fetch('/api/swaps/propose', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                requested_item_id: currentTargetItem.id,
                offered_item_id: selectedOfferItemId,
                extra_cash_inr: extraCash,
                meet_location: meetup,
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
        showToast('Error sending swap proposal', 'error');
    }
}

// ==========================================
// MY SWAPS MANAGEMENT
// ==========================================

async function loadSwaps() {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/swaps');
        userSwaps = await res.json();

        // Update badge
        const pendingCount = userSwaps.filter(s => !s.is_requester && s.status === 'pending').length;
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

    let filtered = userSwaps;
    if (activeTradeFilter === 'incoming') filtered = userSwaps.filter(s => !s.is_requester);
    if (activeTradeFilter === 'outgoing') filtered = userSwaps.filter(s => s.is_requester);

    if (filtered.length === 0) {
        container.innerHTML = `
            <div class="py-16 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <p class="text-3xl mb-1">🤝</p>
                <p class="text-sm font-bold text-slate-700">No swap proposals here yet</p>
                <p class="text-xs text-slate-400 mt-1">Browse clothes and propose your first swap!</p>
                <button onclick="switchTab('marketplace')" class="mt-4 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-sm">
                    Browse Clothes
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = filtered.map(swap => {
        const isIncoming = !swap.is_requester;
        const otherName = isIncoming ? swap.requester_name : swap.receiver_name;
        const otherAvatar = isIncoming ? swap.requester_avatar : swap.receiver_avatar;

        const statusClass = {
            'pending': 'bg-amber-100 text-amber-800',
            'accepted': 'bg-emerald-100 text-emerald-800',
            'declined': 'bg-red-100 text-red-800',
            'completed': 'bg-blue-100 text-blue-800',
            'cancelled': 'bg-slate-100 text-slate-600'
        }[swap.status] || 'bg-slate-100 text-slate-700';

        return `
            <div class="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm space-y-4">
                <div class="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div class="flex items-center gap-2">
                        <img src="${otherAvatar}" class="w-8 h-8 rounded-lg object-cover">
                        <div>
                            <span class="text-xs font-bold text-slate-900">${isIncoming ? `Offer received from ${otherName}` : `Offer sent to ${otherName}`}</span>
                            <span class="block text-[10px] text-slate-400">${swap.created_at}</span>
                        </div>
                    </div>
                    <span class="text-[10px] font-bold px-2.5 py-1 rounded-lg uppercase ${statusClass}">
                        ${swap.status}
                    </span>
                </div>

                <!-- Swap Items Comparison in ₹ -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-xl items-center text-xs">
                    <div class="flex items-center gap-3">
                        <img src="${swap.offered_image}" class="w-14 h-16 object-cover rounded-xl">
                        <div class="min-w-0">
                            <span class="text-[10px] font-bold text-emerald-700 uppercase">${isIncoming ? "THEY OFFER" : "YOU OFFER"}</span>
                            <h4 class="font-bold text-slate-900 truncate">${swap.offered_title}</h4>
                            <p class="text-[11px] text-slate-500">Size ${swap.offered_size} • Value: <strong>₹${swap.offered_price.toLocaleString('en-IN')}</strong></p>
                        </div>
                    </div>

                    <div class="flex items-center gap-3">
                        <img src="${swap.requested_image}" class="w-14 h-16 object-cover rounded-xl">
                        <div class="min-w-0">
                            <span class="text-[10px] font-bold text-blue-700 uppercase">${isIncoming ? "FOR YOUR" : "FOR THEIR"}</span>
                            <h4 class="font-bold text-slate-900 truncate">${swap.requested_title}</h4>
                            <p class="text-[11px] text-slate-500">Size ${swap.requested_size} • Value: <strong>₹${swap.requested_price.toLocaleString('en-IN')}</strong></p>
                        </div>
                    </div>
                </div>

                <!-- Meetup and Action Controls -->
                <div class="flex flex-wrap items-center justify-between text-xs text-slate-600 gap-2">
                    <div class="flex items-center gap-3">
                        <span><strong>📍 Location:</strong> ${swap.meet_location}</span>
                        ${swap.extra_cash_inr > 0 ? `
                            <span class="bg-emerald-50 text-emerald-800 font-bold px-2 py-0.5 rounded text-[11px]">
                                + ₹${swap.extra_cash_inr} extra cash offered
                            </span>
                        ` : ''}
                    </div>

                    <div class="flex items-center gap-2">
                        <button onclick="openChat(${swap.id}, '${otherName}')" class="px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl font-bold">
                            💬 Chat
                        </button>

                        ${isIncoming && swap.status === 'pending' ? `
                            <button onclick="handleSwapAction(${swap.id}, 'accept')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold">
                                Accept Swap
                            </button>
                            <button onclick="handleSwapAction(${swap.id}, 'decline')" class="px-3 py-1.5 bg-slate-200 hover:bg-red-100 hover:text-red-700 text-slate-600 rounded-xl font-bold">
                                Decline
                            </button>
                        ` : ''}

                        ${swap.status === 'accepted' ? `
                            <button onclick="handleSwapAction(${swap.id}, 'complete')" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold">
                                ✅ Confirm Swap Completed
                            </button>
                        ` : ''}

                        ${!isIncoming && swap.status === 'pending' ? `
                            <button onclick="handleSwapAction(${swap.id}, 'cancel')" class="px-3 py-1.5 text-slate-400 hover:text-red-600 font-semibold">
                                Cancel
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

async function handleSwapAction(swapId, action) {
    try {
        const res = await fetch(`/api/swaps/${swapId}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        const data = await res.json();
        if (data.success) {
            showToast(`Swap ${action.toUpperCase()}!`, 'success');
            await loadSwaps();
            await loadWardrobe();
            await loadMarketplace();
        } else {
            showToast(data.error || 'Action failed', 'error');
        }
    } catch (err) {
        showToast('Error updating swap', 'error');
    }
}

// ==========================================
// SWAP CHAT
// ==========================================

async function openChat(swapId, name) {
    activeChatSwapId = swapId;
    document.getElementById('chat-title').innerText = `Chat with ${name}`;
    document.getElementById('chat-subtitle').innerText = `Coordinate meetup time and place`;
    await loadMessages();
    openModal('modal-swap-chat');
}

async function loadMessages() {
    if (!activeChatSwapId) return;
    try {
        const res = await fetch(`/api/swaps/${activeChatSwapId}/messages`);
        const messages = await res.json();
        const container = document.getElementById('chat-messages-container');

        if (messages.length === 0) {
            container.innerHTML = `<p class="text-xs text-slate-400 text-center py-8">No messages yet. Say hello and coordinate meetup time!</p>`;
            return;
        }

        container.innerHTML = messages.map(m => `
            <div class="flex flex-col ${m.is_me ? 'items-end' : 'items-start'}">
                <span class="text-[10px] text-slate-400 mb-0.5 px-1">${m.sender_name}</span>
                <div class="max-w-xs px-3.5 py-2 rounded-2xl text-xs ${m.is_me ? 'bg-emerald-600 text-white' : 'bg-white border border-slate-200 text-slate-800 shadow-sm'}">
                    ${m.message}
                </div>
            </div>
        `).join('');

        container.scrollTop = container.scrollHeight;
    } catch (err) {
        console.error('Failed to load chat messages:', err);
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
            await loadMessages();
        }
    } catch (err) {
        showToast('Failed to send message', 'error');
    }
}

// ==========================================
// MY WARDROBE & UPLOAD
// ==========================================

async function loadWardrobe() {
    if (!currentUser) return;
    try {
        const res = await fetch('/api/wardrobe');
        wardrobeItems = await res.json();
        renderWardrobeGrid();
    } catch (err) {
        console.error('Failed to load wardrobe:', err);
    }
}

function renderWardrobeGrid() {
    const grid = document.getElementById('wardrobe-grid');
    if (!grid) return;

    if (wardrobeItems.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center bg-slate-50 rounded-2xl border border-dashed border-slate-200">
                <p class="text-3xl mb-1">🧥</p>
                <p class="text-sm font-bold text-slate-700">Your wardrobe is empty</p>
                <p class="text-xs text-slate-400 mt-1">Upload clothes you don't wear so you can swap them!</p>
                <button onclick="handleUploadClick()" class="mt-4 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-sm">
                    + Upload Clothes
                </button>
            </div>
        `;
        return;
    }

    grid.innerHTML = wardrobeItems.map(item => `
        <div class="bg-white rounded-3xl overflow-hidden border border-slate-200 shadow-sm flex flex-col justify-between">
            <div>
                <div class="relative h-56 overflow-hidden bg-slate-100">
                    <img src="${item.image_url}" class="w-full h-full object-cover">
                    <div class="absolute top-3 left-3 bg-slate-900/90 text-white text-xs font-black px-2.5 py-1 rounded-xl">
                        ₹${item.price_inr.toLocaleString('en-IN')}
                    </div>
                    <div class="absolute top-3 right-3 text-xs font-bold px-2 py-0.5 rounded-lg ${item.status === 'available' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
                        ${item.status}
                    </div>
                </div>

                <div class="p-4">
                    <span class="text-[10px] text-slate-400 font-bold uppercase">${item.category}</span>
                    <h4 class="font-bold text-sm text-slate-900 truncate mt-0.5">${item.title}</h4>
                    <p class="text-xs text-slate-500">${item.brand || ''} • Size ${item.size}</p>
                </div>
            </div>

            <div class="p-4 pt-0">
                <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
                    <span class="text-[11px] text-emerald-700 font-bold">💧 ${item.water_saved_l}L Water Saved</span>
                    <button onclick="deleteGarment(${item.id})" class="text-slate-400 hover:text-red-600 text-xs font-bold">
                        Delete
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function cycleUploadPhoto() {
    photoIdx = (photoIdx + 1) % SAMPLE_PHOTOS.length;
    document.getElementById('up-image').value = SAMPLE_PHOTOS[photoIdx];
}

async function handleUploadSubmit(e) {
    e.preventDefault();
    const payload = {
        title: document.getElementById('up-title').value,
        category: document.getElementById('up-category').value,
        size: document.getElementById('up-size').value,
        brand: document.getElementById('up-brand').value,
        condition: document.getElementById('up-condition').value,
        price_inr: document.getElementById('up-price').value,
        material: document.getElementById('up-material').value,
        swap_preference: document.getElementById('up-preference').value,
        image_url: document.getElementById('up-image').value,
        description: document.getElementById('up-description').value
    };

    try {
        const res = await fetch('/api/items', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            closeModal('modal-upload-item');
            showToast('Clothes uploaded to your wardrobe successfully!', 'success');
            await loadWardrobe();
            await loadMarketplace();
            switchTab('wardrobe');
        } else {
            showToast(data.error || 'Failed to upload', 'error');
        }
    } catch (err) {
        showToast('Error uploading clothes', 'error');
    }
}

async function deleteGarment(itemId) {
    if (!confirm('Are you sure you want to remove this garment from your wardrobe?')) return;
    try {
        const res = await fetch(`/api/items/${itemId}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            showToast('Removed from wardrobe', 'info');
            await loadWardrobe();
            await loadMarketplace();
        }
    } catch (err) {
        showToast('Failed to delete item', 'error');
    }
}

// ==========================================
// SAFE MEETING SPOTS & HUBS
// ==========================================

async function loadHubs() {
    try {
        const res = await fetch('/api/eco-hubs');
        hubsList = await res.json();
        const grid = document.getElementById('hubs-grid');
        if (grid) {
            grid.innerHTML = hubsList.map(h => `
                <div class="p-5 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col justify-between">
                    <div>
                        <span class="text-[10px] font-bold bg-emerald-100 text-emerald-800 px-2 py-0.5 rounded uppercase">${h.hub_type}</span>
                        <h4 class="font-bold text-sm text-slate-900 mt-2">${h.name}</h4>
                        <p class="text-xs text-slate-600 mt-1">${h.address}, ${h.city}</p>
                    </div>
                    <div class="mt-4 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px]">
                        <span class="text-emerald-700 font-bold">🕒 ${h.timings}</span>
                        <span class="text-slate-500">${h.description}</span>
                    </div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error('Failed to load hubs:', err);
    }
}

// ==========================================
// MODAL & TOAST HELPERS
// ==========================================

function openModal(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) {
        el.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `p-4 rounded-2xl shadow-xl text-xs font-bold text-white flex items-center gap-2 pointer-events-auto ${type === 'success' ? 'bg-emerald-800' : type === 'error' ? 'bg-red-800' : 'bg-slate-900'}`;
    toast.innerHTML = `<span>${type === 'success' ? '✅' : type === 'error' ? '⚠️' : 'ℹ️'}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
