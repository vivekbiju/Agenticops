// Location: frontend/app/components/SidebarDrawer.tsx
'use client';

import React from 'react';
import { SourceFragment } from '../hooks/useAgentStream';

interface SidebarDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  fragment: SourceFragment | null;
  index: number;
}

export const SidebarDrawer: React.FC<SidebarDrawerProps> = ({ isOpen, onClose, fragment, index }) => {
  return (
    <>
      {/* Backdrop overlay */}
      <div
        className={`fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300 ${
          isOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        }`}
        onClick={onClose}
      />
      
      {/* Sliding Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-[450px] bg-slate-900 border-l border-slate-800 z-50 shadow-2xl transform transition-transform duration-300 ease-out p-6 overflow-y-auto ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
          <h3 className="text-lg font-bold text-white flex items-center gap-2">
            <span className="p-1 rounded bg-indigo-500/10 text-indigo-400 text-sm">Doc-{index + 1}</span>
            Retrieved Log Snippet
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white transition-colors text-sm font-medium">
            ✕ Close
          </button>
        </div>

        {fragment ? (
          <div className="space-y-4">
            <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed">
              {fragment.content || fragment.text || "No readable string context matched."}
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 text-slate-400">
              <div><span className="text-slate-500">Account Ref:</span> {fragment.account_id || 'N/A'}</div>
              <div><span className="text-slate-500">Fragment ID:</span> {fragment.chunk_id ?? 'N/A'}</div>
            </div>
          </div>
        ) : (
          <p className="text-sm text-slate-400 italic">No historical text matched inside this index registry allocation.</p>
        )}
      </div>
    </>
  );
};