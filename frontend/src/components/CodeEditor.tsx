import { useEffect, useRef } from 'react'
import { EditorState } from '@codemirror/state'
import { EditorView, keymap, lineNumbers } from '@codemirror/view'
import { python } from '@codemirror/lang-python'
import { defaultKeymap, historyKeymap } from '@codemirror/commands'

interface Props {
  value: string
  onChange: (value: string) => void
  onRun?: () => void
}

export function CodeEditor({ value, onChange, onRun }: Props) {
  const hostRef = useRef<HTMLDivElement>(null)
  const viewRef = useRef<EditorView | null>(null)
  const onChangeRef = useRef(onChange)
  const onRunRef = useRef(onRun)

  onChangeRef.current = onChange
  onRunRef.current = onRun

  useEffect(() => {
    if (!hostRef.current) return

    const view = new EditorView({
      state: EditorState.create({
        doc: value,
        extensions: [
          lineNumbers(),
          python(),
          keymap.of([...historyKeymap, ...defaultKeymap]),
          keymap.of([
            {
              key: 'Shift-Enter',
              run: () => {
                onRunRef.current?.()
                return true
              },
            },
          ]),
          EditorView.lineWrapping,
          EditorView.updateListener.of((update) => {
            if (update.docChanged) {
              onChangeRef.current(update.state.doc.toString())
            }
          }),
          EditorView.theme({
            '&': { fontSize: '14px', backgroundColor: 'transparent' },
            '.cm-content': { fontFamily: "'Consolas', 'Monaco', monospace" },
            '.cm-gutters': {
              backgroundColor: 'transparent',
              border: 'none',
              color: '#666',
            },
            '&.cm-focused': { outline: 'none' },
          }),
        ],
      }),
      parent: hostRef.current,
    })
    viewRef.current = view

    return () => view.destroy()
  }, [])

  useEffect(() => {
    const view = viewRef.current
    if (view && view.state.doc.toString() !== value) {
      view.dispatch({
        changes: { from: 0, to: view.state.doc.length, insert: value },
      })
    }
  }, [value])

  return <div ref={hostRef} className="code-editor" />
}