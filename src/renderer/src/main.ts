//import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import Login from './components/Login.vue'
import Home from './components/Home.vue'

const vuetify = createVuetify({
  components,
  directives,
})
const app = createApp(App)

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Login },
    { path: '/home', component: Home }
  ]
})
app.use(router)
app.use(vuetify)
app.mount('#app')
