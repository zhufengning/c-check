<template>
  <v-layout>
    <v-app-bar :elevation="2">
      <v-app-bar-title>C语言代码审计</v-app-bar-title>
    </v-app-bar>
    <v-main>
      <v-container>

        <v-text-field label="用户名"></v-text-field>
        <v-text-field label="密码" type="password"></v-text-field>
        <v-row>
          <v-btn class="mx-2" text="登录" color="teal-accent-4"></v-btn>
          <v-btn text="注册"></v-btn>
        </v-row>
      </v-container>
        <router-link to="/home">111</router-link>
    </v-main>
  </v-layout>
</template>
