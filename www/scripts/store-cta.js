/* iPhone download bar and App Store click hook.

   Measurement is intentionally inert until an analytics function already
   exists on the page. This file does not load a tracker, does not read
   homework or any other page text, and does not invent an Apple provider
   token. Setup that still has to happen outside the repo is documented in
   docs/analytics/app-store-clicks.md.
*/
(function () {
    var ua = navigator.userAgent || '';
    var iOS = /iPad|iPhone|iPod/.test(ua) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    var native = window.Capacitor && window.Capacitor.isNativePlatform && window.Capacitor.isNativePlatform();
    if (native) return;

    if (iOS) document.documentElement.classList.add('is-ios');

    var bar = document.getElementById('ios-download-bar');
    var dismiss = document.getElementById('ios-download-dismiss');
    var storageKey = 'tutormate-ios-bar-dismissed';
    var dismissed = false;
    try {
        dismissed = sessionStorage.getItem(storageKey) === '1';
    } catch (e) {
        dismissed = false;
    }

    if (iOS && bar && !dismissed) {
        bar.hidden = false;
        document.body.classList.add('has-ios-bar');
    }

    if (dismiss && bar) {
        dismiss.addEventListener('click', function () {
            bar.hidden = true;
            document.body.classList.remove('has-ios-bar');
            try {
                sessionStorage.setItem(storageKey, '1');
            } catch (e) {
                /* Private mode can reject storage. The bar still closes. */
            }
        });
    }

    document.addEventListener('click', function (event) {
        var target = event.target;
        if (!target || !target.closest) return;
        var link = target.closest('a[data-placement]');
        if (!link) return;
        var href = link.getAttribute('href') || '';
        if (href.indexOf('apps.apple.com') === -1) return;

        var detail = {
            page_path: location.pathname || '/',
            placement: link.getAttribute('data-placement') || 'unspecified'
        };

        document.dispatchEvent(new CustomEvent('tutormate:app-store-click', { detail: detail }));

        if (typeof window.gtag === 'function') {
            window.gtag('event', 'app_store_click', {
                page_path: detail.page_path,
                placement: detail.placement
            });
        }
    }, true);
})();
