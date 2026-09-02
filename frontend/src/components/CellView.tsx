import type { CellInfo, UIComponentInfo } from '../types'
import { CodeEditor } from './CodeEditor'

interface Props {
  cell: CellInfo
  onRun: (cellId: string) => void
  onUpdate: (cellId: string, code: string) => void
  onRemove: (cellId: string) => void
  onUIEvent: (componentId: string, value: unknown) => void
}

const STATUS_ICON: Record<string, string> = {
  idle: '·',
  pending: '…',
  running: '→',
  done: '✓',
  error: '✗',
  stale: '○',
}

function UIComponentView({
  component,
  onEvent,
}: {
  component: UIComponentInfo
  onEvent: (id: string, value: unknown) => void
}) {
  if (!component.id) return null

  switch (component.type) {
    case 'slider':
      return (
        <div className="ui-component">
          <input
            type="range"
            min={component.props.min as number}
            max={component.props.max as number}
            step={component.props.step as number}
            value={component.value as number}
            onChange={(e) => onEvent(component.id!, Number(e.target.value))}
          />
          <span className="ui-value">{String(component.value)}</span>
        </div>
      )
    case 'button':
      return (
        <div className="ui-component">
          <button
            className="ui-button"
            onClick={() =>
              onEvent(component.id!, (component.value as number) + 1)
            }
          >
            {component.props.label as string}
          </button>
          <span className="ui-value">clicks: {String(component.value)}</span>
        </div>
      )
    case 'checkbox':
      return (
        <div className="ui-component">
          <label className="ui-checkbox">
            <input
              type="checkbox"
              checked={component.value as boolean}
              onChange={(e) => onEvent(component.id!, e.target.checked)}
            />
            {component.props.label as string}
          </label>
        </div>
      )
    default:
      return null
  }
}

export function CellView({ cell, onRun, onUpdate, onRemove, onUIEvent }: Props) {
  const outputIsUI =
    cell.output !== null &&
    typeof cell.output === 'object' &&
    (cell.output as Record<string, unknown>)?._ui === true

  return (
    <div className={`cell cell-${cell.status}`}>
      <div className="cell-header">
        <span className="cell-status">{STATUS_ICON[cell.status]}</span>
        <span className="cell-id">{cell.cell_id}</span>
        {cell.defs.length > 0 && (
          <span className="cell-tag tag-def">
            defs: {cell.defs.join(', ')}
          </span>
        )}
        {cell.refs.length > 0 && (
          <span className="cell-tag tag-ref">
            refs: {cell.refs.join(', ')}
          </span>
        )}
        <div className="cell-actions">
          <button className="btn-run" onClick={() => onRun(cell.cell_id)}>
            Run
          </button>
          <button
            className="btn-remove"
            onClick={() => onRemove(cell.cell_id)}
          >
            ×
          </button>
        </div>
      </div>
      <CodeEditor
        value={cell.code}
        onChange={(code) => onUpdate(cell.cell_id, code)}
        onRun={() => onRun(cell.cell_id)}
      />
      {cell.components.length > 0 && (
        <div className="cell-components">
          {cell.components.map((comp) => (
            <UIComponentView
              key={comp.id}
              component={comp}
              onEvent={onUIEvent}
            />
          ))}
        </div>
      )}
      {(cell.stdout || cell.output !== null || cell.exception) && (
        <div className="cell-output">
          {cell.stdout && <pre className="output-stdout">{cell.stdout}</pre>}
          {cell.output !== null && !outputIsUI && (
            <pre className="output-value">
              {typeof cell.output === 'string'
                ? cell.output
                : JSON.stringify(cell.output, null, 2)}
            </pre>
          )}
          {outputIsUI && (
            <UIComponentView
              component={cell.output as UIComponentInfo}
              onEvent={onUIEvent}
            />
          )}
          {cell.exception && (
            <pre className="output-error">
              {cell.exception_type}: {cell.exception}
            </pre>
          )}
        </div>
      )}
    </div>
  )
}
