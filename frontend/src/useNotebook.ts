import { useEffect, useRef, useState, useCallback } from 'react'
import type { CellInfo, ServerMessage } from './types'

export function useNotebook() {
  const [cells, setCells] = useState<CellInfo[]>([])
  const [edges, setEdges] = useState<[string, string][]>([])
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${location.host}/ws`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      ws.send(JSON.stringify({ type: 'get_state' }))
    }
    ws.onclose = () => setConnected(false)
    ws.onmessage = (event) => {
      const msg: ServerMessage = JSON.parse(event.data)
      switch (msg.type) {
        case 'state':
        case 'graph_changed':
          setCells(msg.cells)
          setEdges(msg.edges)
          break
        case 'cell_result':
          setCells((prev) =>
            prev.map((c) =>
              c.cell_id === msg.cell_id
                ? {
                    ...c,
                    status: msg.status,
                    output: msg.output,
                    stdout: msg.stdout,
                    exception: msg.exception,
                    exception_type: msg.exception_type,
                    components: msg.components,
                  }
                : c
            )
          )
          break
        case 'error':
          console.error('Server error:', msg.message)
          break
      }
    }

    return () => ws.close()
  }, [])

  const send = useCallback((msg: object) => {
    wsRef.current?.send(JSON.stringify(msg))
  }, [])

  return { cells, edges, connected, send }
}