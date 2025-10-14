
import { createApp } from 'vue';
import SimpleAnalytics from 'simple-analytics-vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import './assets/main.css';
import * as Sentry from '@sentry/vue';


const app = createApp(App);

// Initialize Sentry as early as possible
Sentry.init({
	app,
	dsn: "https://e47d48ee632b1605699c2e234894fc13@o4510181581389824.ingest.de.sentry.io/4510181650268240",
	sendDefaultPii: true
});

// Runtime device input detection: add 'device-touch' class when touch input is available
function updateDeviceClass() {
	try {
		const hasTouch = ('maxTouchPoints' in navigator && navigator.maxTouchPoints > 0) || window.matchMedia('(pointer: coarse)').matches
		if (hasTouch) document.documentElement.classList.add('device-touch')
		else document.documentElement.classList.remove('device-touch')
	} catch {
		// ignore
	}
}

updateDeviceClass()
// Listen for changes to pointer capability
if (window.matchMedia) {
	const mq = window.matchMedia('(pointer: coarse)')
	if (mq && mq.addEventListener) {
		mq.addEventListener('change', updateDeviceClass)
	} else if (mq && mq.addListener) {
		mq.addListener(updateDeviceClass)
	}
	// also listen for maxTouchPoints changes indirectly by checking focus/click events
	window.addEventListener('touchstart', updateDeviceClass, { once: true, passive: true })
}


app.use(createPinia());
app.use(router);

// Register Simple Analytics with skip option for development
app.use(SimpleAnalytics, { skip: import.meta.env.MODE !== 'production' });



// Vue global error handler for Sentry
app.config.errorHandler = (err, vm, info) => {
	Sentry.captureException(err);
	throw err; // rethrow for default behavior
};

app.mount('#app');
