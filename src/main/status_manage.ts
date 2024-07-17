import { dialog, ipcMain, shell } from 'electron'
import { Status } from '../model/status'
import { dirname } from 'path'
import { exec, spawn } from 'child_process'
import { realpath, realpathSync } from 'fs'

let status = new Status()

export function initHandlers(mainWindow) {
  ipcMain.handle('choose-folder', () => chooseFolder(mainWindow))
  ipcMain.handle('get-status', () => getStatus())
  ipcMain.handle('set-status', setStatus)
  ipcMain.handle('fullscreen', () => goFullscreen(mainWindow))
  ipcMain.handle('open-graph', async () => {
    const p = realpathSync('./py/server/graph.png')
    console.log(p)
    return await shell.openPath(p)
  })
  ipcMain.handle('open-report', async () => {
    const p = realpathSync('./py/reports/report.pdf')
    console.log(p)
    return await shell.openPath(p)
  })

  ipcMain.handle("shell", ()=>{
    exec(`start pwsh.exe -wd ${getStatus().cwd}`)
  })


  ipcMain.handle("clang", ()=>{
    exec(`start pwsh.exe -F clangd.ps1 ${getStatus().cwd}`)
  })
}

export function getStatus() {
  return status
}
export function setStatus(_e: Electron.IpcMainInvokeEvent, new_status: Status) {
  status = new_status
}

export function chooseFolder(mainWindow: Electron.BrowserWindow | null) {
  const res = dialog.showOpenDialogSync(mainWindow!, {
    properties: ['openFile']
  })
  if (res) status.cwd = dirname(res[0])
  return res ? res[0] : ''
}

function goFullscreen(mainWindow: Electron.BrowserWindow | null) {
  if (!mainWindow) return
  mainWindow.maximize()
}
