'use client';
import React, { createContext, useCallback, useContext, useEffect, useLayoutEffect, useRef, useState } from 'react';
import type { Prov } from '@/lib/types';
import { STATUS_EXPLAIN, splitUrls } from '@/lib/concepts';

interface PopState {
  x: number;
  y: number;
  content: React.ReactNode;
  pinned: boolean;
}

interface Ctx {
  show: (e: { clientX: number; clientY: number }, content: React.ReactNode, pin?: boolean) => void;
  hide: () => void;
}

const PopCtx = createContext<Ctx>({ show: () => {}, hide: () => {} });
export const usePop = () => useContext(PopCtx);

export function ProvProvider({ children }: { children: React.ReactNode }) {
  const [st, setSt] = useState<PopState | null>(null);
  const ref = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState<{ left: number; top: number }>({ left: 0, top: 0 });

  const show = useCallback<Ctx['show']>((e, content, pin = false) => {
    setSt((prev) => {
      if (prev?.pinned && !pin) return prev;
      return { x: e.clientX, y: e.clientY, content, pinned: pin };
    });
  }, []);
  const hide = useCallback(() => setSt((prev) => (prev?.pinned ? prev : null)), []);

  useLayoutEffect(() => {
    if (!st || !ref.current) return;
    const r = ref.current.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    let left = st.x + 14;
    let top = st.y + 14;
    if (left + r.width > vw - 8) left = Math.max(8, st.x - r.width - 14);
    if (left + r.width > vw - 8) left = Math.max(8, vw - r.width - 8);
    if (top + r.height > vh - 8) top = Math.max(8, st.y - r.height - 14);
    setPos({ left, top });
  }, [st]);

  useEffect(() => {
    if (!st?.pinned) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setSt(null);
    const onDown = (e: PointerEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setSt(null);
    };
    const onScroll = () => setSt(null);
    window.addEventListener('keydown', onKey);
    const t = setTimeout(() => window.addEventListener('pointerdown', onDown), 0);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      clearTimeout(t);
      window.removeEventListener('keydown', onKey);
      window.removeEventListener('pointerdown', onDown);
      window.removeEventListener('scroll', onScroll);
    };
  }, [st?.pinned]);

  return (
    <PopCtx.Provider value={{ show, hide }}>
      {children}
      {st && (
        <div
          ref={ref}
          className={`pop${st.pinned ? ' pinned' : ''}`}
          role="dialog"
          aria-live="polite"
          style={{ left: pos.left, top: pos.top }}
        >
          {st.pinned && (
            <button className="pop-close" aria-label="Close" onClick={() => setSt(null)}>
              ×
            </button>
          )}
          {st.content}
          {!st.pinned && <div className="pop-hint">Click to pin and follow the source links</div>}
        </div>
      )}
    </PopCtx.Provider>
  );
}

export function ProvCard({ title, value, prov, extra }: { title?: string; value?: string; prov: Prov; extra?: React.ReactNode }) {
  const urls = splitUrls(prov.source_url);
  return (
    <div className="prov">
      {value && <div className="prov-value">{value}</div>}
      {title && <div className="prov-title">{title}</div>}
      {extra}
      <dl>
        <dt>Status</dt>
        <dd>
          <span className={`badge st-${prov.status.split(' ')[0]}`}>{prov.status}</span>
          {STATUS_EXPLAIN[prov.status] && <span className="muted"> — {STATUS_EXPLAIN[prov.status]}</span>}
        </dd>
        <dt>Confidence</dt>
        <dd>{prov.confidence_level}</dd>
        <dt>Source</dt>
        <dd>
          {prov.source}
          {urls.length > 0 && (
            <span className="links">
              {urls.map((u, i) => (
                <a key={u} href={u} target="_blank" rel="noopener noreferrer">
                  link{urls.length > 1 ? ` ${i + 1}` : ''}
                </a>
              ))}
            </span>
          )}
        </dd>
        <dt>Method</dt>
        <dd>{prov.methodology}</dd>
        {prov.note && (
          <>
            <dt>Note</dt>
            <dd>{prov.note}</dd>
          </>
        )}
      </dl>
    </div>
  );
}

/** Hover/focus props that open a provenance popover; click pins it. */
export function usePopHandlers(content: () => React.ReactNode, onActivate?: () => void) {
  const { show, hide } = usePop();
  return {
    onPointerMove: (e: React.PointerEvent) => e.pointerType === 'mouse' && show(e, content()),
    onPointerLeave: () => hide(),
    onFocus: (e: React.FocusEvent) => {
      const r = (e.target as Element).getBoundingClientRect();
      show({ clientX: r.left, clientY: r.bottom }, content());
    },
    onBlur: () => hide(),
    onClick: (e: React.MouseEvent) => {
      show(e.clientX || e.clientY ? e : { clientX: (e.target as Element).getBoundingClientRect().left, clientY: (e.target as Element).getBoundingClientRect().bottom }, content(), true);
      onActivate?.();
    },
  };
}

/** A displayed number that always carries its provenance. */
export function Num({ children, prov, title, className }: { children: React.ReactNode; prov: Prov; title?: string; className?: string }) {
  const h = usePopHandlers(() => <ProvCard title={title} value={typeof children === 'string' ? children : undefined} prov={prov} />);
  return (
    <button type="button" className={`num ${className || ''}`} {...h}>
      {children}
    </button>
  );
}
