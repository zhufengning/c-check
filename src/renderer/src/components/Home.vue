<script setup lang="ts">
import { onMounted, ref } from 'vue'
import * as monaco from 'monaco-editor'
import { useRouter } from 'vue-router'
import { nextTick } from 'vue'
import { TreeNode } from 'primevue/treenode'
import { apiPost } from '../../../model/api'
import { Status } from '@model/status'
//const ipcHandle = () => window.electron.ipcRenderer.send('ping')

let editor1: monaco.editor.IStandaloneCodeEditor
const editor_container = ref<HTMLElement | null>(null)
let decorations: monaco.editor.IEditorDecorationsCollection[] = []
const router = useRouter()
window.api.goFullscreen().then()
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

let draw_poses = []
function test_draw() {
  decorations = []

  draw_poses.forEach((element) => {
    let line = editor1.getModel()!.getLineContent(element[0])

    //search for end of identifier ([a-zA-Z_])
    let start = element[1] - 1
    console.log(line, line[start])
    let end = start + line.slice(start).search(/[^a-zA-Z_]/)
    console.log(end)
    decorations.push(
      editor1.createDecorationsCollection([
        {
          range: {
            startLineNumber: element[0],
            startColumn: start + 1,
            endLineNumber: element[0],
            endColumn: end + 1
          },
          options: {
            isWholeLine: false,
            inlineClassName: 'someClassName',
            stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
          }
        }
      ])
    )
  })
}

function deco_clear() {
  if (decorations) {
    decorations.forEach((element) => {
      element.clear()
    })
  }
}

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
  const status: Status = await window.api.getStatus()
  const cwd = status.cwd
  const ri = { filepath: node.key, cwd: cwd }
  status.currentFile = node.key!
  await window.api.setStatus(status)
  const res = await apiPost('parse/', ri)
  const content = await res.json()
  editor1.setValue(content)
  const vars = await (await apiPost('vars/', ri)).json()
  console.log(vars)
  global_vars.value = vars['global']
  local_vars.value = vars['local']
}

const highlight = ref(false)
function switchHighlight() {
  if (!highlight.value) monaco.editor.setModelLanguage(editor1.getModel()!, 'c')
  else monaco.editor.setModelLanguage(editor1.getModel()!, 'plaintext')
  highlight.value = !highlight.value
}

const global_vars = ref([])
const local_vars = ref([])

async function globalVarClick(x) {
  const status: Status = await window.api.getStatus()

  const ri = { filepath: status.currentFile, cwd: status.cwd, var: x['name'], fun: '' }
  const res = await (await apiPost('var_pos', ri)).json()
  draw_poses = res
  console.log(res)
  deco_clear()
  test_draw()
}

async function localVarClick(x) {
  const status: Status = await window.api.getStatus()

  const ri = { filepath: status.currentFile, cwd: status.cwd, var: x['name'], fun: x['fun'] }
  const res = await (await apiPost('var_pos', ri)).json()
  draw_poses = res
  console.log(res)

  deco_clear()
  test_draw()
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
      <div class="d-flex flex-row">
        <v-chip class="ma-1" @click="switchHighlight"> 高亮：{{ highlight ? '全部' : '仅跟踪' }} </v-chip>
        <v-chip class="ma-1" @click="deco_clear"> 清除标记 </v-chip>
      </div>

      <div ref="editor_container" style="height: 90vh"></div>
    </v-main>
    <v-navigation-drawer permanent location="right" :width="200">
      <v-expansion-panels variant="accordion">
        <v-expansion-panel title="变量">
          <v-expansion-panel-text>
            <p>全局</p>
            <v-list lines="one">
              <v-list-item
                v-for="v in global_vars"
                :key="v"
                :title="v.name"
                @click="() => globalVarClick(v)"
              >
              </v-list-item>
            </v-list>
            <p>局部</p>
            <v-list lines="one">
              <v-list-item
                v-for="v in local_vars"
                :key="v.name"
                :title="`${v.name} (${v.fun})`"
                @click="() => localVarClick(v)"
              >
              </v-list-item>
            </v-list>
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
