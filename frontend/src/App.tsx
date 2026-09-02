import { useNotebook } from './useNotebook'
import { CellView } from './components/CellView'

export default function App() {
  const { cells, edges, connected, send } = useNotebook()

  const handleRun = (cellId: string) =>
    send({ type: 'run_cell', cell_id: cellId })
  const handleUpdate = (cellId: string, code: string) =>
    send({ type: 'update_cell', cell_id: cellId, code })
  const handleRemove = (cellId: string) =>
    send({ type: 'remove_cell', cell_id: cellId })
  const handleAdd = () => send({ type: 'add_cell', code: '' })
  const handleRunAll = () => send({ type: 'run_all' })
  const handleUIEvent = (componentId: string, value: unknown) =>
    send({ type: 'ui_event', component_id: componentId, value })

  return (
    <div className="app">
      <header className="app-header">
        <h1>marimo-from-scratch</h1>
        <span
          className={`connection ${connected ? 'connected' : 'disconnected'}`}
        >
          {connected ? '● connected' : '○ disconnected'}
        </span>
        <div className="header-actions">
          <button className="btn-primary" onClick={handleRunAll}>
            Run All
          </button>
          <button className="btn-primary" onClick={handleAdd}>
            + Add Cell
          </button>
        </div>
      </header>
      <div className="notebook">
        {cells.map((cell) => (
          <CellView
            key={cell.cell_id}
            cell={cell}
            onRun={handleRun}
            onUpdate={handleUpdate}
            onRemove={handleRemove}
            onUIEvent={handleUIEvent}
          />
        ))}
        {cells.length === 0 && (
          <div className="empty-state">
            <p>No cells yet.</p>
            <p>Click "+ Add Cell" to start coding.</p>
          </div>
        )}
      </div>
      {edges.length > 0 && (
        <footer className="graph-info">
          {edges.length} dependency edge{edges.length !== 1 ? 's' : ''}
        </footer>
      )}
    </div>
  )
}