import { ElectronAPI } from '@electron-toolkit/preload'

declare global {
  interface Window {
    electron: ElectronAPI
    api: {
      chooseFolder: () => Promise<string>
      goFullscreen: () => Promise<void>
      getStatus: () => Promise<Status>
      setStatus: (string) => Promise<void>
    }
  }
}
