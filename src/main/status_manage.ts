import { dialog, ipcMain } from 'electron'
import { Status } from '../model/status'
import { dirname } from 'path'

const status = new Status()

export function initHandlers(mainWindow) {
  ipcMain.handle('choose-folder', () => chooseFolder(mainWindow))
  ipcMain.handle('get-status', () => getStatus())
  ipcMain.handle('fullscreen', () => goFullscreen(mainWindow))
}

export function getStatus() {
  return status
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
