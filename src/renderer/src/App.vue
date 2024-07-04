<script setup lang="ts">
import { onMounted } from 'vue'
import * as monaco from 'monaco-editor'
//const ipcHandle = () => window.electron.ipcRenderer.send('ping')
let editor1: monaco.editor.IStandaloneCodeEditor
const decorations: monaco.editor.IEditorDecorationsCollection[] = []
onMounted(() => {
  const container = document.getElementById('container')
  editor1 = monaco.editor.create(container!, {
    value: 'console.log("Hello, world")'
  })

  editor1.getModel()!.onDidChangeContent(() => {
    test_draw()
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
  <div id="container" style="width: 800px; height: 600px"></div>
  <button @click="test_draw">Test</button>
  <button @click="deco_clear">Clear</button>
</template>

<style>
.someClassName {
  background-color: red;
}
</style>
