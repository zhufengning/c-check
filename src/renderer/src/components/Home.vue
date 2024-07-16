<script setup lang="ts">
import { onMounted, ref } from 'vue'
import * as monaco from 'monaco-editor'
import { useRouter } from 'vue-router'
import { nextTick } from 'vue'
import { TreeNode } from 'primevue/treenode'
import { apiGet, apiPost } from '../../../model/api'
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

let draw_poses: any[] = []
function test_draw() {
  decorations = []

  draw_poses.forEach((element) => {
    let line = editor1.getModel()!.getLineContent(element[0])

    //search for end of identifier ([a-zA-Z_])
    let start = element[1] - 1
    console.log(line, line[start])
    let end = start + line.slice(start).search(/[^a-zA-Z1-9_]/)
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
  draw_poses = []
  if (decorations) {
    decorations.forEach((element) => {
      element.clear()
    })
  }
}

function relative(from: string, to) {
  const sp = from.indexOf('/') == -1 ? '\\' : '/'
  const fromParts = from.split(sp).filter(Boolean)
  const toParts = to.split(sp).filter(Boolean)

  let commonIndex = 0
  while (
    commonIndex < fromParts.length &&
    commonIndex < toParts.length &&
    fromParts[commonIndex] === toParts[commonIndex]
  ) {
    commonIndex++
  }

  const upLevels = fromParts.length - commonIndex
  const upPath = new Array(upLevels).fill('..')
  const downPath = toParts.slice(commonIndex)

  return upPath.concat(downPath).join(sp)
}

const callee = ref({})
async function parseFile() {
  try {
    const res = await apiPost('scan/', { filename: await window.api.chooseFolder() })
    nodes.value = transformToTreeNodes(await res.json())
    console.log(nodes.value)
    const funres = await (await apiGet('functions/')).json()
    funres.forEach(async (x) => (x.file = relative((await window.api.getStatus()).cwd, x.file)))
    funcs.value = funres
    console.log(funres)
    const callee_res = await (await apiGet('callee/')).json()

    callee.value = callee_res
  } catch (e) {
    nodes.value = []
  }
}

const nodes = ref<TreeNode[]>([])
const selectedKey = ref<any>({})
const funcs = ref([])

async function openFile(node: TreeNode) {
  deco_clear()
  console.log('Selection:', node.key)
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
  const leak = await (await apiPost('mem/', ri)).json()
  global_vars.value = vars['global']
  local_vars.value = vars['local']
  leak_vars.value = leak
}

function switchSelection(v) {
  const nv = {}
  for (const i of v) {
    nv[i] = true
  }

  selectedKey.value = nv
  openFile({ key: v[0] })
}

const highlight = ref(false)
function switchHighlight() {
  if (!highlight.value) monaco.editor.setModelLanguage(editor1.getModel()!, 'c')
  else monaco.editor.setModelLanguage(editor1.getModel()!, 'plaintext')
  highlight.value = !highlight.value
}

const global_vars = ref([])
const local_vars = ref([])
const leak_vars = ref([])

async function globalVarClick(x) {
  const status: Status = await window.api.getStatus()

  const ri = { filepath: status.currentFile, cwd: status.cwd, var: x['name'], fun: '' }
  const res = await (await apiPost('var_pos', ri)).json()
  console.log(res)
  deco_clear()
  draw_poses = res
  test_draw()
}

async function localVarClick(x) {
  console.log(x)
  const status: Status = await window.api.getStatus()
  if (x['name']['id']) {
    x['name'] = x['name']['id']
  }

  const ri = { filepath: status.currentFile, cwd: status.cwd, var: x['name'], fun: x['fun'] }
  const res = await (await apiPost('var_pos', ri)).json()
  console.log(res)

  deco_clear()
  draw_poses = res
  test_draw()
}

async function funcClick(x) {
  switchSelection([x.file])
  deco_clear()
  draw_poses = [x.pos]
  test_draw()
}

async function findDef() {
  const s = editor1.getModel()?.getValueInRange(editor1.getSelection()!)

  const res = funcs.value.find((x) => x.name == s)
  console.log(res)
  funcClick(res)
}

function jumpTo(p) {
  console.log(p)
  switchSelection([p.file])
  deco_clear()
  draw_poses = [p.pos]
  test_draw()
}

const isActive = ref(false)
const target_callee = ref([])
async function findCall() {
  const s = editor1.getModel()?.getValueInRange(editor1.getSelection()!)

  const res = callee.value[s]

  res.forEach(async (x) => (x.file = relative((await window.api.getStatus()).cwd, x.file)))
  target_callee.value = res
  isActive.value = true
  console.log(res)
}
</script>

<template>
  <v-layout>
    <v-navigation-drawer permanent :width="300">
      <v-container>
        <v-row>
          <v-col class="d-flex flex-wrap ga-3">
            <v-btn prepend-icon="mdi-file" @click="parseFile">打开</v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-col class="d-flex flex-wrap ga-3">
            <v-btn prepend-icon="mdi-apple" @click="findDef">到函数定义</v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-col class="d-flex flex-wrap ga-3">
            <v-btn prepend-icon="mdi-google" @click="findCall">查找调用</v-btn>
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
        <v-chip class="ma-1" @click="switchHighlight">
          高亮：{{ highlight ? '全部' : '仅跟踪' }}
        </v-chip>
        <v-chip class="ma-1" @click="deco_clear"> 清除标记 </v-chip>
      </div>

      <div ref="editor_container" style="height: 90vh"></div>
    </v-main>
    <v-navigation-drawer
      permanent
      location="right"
      :width="300"
      style="
        ::-webkit-scrollbar {
          display: none;
        }
      "
    >
      <v-expansion-panels variant="accordion">
        <v-expansion-panel title="变量">
          <v-expansion-panel-text>
            <p>全局</p>
            <v-list lines="one">
              <v-list-item
                v-for="v in global_vars"
                :key="v"
                :title="v.repr"
                @click="() => globalVarClick(v)"
              >
              </v-list-item>
            </v-list>
            <p>局部</p>
            <v-list lines="one">
              <v-list-item
                v-for="v in local_vars"
                :key="v.name"
                :title="`${v.repr} (${v.fun})`"
                @click="() => localVarClick(v)"
              >
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel title="函数">
          <v-expansion-panel-text>
            <v-list lines="one">
              <v-list-item
                v-for="v in funcs"
                :key="v"
                :title="`${v.name}(${v.file})`"
                @click="() => funcClick(v)"
              >
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
        <v-expansion-panel title="检测警告">
          <v-expansion-panel-text>
            <v-list lines="three">
              <v-list-item
                v-for="item in local_vars.filter((x) => x['used'] == false)"
                :key="item['name']"
                :title="'当前文件' + item['pos'][0] + '行' + item['pos'][1] + '列'"
                @click="() => localVarClick(item)"
              >
                <v-list-item-subtitle
                  >{{ item['fun'] }}函数中变量{{ item['name'] }}未使用</v-list-item-subtitle
                >
              </v-list-item>
            </v-list>
            <v-list lines="three">
              <v-list-item
                v-for="item in global_vars.filter((x) => x['used'] == false)"
                :key="item['name']"
                :title="'当前文件' + item['pos'][0] + '行' + item['pos'][1] + '列'"
                @click="() => globalVarClick(item)"
              >
                <v-list-item-subtitle>全局变量{{ item['name'] }}未使用</v-list-item-subtitle>
              </v-list-item>
            </v-list>

            <v-list lines="three">
              <v-list-item
                v-for="v in funcs"
                :key="v"
                :title="'任何文件中均未使用函数'"
                :subtitle="`${v.name} 定义于${v.file}`"
                @click="() => funcClick(v)"
              >
              </v-list-item>
            </v-list>

            <v-list lines="three">
              <v-list-item
                v-for="item in leak_vars"
                :key="item['name']"
                :title="'定义于' + item['pos'][0] + '行' + item['pos'][1] + '列的指针'"
                @click="() => localVarClick(item)"
              >
                <v-list-item-subtitle
                  >{{ item['fun'] }}函数中指针{{ item['name'] }}分配后未释放</v-list-item-subtitle
                >
              </v-list-item>
            </v-list>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-navigation-drawer>
  </v-layout>

  <v-dialog v-model="isActive" max-width="400">
    <v-card title="提示">
      <v-card-text>
        <v-list>
          <v-list-item
            v-for="item in target_callee"
            :key="item"
            @click="
              () => {
                jumpTo(item)
                isActive = false
              }
            "
          >
            <v-list-item-title>{{ item.pos }} {{ item.file }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn text="关闭" @click="isActive = false"></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<style>
.someClassName {
  background-color: red;
}
</style>
