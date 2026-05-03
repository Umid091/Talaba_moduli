/* =============================================================
   Talaba Moduli — global JavaScript
   ============================================================= */

(function () {
    'use strict';

    // ---- Mobile sidebar toggle ----
    const menuBtn = document.getElementById('menuBtn');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');

    function toggleSidebar(open) {
        if (!sidebar) return;
        const willOpen = open === undefined ? !sidebar.classList.contains('open') : open;
        sidebar.classList.toggle('open', willOpen);
        if (overlay) overlay.classList.toggle('show', willOpen);
        document.body.style.overflow = willOpen ? 'hidden' : '';
    }

    if (menuBtn) menuBtn.addEventListener('click', () => toggleSidebar());
    if (overlay) overlay.addEventListener('click', () => toggleSidebar(false));

    // Close on link click (mobile)
    document.querySelectorAll('.sidebar .nav-link').forEach(a => {
        a.addEventListener('click', () => {
            if (window.innerWidth <= 1024) toggleSidebar(false);
        });
    });

    // ---- Cascading region → district selectors ----
    const regionFields = ['id_home_region', 'id_region']; // student profile, rental
    regionFields.forEach(id => {
        const regionEl = document.getElementById(id);
        if (!regionEl) return;
        const districtId = id.replace('region', 'district');
        const districtEl = document.getElementById(districtId);
        if (!districtEl) return;

        regionEl.addEventListener('change', async () => {
            const url = window.DISTRICTS_API_URL || '/students/api/districts/';
            const currentVal = districtEl.value;

            try {
                const r = await fetch(url + '?region=' + regionEl.value, {
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const data = await r.json();
                districtEl.innerHTML = '<option value="">— Tanlang —</option>';
                data.districts.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value = d.id;
                    opt.textContent = d.name;
                    if (String(d.id) === String(currentVal)) opt.selected = true;
                    districtEl.appendChild(opt);
                });
            } catch (e) {
                console.error('Tumanlarni yuklab bo\'lmadi:', e);
            }
        });
    });

    // ---- Auto-dismiss alerts after 5s ----
    document.querySelectorAll('.alert').forEach(el => {
        if (el.dataset.persist) return;
        setTimeout(() => {
            el.style.transition = 'opacity .4s, transform .4s';
            el.style.opacity = '0';
            el.style.transform = 'translateY(-8px)';
            setTimeout(() => el.remove(), 400);
        }, 5000);
    });

    // ---- Confirm dangerous actions ----
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', e => {
            if (!confirm(el.dataset.confirm)) e.preventDefault();
        });
    });

    // ---- Format numbers with spaces (so'm) ----
    document.querySelectorAll('[data-money]').forEach(el => {
        const v = parseFloat(el.textContent.replace(/\s/g, '')) || 0;
        el.textContent = v.toLocaleString('uz-UZ');
    });

})();
