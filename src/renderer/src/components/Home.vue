<script setup lang="ts">
import { ComponentPublicInstance, onMounted, ref } from 'vue'
import * as monaco from 'monaco-editor'
import { useRouter } from 'vue-router';
import { nextTick } from 'vue';
//const ipcHandle = () => window.electron.ipcRenderer.send('ping')
let editor1: monaco.editor.IStandaloneCodeEditor
let editor_container = ref<ComponentPublicInstance | null>(null)
const decorations: monaco.editor.IEditorDecorationsCollection[] = []
const router = useRouter()
onMounted(async () => {
  await router.isReady()
  await nextTick()
  setTimeout(() => {
    editor1 = monaco.editor.create(editor_container.value, {
      value: 'console.log("Hello, world")'
    })

    console.log("Editor", editor1)
    editor1.getModel()!.onDidChangeContent(() => {
      test_draw()
    })

  })
})

function test_draw() {
  const acceptedList = ['fuck', 'shit']

  acceptedList.forEach((item) => {
    const matches = editor1
      .getModel()!
      .findMatches(item, false, false, true, null, false, undefined)
    matches.forEach((match) => {
      console.log(match.range)
      decorations.push(
        editor1.createDecorationsCollection([
          {
            range: match.range,
            options: {
              isWholeLine: false,
              inlineClassName: 'someClassName',
              stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
            }
          }
        ])
      )
      //console.log(decorations)
    })
  })
}

function deco_clear() {
  if (decorations) {
    decorations.forEach((element) => {
      element.clear()
    })
  }
}
</script>

<template>
  <v-layout>
    <v-navigation-drawer image="https://cdn.vuetifyjs.com/images/backgrounds/bg-2.jpg" theme="dark" permanent>
      <v-list nav>
        <v-list-item prepend-icon="mdi-email" title="Inbox" value="inbox"></v-list-item>
        <v-list-item prepend-icon="mdi-account-supervisor-circle" title="Supervisors" value="supervisors"></v-list-item>
        <v-list-item prepend-icon="mdi-clock-start" title="Clock-in" value="clockin"></v-list-item>
      </v-list>
    </v-navigation-drawer>
    <v-main>
      <div ref="editor_container" style="height: 90vh;"></div>
    </v-main>
  </v-layout>
</template>

<style>
.someClassName {
  background-color: red;
}
</style>
