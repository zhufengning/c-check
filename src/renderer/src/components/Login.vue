<script setup lang="ts">
import { ref } from 'vue'
import { apiPost } from '../../../model/api'
import { useRouter } from 'vue-router';
let user = ref('')
let passwd = ref('')
let msg = ref('')
const router = useRouter()

async function login() {
  let res = await apiPost('check_user', { user: user.value, passwd: passwd.value })
  const data = await res.json();
  console.log(data)
  if (data) {
    let st =await window.api.getStatus()
    console.log(st.user)
    st.user = user.value
    st.passwd = passwd.value
    await window.api.setStatus(st)
    st =await window.api.getStatus()
    console.log(st.user)
    await window.api.goFullscreen()
    router.push('/home')
  } else {
    msg.value = "登录失败"
    isActive.value = true
  }
}

async function reg() {
  let res = await apiPost('create_user', { user: user.value, passwd: passwd.value })
  const data = await res.json();
  console.log(data)
  if (data) {
    msg.value = "注册成功"
    isActive.value = true
  } else {
    msg.value = "注册失败"
    isActive.value = true
  }
}
let isActive = ref(false)
</script>
<template>
  <v-layout>
    <v-app-bar :elevation="2">
      <v-app-bar-title>C语言代码审计</v-app-bar-title>
    </v-app-bar>
    <v-main>
      <v-container>
        <v-text-field v-model="user" label="用户名"></v-text-field>
        <v-text-field v-model="passwd" label="密码" type="password"></v-text-field>
        <v-row>
          <v-btn class="mx-2" text="登录" color="teal-accent-4" @click="login"></v-btn>
          <v-btn text="注册" @click="reg"></v-btn>
        </v-row>
      </v-container>
    </v-main>
    <v-dialog v-model="isActive" max-width="400">
      <v-card title="提示">
        <v-card-text> {{ msg }} </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>

          <v-btn text="关闭" @click="isActive = false"></v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-layout>
</template>
