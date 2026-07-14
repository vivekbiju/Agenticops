'use client';

import React from 'react';
import { RiskAnalysis } from '../hooks/useAgentStream';

export const HealthMetrics: React.FC<{ data: RiskAnalysis | null }> = ({ data }) => {
  if (!data) {
    return (
      <div className="p-6 rounded-xl border border-dashed border-slate-800 flex flex-col items-center justify-center min-h-[220px] text-slate-500">
        <div className="w-10 h-10 rounded-full border-2 border-dashed border-slate-700 animate-spin mb-3" />
        <span className="text-xs font-mono">Awaiting Risk Analyst Telemetry...</span>
      </div>
    );
  }

  const score = data.health_score;

  // Determine thresholds, CSS statuses, and custom text labels
  let strokeColor = "stroke-emerald-500 text-emerald-500";
  let bgClass = "border-emerald-500/20 bg-emerald-500/5 text-emerald-400";
  let textStatus = "SAFE REGIME";

  if (score < 50) {
    strokeColor = "stroke-rose-500 text-rose-500 animate-pulse";
    bgClass = "border-rose-500/25 bg-rose-500/10 text-rose-400";
    textStatus = "CRITICAL ALERT";
  } else if (score >= 50 && score < 80) {
    strokeColor = "stroke-amber-500 text-amber-500";
    bgClass = "border-amber-500/20 bg-amber-500/5 text-amber-400";
    textStatus = "WARNING STATUS";
  }

  // SVG Circular Gauge Calculations
  const radius = 50;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className={`p-6 rounded-xl border ${bgClass} transition-all duration-500 shadow-lg`}>
      {/* Header telemetry metrics */}
      <div className="flex justify-between items-center mb-4">
        <h4 className="text-xs font-bold tracking-wider uppercase opacity-80">Account Risk Blueprint</h4>
        <div className="flex gap-2">
          {data.churn_flag && (
            <span className="px-2.5 py-0.5 rounded text-[10px] font-black uppercase bg-rose-600 text-white animate-pulse">
              High Churn Risk
            </span>
          )}
          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold uppercase border ${
            score < 50 ? 'bg-rose-500/20 border-rose-500/30' :
            score < 80 ? 'bg-amber-500/20 border-amber-500/30' :
            'bg-emerald-500/20 border-emerald-500/30'
          }`}>
            {textStatus}
          </span>
        </div>
      </div>

      <div className="flex flex-col md:flex-row items-center gap-6 mb-6">
        {/* Dynamic SVG Radial Score Meter */}
        <div className="relative flex items-center justify-center flex-shrink-0">
          <svg className="w-28 h-28 transform -rotate-90">
            {/* Background track */}
            <circle 
              cx="56" 
              cy="56" 
              r={radius} 
              className="stroke-slate-800/60" 
              strokeWidth="8" 
              fill="transparent" 
            />
            {/* Dynamic visual metric line */}
            <circle 
              cx="56" 
              cy="56" 
              r={radius} 
              className={`transition-all duration-1000 ease-out ${strokeColor}`} 
              strokeWidth="8" 
              fill="transparent"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>
          <div className="absolute text-center">
            <span className="text-2xl font-black text-white block leading-none">{score}</span>
            <span className="text-[8px] font-mono tracking-wider uppercase text-slate-400 mt-1 block">Rating</span>
          </div>
        </div>

        {/* Live numerical outputs */}
        <div className="flex-1 text-center md:text-left">
          <div className="text-3xl font-extrabold tracking-tight text-white mb-1">
            {score} <span className="text-sm font-normal text-slate-400">/ 100</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Calculated health rating representing current system performance mapped against active contracts.
          </p>
        </div>
      </div>

      {/* Active risk factors list */}
      {data.risk_factors && data.risk_factors.length > 0 && (
        <div className="border-t border-slate-800/50 pt-4">
          <span className="text-xs font-semibold block mb-2 opacity-70">Active Risk Projections:</span>
          <ul className="list-disc list-inside text-xs space-y-1.5 opacity-90">
            {data.risk_factors.map((factor, idx) => (
              <li key={idx} className="truncate text-slate-300 hover:text-white transition-colors">
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};