import fs from 'fs';
import vm from 'vm';

const source = fs.readFileSync(new URL('../../www/scripts/store-cta.js', import.meta.url), 'utf8');

function boot(options) {
    const htmlClasses = new Set();
    const bodyClasses = new Set();
    const events = [];
    const gtagCalls = [];
    const store = {};
    if (options.dismissed) store['tutormate-ios-bar-dismissed'] = '1';

    const bar = { hidden: true };
    const dismiss = { listeners: {} };
    dismiss.addEventListener = (type, fn) => {
        dismiss.listeners[type] = fn;
    };

    const document = {
        documentElement: { classList: { add: (name) => htmlClasses.add(name) } },
        body: {
            classList: {
                add: (name) => bodyClasses.add(name),
                remove: (name) => bodyClasses.delete(name),
            },
        },
        getElementById: (id) => (id === 'ios-download-bar' ? bar : id === 'ios-download-dismiss' ? dismiss : null),
        addEventListener: (type, fn) => {
            document.listeners = document.listeners || {};
            document.listeners[type] = fn;
        },
        dispatchEvent: (event) => events.push(event),
    };

    const context = {
        navigator: {
            userAgent: options.ua,
            platform: options.platform || '',
            maxTouchPoints: options.maxTouchPoints || 0,
        },
        location: { pathname: options.pathname || '/algebra/' },
        sessionStorage: {
            getItem: (key) => (key in store ? store[key] : null),
            setItem: (key, value) => {
                store[key] = String(value);
            },
        },
        CustomEvent: class CustomEvent {
            constructor(type, init) {
                this.type = type;
                this.detail = init && init.detail;
            }
        },
        window: {
            gtag: options.withGtag ? (...args) => gtagCalls.push(args) : undefined,
            Capacitor: options.native ? { isNativePlatform: () => true } : undefined,
        },
        document,
    };
    context.window.window = context.window;
    vm.runInNewContext(source, context, { filename: 'store-cta.js' });
    return { htmlClasses, bodyClasses, bar, dismiss, events, document, gtagCalls, store };
}

function click(document, node) {
    document.listeners.click({ target: node });
}

function anchor(attrs) {
    return {
        attrs,
        getAttribute: (name) => (name in attrs ? attrs[name] : null),
        closest: function (selector) {
            return selector === 'a[data-placement]' ? this : null;
        },
    };
}

const failures = [];
function check(condition, message) {
    if (!condition) failures.push(message);
}

const iphone = boot({
    ua: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 Version/17.5 Mobile/15E148 Safari/604.1',
});
check(iphone.htmlClasses.has('is-ios'), 'iPhone adds is-ios');
check(iphone.bar.hidden === false, 'iPhone shows the download bar');
check(iphone.bodyClasses.has('has-ios-bar'), 'iPhone reserves space for the bar');

iphone.dismiss.listeners.click();
check(iphone.bar.hidden === true, 'dismiss hides the bar');
check(!iphone.bodyClasses.has('has-ios-bar'), 'dismiss removes the spacer');
check(iphone.store['tutormate-ios-bar-dismissed'] === '1', 'dismiss is remembered for the tab');

const again = boot({
    ua: iphone ? 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X)' : '',
    dismissed: true,
});
check(again.bar.hidden === true, 'a dismissed iPhone tab does not reopen the bar');
check(again.htmlClasses.has('is-ios'), 'dismiss does not remove the iOS layout');

const desktop = boot({
    ua: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    platform: 'MacIntel',
    maxTouchPoints: 0,
});
check(!desktop.htmlClasses.has('is-ios'), 'desktop Safari does not get the iOS layout');
check(desktop.bar.hidden === true, 'desktop leaves the download bar hidden');

const ipad = boot({
    ua: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.5 Safari/605.1.15',
    platform: 'MacIntel',
    maxTouchPoints: 5,
});
check(ipad.htmlClasses.has('is-ios'), 'iPadOS desktop user agent is treated as iOS');

const native = boot({
    ua: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X)',
    native: true,
});
check(!native.htmlClasses.has('is-ios'), 'the native app shell does not add the marketing bar');
check(native.bar.hidden === true, 'the native app shell leaves the bar hidden');

const measured = boot({
    ua: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0',
    pathname: '/biology/',
    withGtag: true,
});
click(measured.document, anchor({
    href: 'https://apps.apple.com/app/id6793738685',
    'data-placement': 'section',
}));
check(measured.events.length === 1, 'App Store click emits one event');
const detail = measured.events[0] && measured.events[0].detail;
check(detail && detail.page_path === '/biology/' && detail.placement === 'section', 'event carries path and placement');
check(Object.keys(detail || {}).sort().join() === 'page_path,placement', 'event has no other fields');
check(JSON.stringify(detail).indexOf('mitochondri') === -1, 'event does not include page content');
check(measured.gtagCalls.length === 1, 'existing gtag receives the click');
check(measured.gtagCalls[0][0] === 'event' && measured.gtagCalls[0][1] === 'app_store_click', 'gtag event name');
check(!('homework' in (measured.gtagCalls[0][2] || {})), 'gtag payload has no homework field');

const silent = boot({ ua: 'Mozilla/5.0 (Windows NT 10.0) Chrome/120.0.0.0', pathname: '/' });
click(silent.document, anchor({ href: '/app/', 'data-placement': 'hero' }));
click(silent.document, { closest: () => null });
check(silent.events.length === 0, 'browser links and non-links are not measured');
check(silent.gtagCalls.length === 0, 'gtag is not called when it was not already on the page');

if (failures.length) {
    console.error(`${failures.length} store CTA check(s) failed:`);
    for (const item of failures) console.error(`  - ${item}`);
    process.exit(1);
}
console.log('ok: iOS bar, dismiss, native shell, and App Store click payload');
