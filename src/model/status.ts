import { realpathSync } from 'fs'
export class Status {
  cwd: string | null = null
  dataDir: string

  constructor() {
    this.dataDir = realpathSync('data')
  }
}
