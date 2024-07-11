<script setup lang="ts">
import { onMounted, ref } from 'vue'
import * as monaco from 'monaco-editor'
import { useRouter } from 'vue-router'
import { nextTick } from 'vue'
import { TreeNode } from 'primevue/treenode'
import { apiPost } from '../../../model/api'
//const ipcHandle = () => window.electron.ipcRenderer.send('ping')

let editor1: monaco.editor.IStandaloneCodeEditor
const editor_container = ref<HTMLElement | null>(null)
const decorations: monaco.editor.IEditorDecorationsCollection[] = []
const router = useRouter()
onMounted(async () => {
  await router.isReady()
  await nextTick()
  setTimeout(() => {
    editor1 = monaco.editor.create(editor_container.value!, {
      readOnly: true,
      language: 'plaintext',
      automaticLayout: true
    })

    //console.log('Editor', editor1)
    editor1.getModel()!.onDidChangeContent(() => {
      test_draw()
    })
  }, 100)
})

const folderIcon = 'mdi mdi-chevron-right mdi-folder' // 文件夹的图标
const fileIcon = 'mdi mdi-chevron-down mdi-file' // 文件的图标

function transformToTreeNodes(obj: any, path: string = ''): TreeNode[] {
  //console.log(obj)
  const result: TreeNode[] = []

  Object.entries(obj).forEach(([key, value]) => {
    const newPath = path ? `${path}/${key}` : key
    const node: TreeNode = {
      key: newPath,
      label: key,
      icon: value === null ? fileIcon : folderIcon
    }

    if (value !== null && typeof value === 'object') {
      node.children = transformToTreeNodes(value, newPath)
    }

    result.push(node)
  })

  return result.toSorted((a, b) => {
    console.log('sort', a, b)
    if (a.children && !b.children) {
      return -1
    }
    if (!a.children && b.children) {
      return 1
    }
    return a.label!.localeCompare(b.label!)
  })
}

async function chooseFolder() {
  console.log(await window.api.chooseFolder())
}

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

// function deco_clear() {
//   if (decorations) {
//     decorations.forEach((element) => {
//       element.clear()
//     })
//   }
// }

async function parseFile() {
  try {
    const res = await apiPost('scan/', { filename: await window.api.chooseFolder() })
    nodes.value = transformToTreeNodes(await res.json())
    console.log(nodes.value)
  } catch (e) {
    nodes.value = []
  }
}

const nodes = ref<TreeNode[]>([])
const selectedKey = ref<string[]>([])

async function openFile(node: TreeNode) {
  console.log(node.key)

  const cwd = (await window.api.getStatus()).cwd
  const res = await apiPost('parse/', { filepath: node.key, cwd: cwd })
  const content = await res.json()
  editor1.setValue(content)
}

const highlight = ref(false)
function switchHighlight() {
  if (!highlight.value) monaco.editor.setModelLanguage(editor1.getModel()!, 'c')
  else monaco.editor.setModelLanguage(editor1.getModel()!, 'plaintext')
  highlight.value = !highlight.value
}
</script>

<template>
  <v-layout>
    <v-navigation-drawer permanent :width="300">
      <v-container>
        <v-row>
          <v-col class="d-flex flex-wrap ga-3">
            <v-btn prepend-icon="mdi-file" @click="parseFile">打开</v-btn>
            <v-btn prepend-icon="mdi-apple" @click="chooseFolder">111</v-btn>
            <v-btn prepend-icon="mdi-google" @click="chooseFolder">111</v-btn>
          </v-col>
        </v-row>
        <v-row v-if="nodes.length == 0">
          <v-col class="d-flex flex-wrap ga-3">
            <p>文件未选择</p>
          </v-col>
        </v-row>
      </v-container>

      <tree
        v-if="nodes.length > 0"
        v-model:selectionKeys="selectedKey"
        :value="nodes"
        :filter="true"
        filter-mode="lenient"
        selection-mode="single"
        @node-select="openFile"
      >
      </tree>
    </v-navigation-drawer>
    <v-main>
      <v-row class="mx-2 my-1">
        <v-col
          ><v-chip @click="switchHighlight">
            高亮：{{ highlight ? '全部' : '仅跟踪' }}
          </v-chip></v-col
        >
      </v-row>

      <div ref="editor_container" style="height: 90vh"></div>
    </v-main>
    <v-navigation-drawer permanent location="right" :width="200">
      <v-expansion-panels variant="accordion">
        <v-expansion-panel title="变量">
          <v-expansion-panel-text>
            111<br />
            222
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel title="函数">
          <v-expansion-panel-text>
            111<br />
            222
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-navigation-drawer>
  </v-layout>
</template>

<style>
.someClassName {
  background-color: red;
}
</style>
