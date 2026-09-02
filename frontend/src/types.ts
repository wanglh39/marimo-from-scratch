export type CellStatus = 'idle' | 'pending' | 'running' | 'done' | 'error' | 'stale'

export interface UIComponentInfo {
  _ui: boolean
  id: string | null
  type: string
  value: unknown
  props: Record<string, unknown>
  var_name?: string
}

export interface CellInfo {
  cell_id: string
  code: string
  defs: string[]
  refs: string[]
  status: CellStatus
  output: unknown
  stdout: string
  exception: string | null
  exception_type: string | null
  components: UIComponentInfo[]
}

export interface StateMessage {
  type: 'state'
  cells: CellInfo[]
  edges: [string, string][]
}

export interface CellResultMessage {
  type: 'cell_result'
  cell_id: string
  status: CellStatus
  output: unknown
  stdout: string
  exception: string | null
  exception_type: string | null
  components: UIComponentInfo[]
}

export interface GraphChangedMessage {
  type: 'graph_changed'
  cells: CellInfo[]
  edges: [string, string][]
}

export interface ErrorMessage {
  type: 'error'
  message: string
}

export type ServerMessage =
  | StateMessage
  | CellResultMessage
  | GraphChangedMessage
  | ErrorMessage
