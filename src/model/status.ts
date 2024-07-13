import { realpathSync } from 'fs'
export class Status {
  cwd: string | null = null
  dataDir: string
  currentFile: string | null = null
  user: string = ''
  passwd: string = ''

  constructor() {
    this.dataDir = realpathSync('data')
  }
}
