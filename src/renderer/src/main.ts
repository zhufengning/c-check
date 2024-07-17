//import './assets/main.css'
import '@mdi/font/css/materialdesignicons.css' // Ensure you are using css-loader
import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHashHistory } from 'vue-router'
// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import Login from './components/Login.vue'
import Home from './components/Home.vue'
import PrimeVue from 'primevue/config'
import Noir from "./theme/Noir"
const vuetify = createVuetify({
  components,
  directives
})
const app = createApp(App)

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: Login },
    { path: '/home', component: Home },
    { path: '/manage', component: () => import('./components/Manage.vue') },
  ]
})
app.use(router)
app.use(vuetify)
app.use(PrimeVue, {
  theme: {
    preset: Noir
  }
})

import Tree from 'primevue/tree'
app.component('Tree', Tree)
app.mount('#app')
