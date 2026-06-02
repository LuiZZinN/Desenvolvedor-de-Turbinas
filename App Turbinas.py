import React, { useState } from 'react';
import { HydroInputs, HydroOutputs, VelocityTriangle } from '../types';

interface Props {
  inputs: HydroInputs;
  outputs: HydroOutputs;
}

export function Dashboard({ inputs, outputs }: Props) {
  const { N, P_MW, Ns, turbineType, D1_est, Heuler, eulerPowerkW, hydraulicEfficiency, inlet, outlet } = outputs;
  const [simTorque, setSimTorque] = useState<number | ''>('');
  const [simHead, setSimHead] = useState<number | ''>('');

  // CFD Validation Math
  let powerSimkW = 0, effGlobal = 0, effEuler = 0, effTargetGlobal = 0, effTargetEuler = 0;
  const hasCFD = typeof simTorque === 'number' && simTorque > 0;
  
  if (hasCFD) {
    const powerSimW = simTorque * outputs.omega;
    powerSimkW = powerSimW / 1000;
    effTargetGlobal = (simTorque / outputs.torque) * 100;
    effTargetEuler = (simTorque / outputs.eulerTorque) * 100;
    
    if (typeof simHead === 'number' && simHead > 0) {
      const hydraulicPowerCFD = outputs.massFlow * 9.81 * simHead;
      effGlobal = (powerSimW / hydraulicPowerCFD) * 100;
      effEuler = (powerSimW / (outputs.massFlow * 9.81 * Heuler)) * 100;
    }
  }

  const cfdScript = `// ANSYS / CFX BOUNDARY CONDITIONS
Rotational_Speed_rads = ${outputs.omega.toFixed(4)} [rad/s]
Rotational_Speed_RPM  = ${outputs.N.toFixed(2)} [rpm]
Mass_Flow_Rate        = ${outputs.massFlow.toFixed(2)} [kg/s]

// GEOMETRIA E ANGULOS
Diameter_Outer_D1     = ${outputs.D1_est.toFixed(3)} [m]
Diameter_Inner_D2     = ${outputs.D2_est.toFixed(3)} [m]
Angle_Beta_1          = ${inlet ? inlet.beta.toFixed(2) : 'N/A'} [deg]
Angle_Beta_2          = ${outlet ? outlet.beta.toFixed(2) : 'N/A'} [deg]

// ALVOS TEÓRICOS DE TORQUE
Target_Torque_Global  = ${outputs.torque.toFixed(2)} [N·m]
Target_Torque_Euler   = ${outputs.eulerTorque.toFixed(2)} [N·m]
`;

  return (
    <div className="space-y-6 pb-20">
      
      {/* 1. SELEÇÃO E RESULTADOS GLOBAIS */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-extrabold text-slate-800">1. Dimensionamento Global e Seleção</h2>
            <p className="text-xs text-slate-500 font-medium mt-1">Estimativa macroscópica com base no balanço de energia (Eficiência Estipulada).</p>
          </div>
          <span className={`px-5 py-2 rounded-lg text-sm font-bold tracking-widest uppercase flex items-center justify-center shrink-0 ${
            turbineType === 'Pelton' ? 'bg-emerald-100 text-emerald-800 border border-emerald-200' :
            turbineType === 'Francis' ? 'bg-blue-100 text-blue-800 border border-blue-200' :
            turbineType === 'Kaplan' ? 'bg-amber-100 text-amber-800 border border-amber-200' : 'bg-red-100 text-red-800'
          }`}>
            Turbina {turbineType}
          </span>
        </div>
        <div className="p-6 grid grid-cols-2 md:grid-cols-4 gap-6 bg-slate-50/50">
          <div>
            <p className="text-xs text-slate-500 font-bold uppercase tracking-wide mb-1">Rot. Específica (Ns)</p>
            <p className="text-3xl font-extrabold text-slate-900">{Ns.toFixed(1)}</p>
          </div>
          <div>
             <p className="text-xs text-slate-500 font-bold uppercase tracking-wide mb-1">Potência Estimada</p>
            <p className="text-3xl font-extrabold text-slate-900">{P_MW.toFixed(2)} <span className="text-lg text-slate-400 font-medium">MW</span></p>
          </div>
          <div>
             <p className="text-xs text-slate-500 font-bold uppercase tracking-wide mb-1">Rotação Síncrona</p>
            <p className="text-3xl font-extrabold text-slate-900">{N.toFixed(1)} <span className="text-lg text-slate-400 font-medium">RPM</span></p>
          </div>
          <div>
             <p className="text-xs text-slate-500 font-bold uppercase tracking-wide mb-1">Diâmetro (D1_est)</p>
            <p className="text-3xl font-extrabold text-slate-900">{D1_est.toFixed(2)} <span className="text-lg text-slate-400 font-medium">m</span></p>
          </div>
        </div>
      </div>

       {/* AVISOS DE SEGURANÇA */}
       {inputs.useAdvanced && inputs.D1 <= inputs.D2 && (
         <div className="bg-red-50 border border-red-200 text-red-700 p-5 rounded-2xl animate-in slide-in-from-top-4 duration-500 shadow-sm">
           <strong className="font-bold">🚨 Aviso de Segurança Geométrico:</strong>
           <span className="block mt-1 text-sm font-medium">O diâmetro de entrada (D1) não pode ser menor ou igual ao diâmetro de saída (D2). Em turbinas centrípetas, o fluxo entra pelo diâmetro maior e sai pelo menor. Verifique os valores inseridos.</span>
         </div>
       )}

       {/* 2. CINEMÁTICA E EULER */}
       {inputs.useAdvanced && inlet && outlet && (
         <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-500">
           <div className="p-6 border-b border-slate-100">
             <h2 className="text-xl font-extrabold text-slate-800">2. Análise Cinemática (Euler)</h2>
             <p className="text-xs text-slate-500 font-medium mt-1">
               Avaliação do intercâmbio de quantidade de movimento a partir da geometria e escoamento.
             </p>
           </div>
           
           <div className="p-6 grid grid-cols-1 md:grid-cols-3 gap-6 bg-purple-50/30">
             <div className="bg-white p-5 rounded-xl border border-purple-100 shadow-sm">
                <p className="text-[11px] text-purple-600 font-bold uppercase tracking-widest mb-1.5">Carga Específica (Heuler)</p>
                <p className="text-3xl font-extrabold text-slate-800">{Heuler.toFixed(1)} <span className="text-lg text-slate-400 font-medium">m</span></p>
                <p className="text-xs text-slate-400 mt-2 font-medium">Energia bruta atuante no rotor</p>
             </div>
             <div className="bg-white p-5 rounded-xl border border-purple-100 shadow-sm">
                <p className="text-[11px] text-purple-600 font-bold uppercase tracking-widest mb-1.5">Potência (Euler)</p>
                <p className="text-3xl font-extrabold text-slate-800">{eulerPowerkW.toFixed(0)} <span className="text-lg text-slate-400 font-medium">kW</span></p>
                <p className="text-xs text-slate-400 mt-2 font-medium">Capacidade vetorial de extração</p>
             </div>
             <div className="bg-white p-5 rounded-xl border border-purple-100 shadow-sm">
                <p className="text-[11px] text-purple-600 font-bold uppercase tracking-widest mb-1.5">Rendimento Hidráulico</p>
                <p className="text-3xl font-extrabold text-slate-800">{(hydraulicEfficiency*100).toFixed(1)} <span className="text-lg text-slate-400 font-medium">%</span></p>
                <p className="text-xs text-slate-400 mt-2 font-medium">Heuler / Queda Líquida</p>
             </div>
           </div>

           <div className="p-6 grid grid-cols-1 lg:grid-cols-2 gap-8 border-t border-slate-100">
              <TrianglePlot triangle={inlet} title="Entrada no Rotor (Seção 1)" />
              <TrianglePlot triangle={outlet} title="Saída do Rotor (Seção 2)" />
           </div>
         </div>
       )}

       {/* 3. CFD / VALIDAÇÃO */}
       <div className="bg-slate-900 rounded-2xl shadow-sm border border-slate-800 overflow-hidden mt-8 text-white">
         <div className="p-6 border-b border-slate-800">
             <h2 className="text-xl font-extrabold text-white">3. Setup e Validação para CFD</h2>
             <p className="text-xs text-slate-400 font-medium mt-1">Exporte as Boundary Conditions numéricas para o Solver e valide a performance estrutural e de fluidos.</p>
         </div>
         <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-10">
           {/* Script */}
           <div>
             <div className="flex items-center justify-between mb-3">
               <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Variáveis de Expressão (Setup)</span>
               <button 
                 onClick={() => navigator.clipboard.writeText(cfdScript)} 
                 className="text-xs font-bold text-slate-900 bg-sky-400 hover:bg-sky-300 transition-colors px-3 py-1.5 rounded"
               >
                 COPIAR
               </button>
             </div>
             <pre className="bg-black/50 text-sky-300 p-5 rounded-xl text-[11px] leading-relaxed font-mono overflow-auto border border-slate-800/80 shadow-inner">
               {cfdScript}
             </pre>
           </div>
           
           {/* Post-processing */}
           <div className="space-y-5">
             <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Avaliação Múltipla de Resultados (CFD)</h3>
             <div className="grid grid-cols-2 gap-4">
               <div>
                  <label className="text-[11px] font-bold text-slate-400 block mb-1.5">Torque Medido no Eixo [N·m]</label>
                  <input type="number" value={simTorque} onChange={e => setSimTorque(parseFloat(e.target.value))} placeholder={outputs.torque.toFixed(0)} className="w-full bg-slate-800 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white focus:ring-2 focus:ring-sky-500 outline-none" />
               </div>
               <div>
                  <label className="text-[11px] font-bold text-slate-400 block mb-1.5">Queda P. Total Efetiva [m] <span className="opacity-50 font-normal">(Opcional)</span></label>
                  <input type="number" value={simHead} onChange={e => setSimHead(parseFloat(e.target.value))} placeholder={inputs.H.toString()} className="w-full bg-slate-800 border border-slate-700/50 rounded-lg px-3 py-2 text-sm text-white focus:ring-2 focus:ring-sky-500 outline-none" />
               </div>
             </div>

             {hasCFD && (
               <div className="mt-6 p-5 bg-sky-950/40 rounded-xl border border-sky-900 animate-in zoom-in-95 duration-300">
                 <div className="grid grid-cols-2 gap-6">
                   <div>
                     <p className="text-[10px] text-sky-400 font-bold uppercase tracking-widest mb-1">Potência Final (Eixo)</p>
                     <p className="text-2xl font-extrabold text-white">{powerSimkW.toFixed(1)} <span className="text-sm font-medium text-sky-200">kW</span></p>
                   </div>
                   <div>
                     <p className="text-[10px] text-sky-400 font-bold uppercase tracking-widest mb-1">Desvio vs Meta Global</p>
                     <p className="text-2xl font-extrabold text-white">{effTargetGlobal.toFixed(1)} <span className="text-sm font-medium text-sky-200">%</span></p>
                   </div>
                 </div>
                 
                 {simHead > 0 && typeof effGlobal === 'number' && (
                   <div className="mt-5 pt-5 border-t border-sky-900/50 grid grid-cols-2 gap-6">
                      <div>
                        <p className="text-[10px] text-sky-400 font-bold uppercase tracking-widest mb-1">Efic. Fluido-Mecânica</p>
                        <p className="text-xl font-extrabold text-white">{effGlobal.toFixed(1)} %</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-sky-400 font-bold uppercase tracking-widest mb-1">Desvio vs Cinemática</p>
                        <p className="text-xl font-extrabold text-white">{effTargetEuler.toFixed(1)} %</p>
                      </div>
                   </div>
                 )}
               </div>
             )}

           </div>
         </div>
       </div>

    </div>
  );
}

// Visualizador de Triângulo Simples
function TrianglePlot({ triangle, title }: { triangle: VelocityTriangle, title: string }) {
  const max = Math.max(triangle.U, triangle.Cm, triangle.Cu) || 1;
  const scale = 220 / max; 
  const originX = 40; 
  const originY = 240; 

  const pU = { x: originX + triangle.U * scale, y: originY };
  const pC = { x: originX + triangle.Cu * scale, y: originY - triangle.Cm * scale };

  return (
    <div className="rounded-xl bg-white border border-slate-200 overflow-hidden shadow-sm">
      <div className="p-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
         <h3 className="text-sm font-extrabold text-slate-800 uppercase tracking-widest">{title}</h3>
         <div className="flex gap-3 text-[11px] font-mono text-slate-600 font-bold">
           <span><span className="text-blue-500 mr-1">U:</span>{triangle.U.toFixed(1)}</span>
           <span><span className="text-red-500 mr-1">C:</span>{triangle.C.toFixed(1)}</span>
           <span><span className="text-emerald-500 mr-1">W:</span>{triangle.W.toFixed(1)}</span>
         </div>
      </div>
      <div className="relative flex justify-center py-6 bg-slate-50/30">
        <svg width="400" height="280" className="max-w-full">
           <defs>
             <marker id="arrowU" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L0,7 L7,3.5 z" fill="#3b82f6" /></marker>
             <marker id="arrowC" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L0,7 L7,3.5 z" fill="#ef4444" /></marker>
             <marker id="arrowW" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L0,7 L7,3.5 z" fill="#10b981" /></marker>
           </defs>
           <line x1="0" y1={originY} x2="400" y2={originY} stroke="#cbd5e1" strokeDasharray="3 3" />
           <line x1={originX} y1="0" x2={originX} y2="280" stroke="#cbd5e1" strokeDasharray="3 3" />

           <line x1={originX} y1={originY} x2={pU.x} y2={pU.y} stroke="#3b82f6" strokeWidth="3" markerEnd="url(#arrowU)" />
           <line x1={originX} y1={originY} x2={pC.x} y2={pC.y} stroke="#ef4444" strokeWidth="3" markerEnd="url(#arrowC)" />
           <line x1={pU.x} y1={pU.y} x2={pC.x} y2={pC.y} stroke="#10b981" strokeWidth="3" markerEnd="url(#arrowW)" />

           <text x={originX + (triangle.U * scale) / 2} y={originY + 20} fill="#3b82f6" fontSize="13" fontWeight="bold">U</text>
           <text x={originX + (triangle.Cu * scale) / 2 - 15} y={originY - (triangle.Cm * scale) / 2 - 5} fill="#ef4444" fontSize="13" fontWeight="bold">C</text>
           <text x={pU.x + (pC.x - pU.x) / 2 + 10} y={pU.y + (pC.y - pU.y) / 2} fill="#10b981" fontSize="13" fontWeight="bold">W</text>
        </svg>
      </div>
    </div>
  );
}
