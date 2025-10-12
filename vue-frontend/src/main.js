import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

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

app.use(createPinia())
app.use(router)

app.mount('#app')
