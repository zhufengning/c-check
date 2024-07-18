<script setup lang="ts">
// @ts-nocheck
import { apiPost } from '../../../model/api'
import { computed, nextTick, onMounted, reactive, watch } from 'vue'
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const dialog = ref(false)
const dialogDelete = ref(false)
const headers = [
  {
    title: '函数名',
    align: 'start',
    sortable: false,
    key: 'fun_name'
  },
  { title: '风险级别', key: 'fun_level' },
  { title: '修改建议', key: 'fun_solution' },
  { title: 'Actions', key: 'actions', sortable: false }
]
const desserts = ref([])

const desserts_searched = ref([])
const editedIndex = ref(-1)
const editedItem = reactive({
  fun_name: 'gets',
  fun_level: '最危险',
  fun_solution: '使用 fgets（buf, size, stdin）这几乎总是一个大问题'
})
const defaultItem = {
  fun_name: 'gets',
  fun_level: '最危险',
  fun_solution: '使用 fgets（buf, size, stdin）这几乎总是一个大问题'
}

const formTitle = computed(() => (editedIndex.value === -1 ? 'New Item' : 'Edit Item'))

watch(dialog, (val) => {
  if (!val) close()
})

watch(dialogDelete, (val) => {
  if (!val) closeDelete()
})

onMounted(() => {
  initialize()
})

async function initialize() {
  const status = await window.api.getStatus()
  desserts.value = await (
    await apiPost('rules', { user: status.user, passwd: status.passwd })
  ).json()
}

function editItem(item: any) {
  editedIndex.value = desserts.value.indexOf(item)
  Object.assign(editedItem, item)
  dialog.value = true
}

async function deleteItem(item: any) {
  editedIndex.value = desserts.value.indexOf(item)
  Object.assign(editedItem, item)
  updateRules()
  dialogDelete.value = true
}

function deleteItemConfirm() {
  desserts.value.splice(editedIndex.value, 1)
  closeDelete()
}

function close() {
  dialog.value = false
  nextTick(async () => {
    Object.assign(editedItem, defaultItem)
    editedIndex.value = -1
    await updateRules()
  })
}

function closeDelete() {
  dialogDelete.value = false
  nextTick(async () => {
    Object.assign(editedItem, defaultItem)
    editedIndex.value = -1
    await updateRules()
  })
}

async function save() {
  if (editedIndex.value > -1) {
    Object.assign(desserts.value[editedIndex.value], editedItem)
  } else {
    desserts.value.push({ ...editedItem })
  }
  close()
}

async function updateRules() {
  const status = await window.api.getStatus()
  console.log(desserts.value)
  await apiPost('update_rules', { user: status.user, passwd: status.passwd, rules: desserts.value })
}

async function reset() {
  const status = await window.api.getStatus()
  await apiPost('init_rules', { user: status.user, passwd: status.passwd })
  initialize()
}

const search_dialog = ref(false)
async function search() {
  search_dialog.value = true
}

const search_text = ref('get[sc]')
function do_search() {
  const reg = new RegExp(search_text.value)
  desserts_searched.value = desserts.value.filter((item) => {
    return reg.test(item['fun_name']) || reg.test(item['fun_level']) || reg.test(item['fun_solution'])
  })
}
</script>
<template>
  <v-app>
    <v-container>
      <v-app-bar :elevation="3">
        <template #prepend>
          <v-app-bar-nav-icon icon="mdi-arrow-left" @click="() => router.back()"></v-app-bar-nav-icon>
        </template>

        <v-app-bar-title>风险函数规则库</v-app-bar-title>
      </v-app-bar>
      <v-main>
        <v-data-table :headers="headers" :items="desserts">
          <template #top>
            <v-toolbar flat>
              <v-toolbar-title>My CRUD</v-toolbar-title>
              <v-divider class="mx-4" inset vertical></v-divider>
              <v-spacer></v-spacer>
              <v-dialog v-model="dialog" max-width="500px">
                <template #activator="{ props }">
                  <v-btn class="mb-2" color="primary" dark v-bind="props"> New Item </v-btn>
                </template>
                <v-card>
                  <v-card-title>
                    <span class="text-h5">{{ formTitle }}</span>
                  </v-card-title>

                  <v-card-text>
                    <v-container>
                      <v-row>
                        <v-col cols="12" md="4" sm="6">
                          <v-text-field v-model="editedItem.fun_name" label="函数名"></v-text-field>
                        </v-col>
                        <v-col cols="12" md="4" sm="6">
                          <v-text-field v-model="editedItem.fun_level" label="风险等级"></v-text-field>
                        </v-col>
                      </v-row>
                      <v-row>
                        <v-col>
                          <v-textarea v-model="editedItem.fun_solution" label="修改建议"></v-textarea>
                        </v-col>
                      </v-row>
                    </v-container>
                  </v-card-text>

                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue-darken-1" variant="text" @click="close"> Cancel </v-btn>
                    <v-btn color="blue-darken-1" variant="text" @click="save"> Save </v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
              <v-dialog v-model="dialogDelete" max-width="500px">
                <v-card>
                  <v-card-title class="text-h5">Are you sure you want to delete this item?</v-card-title>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue-darken-1" variant="text" @click="closeDelete">Cancel</v-btn>
                    <v-btn color="blue-darken-1" variant="text" @click="deleteItemConfirm">OK</v-btn>
                    <v-spacer></v-spacer>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-toolbar>
          </template>
          <template #item.actions="{ item }">
            <v-icon class="me-2" size="small" @click="editItem(item)"> mdi-pencil </v-icon>
            <v-icon size="small" @click="deleteItem(item)"> mdi-delete </v-icon>
          </template>
          <template #no-data>
            <v-btn color="primary" @click="reset"> Reset </v-btn>
          </template>
        </v-data-table>
        <v-btn color="primary" @click="reset"> Reset </v-btn>
        <v-btn color="primary" @click="search"> 正则搜索 </v-btn>
        <v-dialog max-width="500" v-model="search_dialog">
          <v-card title="Dialog">
            <v-card-text>
              <v-text-field label="正则表达式" v-model="search_text"></v-text-field>
              <v-btn @click="do_search">搜索</v-btn>
              <v-data-table :headers="headers" :items="desserts_searched">

                <template #no-data>
                </template>
              </v-data-table>
            </v-card-text>

            <v-card-actions>
              <v-spacer></v-spacer>

              <v-btn text="Close Dialog" @click="search_dialog = false"></v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-main>
    </v-container>
  </v-app>
</template>
