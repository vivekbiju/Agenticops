// Location: frontend/app/components/StreamTerminal.tsx
'use client';

import React, { useEffect, useRef } from 'react';
import { EventLog } from '../hooks/useAgentStream';

export const StreamTerminal: React.FC<{ logs: EventLog[] }> = ({ logs }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-slate-950 rounded-xl border border-slate-800 p-4 font-mono text-xs shadow-inner">
      <div className="flex items-center gap-2 mb-3 border-b border-slate-800 pb-2 text-slate-400 font-sans font-semibold">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
        Agentic Workflow Processing Bus
      </div>
      <div ref={containerRef} className="h-44 overflow-y-auto space-y-2 pr-2 scrollbar-thin">
        {logs.length === 0 ? (
          <p className="text-slate-600 italic">Bus idle. Awaiting operational activation request...</p>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="text-slate-300 leading-relaxed border-l-2 border-slate-800 pl-2">
              {log.message && <span className="text-indigo-400">⚡ [{log.node.toUpperCase()}]</span>}
              {!log.message && <span className="text-emerald-400">✅ [{log.node.toUpperCase()}] Node Completed</span>}
              
              {log.message && <span className="text-slate-300 ml-1">{log.message}</span>}
              {log.metrics && (
                <div className="text-slate-500 ml-4 mt-0.5 text-[11px]">
                  ↳ Loop Index: {log.metrics.loop_count} | Forward Target: <span className="text-amber-500/80">{log.metrics.routing}</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};