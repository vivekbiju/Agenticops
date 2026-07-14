// Location: frontend/app/hooks/useAgentStream.ts
'use client';

import { useState, useCallback } from 'react';

export interface EventLog {
  node: string;
  message?: string;
  metrics?: { loop_count: number; routing?: string };
}

export interface RiskAnalysis {
  health_score: number;
  churn_flag: boolean;
  risk_factors: string[];
}

export interface SourceFragment {
  content?: string;
  text?: string;
  account_id?: string;
  chunk_id?: number;
}

export function useAgentStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamText, setStreamText] = useState('');
  const [logs, setLogs] = useState<EventLog[]>([]);
  const [riskAnalysis, setRiskAnalysis] = useState<RiskAnalysis | null>(null);
  const [sources, setSources] = useState<SourceFragment[]>([]);
  const [error, setError] = useState<string | null>(null);

  const startStream = useCallback(async (accountId: string, issueInput: string) => {
    setIsStreaming(true);
    setStreamText('');
    setLogs([]);
    setRiskAnalysis(null);
    setSources([]);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/agent/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account_id: accountId, raw_issue_input: issueInput }),
      });

      if (!response.ok) throw new Error(`HTTP Error ${response.status}`);
      if (!response.body) throw new Error('ReadableStream not supported.');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep trailing partial line

        for (const line of lines) {
          const cleanedLine = line.trim();
          if (!cleanedLine.startsWith('data: ')) continue;

          try {
            const rawJson = cleanedLine.replace(/^data:\s*/, '');
            const parsed = JSON.parse(rawJson);

            switch (parsed.event) {
              case 'workflow_start':
                setLogs((prev) => [...prev, { node: parsed.node, message: parsed.message }]);
                break;
              case 'token':
                if (parsed.text) setStreamText((prev) => prev + parsed.text);
                break;
              case 'node_complete':
                setLogs((prev) => [...prev, { node: parsed.node, metrics: parsed.metrics }]);
                if (parsed.sources) setSources(parsed.sources);
                if (parsed.risk_analysis) setRiskAnalysis(parsed.risk_analysis);
                break;
              case 'workflow_end':
                setIsStreaming(false);
                break;
              case 'system_exception':
                setError(parsed.message);
                setIsStreaming(false);
                break;
            }
          } catch (e) {
            console.error('Failed parsing SSE payload chunk:', e);
          }
        }
      }
    } catch (err: any) {
      setError(err?.message || 'Unknown network error occurred.');
      setIsStreaming(false);
    }
  }, []);

  return { isStreaming, streamText, logs, riskAnalysis, sources, error, startStream };
}