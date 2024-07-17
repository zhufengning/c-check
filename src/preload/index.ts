import { contextBridge } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// Custom APIs for renderer
const api = {
  chooseFolder: () => electronAPI.ipcRenderer.invoke('choose-folder'),
  getStatus: () => electronAPI.ipcRenderer.invoke('get-status'),
  setStatus: (status: string) => electronAPI.ipcRenderer.invoke('set-status', status),
  goFullscreen: () => electronAPI.ipcRenderer.invoke('fullscreen'),
  openGraph: () => electronAPI.ipcRenderer.invoke('open-graph'),
  openReport: () => electronAPI.ipcRenderer.invoke('open-report'),
  shell: () => electronAPI.ipcRenderer.invoke('shell'),
  clang: () => electronAPI.ipcRenderer.invoke('clang')
}

// Use `contextBridge` APIs to expose Electron APIs to
// renderer only if context isolation is enabled, otherwise
// just add to the DOM global.
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', electronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = electronAPI
  // @ts-ignore (define in dts)
  window.api = api
}
