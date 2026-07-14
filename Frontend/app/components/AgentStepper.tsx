// Location: frontend/app/components/AgentStepper.tsx
'use client';

import React from 'react';

// Explicitly matching potential agent states returned from your LangGraph run
export type AgentNode = 'IDLE' | 'CLASSIFIER' | 'RESEARCHER' | 'RISK_ANALYST' | 'AUDITOR' | 'COMPLETE';

interface AgentStepperProps {
  activeAgent: AgentNode;
}

export const AgentStepper: React.FC<AgentStepperProps> = ({ activeAgent }) => {
  const steps: { id: AgentNode; label: string; desc: string }[] = [
    { 
      id: 'CLASSIFIER', 
      label: 'Classifier Node', 
      desc: 'Extracting system parameters and isolating error structures.' 
    },
    { 
      id: 'RESEARCHER', 
      label: 'Researcher Node', 
      desc: 'Retrieving related historical runbooks from Elasticsearch index.' 
    },
    { 
      id: 'RISK_ANALYST', 
      label: 'Risk Analyst Node', 
      desc: 'Evaluating customer account parameters and projecting health metrics.' 
    },
    { 
      id: 'AUDITOR', 
      label: 'Auditor Node', 
      desc: 'Validating output recommendations to intercept potential hallucinations.' 
    },
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
      <h3 className="text-sm font-bold text-slate-300 mb-5 tracking-wider uppercase">
        Orchestration Pipeline Telemetry
      </h3>
      <div className="space-y-6 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-px before:bg-slate-800">
        {steps.map((step) => {
          // Calculate step completion state
          const isCompleted = 
            activeAgent === 'COMPLETE' || 
            (step.id === 'CLASSIFIER' && ['RESEARCHER', 'RISK_ANALYST', 'AUDITOR'].includes(activeAgent)) ||
            (step.id === 'RESEARCHER' && ['RISK_ANALYST', 'AUDITOR'].includes(activeAgent)) ||
            (step.id === 'RISK_ANALYST' && activeAgent === 'AUDITOR');
            
          const isActive = activeAgent === step.id;

          return (
            <div key={step.id} className="flex gap-4 relative items-start">
              {/* Status Circle indicator */}
              <div className={`w-8 h-8 rounded-full flex items-center justify-center border text-xs font-bold transition-all duration-300 z-10 ${
                isCompleted ? 'bg-emerald-500/10 border-emerald-500 text-emerald-400 shadow-sm shadow-emerald-500/10' :
                isActive ? 'bg-indigo-600 border-indigo-400 text-white animate-pulse shadow-md shadow-indigo-500/40' :
                'bg-slate-950 border-slate-800 text-slate-600'
              }`}>
                {isCompleted ? '✓' : '•'}
              </div>
              
              {/* Step label & detail text */}
              <div className="flex-1 min-w-0">
                <h4 className={`font-semibold text-xs transition-colors ${
                  isActive ? 'text-indigo-400' : isCompleted ? 'text-emerald-400' : 'text-slate-500'
                }`}>
                  {step.label}
                </h4>
                <p className="text-[11px] text-slate-400 mt-1 leading-normal">
                  {step.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};