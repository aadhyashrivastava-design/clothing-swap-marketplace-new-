// Leaflet Interactive Map Module for EcoSwap

let mapInstance = null;
let itemMarkersLayer = null;
let hubMarkersLayer = null;
let userMarker = null;

function initMap(userLat = 47.6150, userLon = -122.3200) {
    const container = document.getElementById('map-container');
    if (!container) return;

    if (typeof L === 'undefined') {
        console.warn('Leaflet map library is not loaded');
        container.innerHTML = '<div class="flex items-center justify-center h-full text-slate-400 text-xs font-semibold">Interactive map view active (Leaflet loading...)</div>';
        return;
    }

    if (mapInstance) {
        mapInstance.invalidateSize();
        return;
    }

    // Initialize Map
    mapInstance = L.map('map-container').setView([userLat, userLon], 12);

    // Clean Tile Layer from OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors',
        maxZoom: 18,
    }).addTo(mapInstance);

    itemMarkersLayer = L.layerGroup().addTo(mapInstance);
    hubMarkersLayer = L.layerGroup().addTo(mapInstance);

    // Plot User Location Marker
    const userIcon = L.divIcon({
        className: 'custom-pin-user',
        html: '📍',
        iconSize: [36, 36],
        iconAnchor: [18, 18]
    });

    userMarker = L.marker([userLat, userLon], { icon: userIcon })
        .addTo(mapInstance)
        .bindPopup(`
            <div style="font-family: 'Plus Jakarta Sans', sans-serif; padding: 4px;">
                <strong style="color: #064e3b; font-size: 13px;">Your Current Location</strong>
                <p style="margin: 2px 0 0 0; font-size: 11px; color: #64748b;">Capitol Hill, Seattle, WA</p>
                <div style="margin-top: 6px; font-size: 10px; background: #ecfdf5; color: #047857; padding: 2px 6px; border-radius: 4px; font-weight: 600; display: inline-block;">
                    Zero-carbon radius active
                </div>
            </div>
        `);
}

function updateMapMarkers(items, hubs) {
    if (!mapInstance) return;

    // Clear previous markers
    if (itemMarkersLayer) itemMarkersLayer.clearLayers();
    if (hubMarkersLayer) hubMarkersLayer.clearLayers();

    // Plot Items
    if (items && items.length > 0) {
        items.forEach(item => {
            if (!item.latitude || !item.longitude) return;

            const itemIcon = L.divIcon({
                className: 'custom-pin-item',
                html: '🧥',
                iconSize: [32, 32],
                iconAnchor: [16, 16]
            });

            const marker = L.marker([item.latitude, item.longitude], { icon: itemIcon });
            
            const popupHtml = `
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; width: 200px;">
                    <img src="${item.image_url}" alt="${item.title}" style="width: 100%; height: 110px; object-fit: cover; border-radius: 8px; margin-bottom: 6px;">
                    <strong style="display: block; font-size: 12px; color: #0f172a; line-height: 1.2;">${item.title}</strong>
                    <div style="font-size: 10px; color: #64748b; margin-top: 2px;">
                        <span>${item.brand || 'Vintage'}</span> • <span>Size ${item.size}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px;">
                        <span style="background: #ecfdf5; color: #059669; font-weight: bold; font-size: 10px; padding: 2px 6px; border-radius: 4px;">
                            ${item.barter_score} Barter Score
                        </span>
                        <span style="font-size: 10px; color: #475569;">${item.distance_miles} mi away</span>
                    </div>
                    <button onclick="openProposeSwapModal(${item.id})" style="width: 100%; margin-top: 8px; background: #059669; color: white; border: none; padding: 6px; border-radius: 6px; font-size: 11px; font-weight: bold; cursor: pointer;">
                        Propose Barter 🤝
                    </button>
                </div>
            `;
            marker.bindPopup(popupHtml);
            itemMarkersLayer.addLayer(marker);
        });
    }

    // Plot Community Eco Hubs
    if (hubs && hubs.length > 0) {
        hubs.forEach(hub => {
            const hubIcon = L.divIcon({
                className: 'custom-pin-hub',
                html: '☕️',
                iconSize: [34, 34],
                iconAnchor: [17, 17]
            });

            const marker = L.marker([hub.latitude, hub.longitude], { icon: hubIcon });
            const hubHtml = `
                <div style="font-family: 'Plus Jakarta Sans', sans-serif; width: 210px;">
                    <span style="background: #eff6ff; color: #2563eb; font-size: 9px; font-weight: bold; padding: 2px 6px; border-radius: 4px; text-transform: uppercase;">
                        ${hub.hub_type}
                    </span>
                    <strong style="display: block; font-size: 13px; color: #1e3a8a; margin-top: 4px;">${hub.name}</strong>
                    <p style="font-size: 11px; color: #475569; margin: 4px 0;">${hub.address}</p>
                    <p style="font-size: 10px; color: #059669; font-weight: 600;">🕒 ${hub.hours}</p>
                    <p style="font-size: 10px; color: #64748b; margin-top: 4px;">${hub.description}</p>
                </div>
            `;
            marker.bindPopup(hubHtml);
            hubMarkersLayer.addLayer(marker);
        });
    }
}
