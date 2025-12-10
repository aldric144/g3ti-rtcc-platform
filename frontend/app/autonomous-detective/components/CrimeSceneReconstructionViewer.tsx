'use client';

import React, { useState, useEffect } from 'react';

interface Evidence {
  evidence_id: string;
  evidence_type: string;
  position: { x: number; y: number; z: number };
  description: string;
}

interface Reconstruction {
  reconstruction_id: string;
  case_id: string;
  scene_type: string;
  status: string;
  confidence_score: number;
  evidence_count: number;
}

interface Props {
  caseId: string | null;
}

export default function CrimeSceneReconstructionViewer({ caseId }: Props) {
  const [reconstruction, setReconstruction] = useState<Reconstruction | null>(null);
  const [evidence, setEvidence] = useState<Evidence[]>([]);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [viewMode, setViewMode] = useState<'2d' | '3d'>('2d');
  const [selectedEvidence, setSelectedEvidence] = useState<Evidence | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (caseId) {
      loadReconstruction();
    }
  }, [caseId]);

  const loadReconstruction = async () => {
    setLoading(true);
    setTimeout(() => {
      setReconstruction({
        reconstruction_id: 'recon-001',
        case_id: caseId || '',
        scene_type: 'indoor',
        status: 'analyzed',
        confidence_score: 0.85,
        evidence_count: 12,
      });
      setEvidence([
        { evidence_id: 'ev-001', evidence_type: 'blood_spatter', position: { x: 25, y: 30, z: 0 }, description: 'Blood spatter pattern on wall' },
        { evidence_id: 'ev-002', evidence_type: 'fingerprint', position: { x: 45, y: 50, z: 1 }, description: 'Latent fingerprint on door handle' },
        { evidence_id: 'ev-003', evidence_type: 'weapon', position: { x: 60, y: 40, z: 0 }, description: 'Knife found under furniture' },
        { evidence_id: 'ev-004', evidence_type: 'footprint', position: { x: 35, y: 70, z: 0 }, description: 'Shoe impression near entry' },
        { evidence_id: 'ev-005', evidence_type: 'dna', position: { x: 50, y: 35, z: 0 }, description: 'DNA sample from cigarette butt' },
      ]);
      setTimeline([
        { time: '22:15', event: 'Suspect enters through rear door', confidence: 0.9 },
        { time: '22:18', event: 'Confrontation begins in living room', confidence: 0.75 },
        { time: '22:22', event: 'Victim sustains injuries', confidence: 0.85 },
        { time: '22:25', event: 'Suspect exits through front door', confidence: 0.8 },
      ]);
      setLoading(false);
    }, 500);
  };

  const getEvidenceColor = (type: string) => {
    const colors: Record<string, string> = {
      blood_spatter: 'bg-red-500',
      fingerprint: 'bg-yellow-500',
      weapon: 'bg-orange-500',
      footprint: 'bg-green-500',
      dna: 'bg-purple-500',
      fiber: 'bg-blue-500',
    };
    return colors[type] || 'bg-gray-500';
  };

  if (!caseId) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-800 rounded-lg">
        <p className="text-gray-400">Select a case to view crime scene reconstruction</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold">Crime Scene Reconstruction</h2>
        <div className="flex items-center gap-4">
          <div className="flex bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setViewMode('2d')}
              className={`px-4 py-2 rounded text-sm ${viewMode === '2d' ? 'bg-blue-600' : ''}`}
            >
              2D View
            </button>
            <button
              onClick={() => setViewMode('3d')}
              className={`px-4 py-2 rounded text-sm ${viewMode === '3d' ? 'bg-blue-600' : ''}`}
            >
              3D View
            </button>
          </div>
          <button
            onClick={loadReconstruction}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm"
          >
            Refresh
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-2 bg-gray-800 rounded-lg p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">Scene Visualization</h3>
            {reconstruction && (
              <span className="text-sm text-gray-400">
                Confidence: {(reconstruction.confidence_score * 100).toFixed(0)}%
              </span>
            )}
          </div>

          <div className="relative bg-gray-900 rounded-lg h-96 overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
              </div>
            ) : (
              <>
                <div className="absolute inset-0 grid grid-cols-10 grid-rows-10 opacity-20">
                  {Array.from({ length: 100 }).map((_, i) => (
                    <div key={i} className="border border-gray-700"></div>
                  ))}
                </div>

                {evidence.map((ev) => (
                  <div
                    key={ev.evidence_id}
                    className={`absolute w-4 h-4 rounded-full cursor-pointer transform -translate-x-1/2 -translate-y-1/2 ${getEvidenceColor(ev.evidence_type)} ${selectedEvidence?.evidence_id === ev.evidence_id ? 'ring-2 ring-white' : ''}`}
                    style={{ left: `${ev.position.x}%`, top: `${ev.position.y}%` }}
                    onClick={() => setSelectedEvidence(ev)}
                    title={ev.description}
                  />
                ))}

                <svg className="absolute inset-0 w-full h-full pointer-events-none">
                  <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                      <polygon points="0 0, 10 3.5, 0 7" fill="#60A5FA" />
                    </marker>
                  </defs>
                  <path
                    d="M 35 70 Q 40 55 45 50 Q 50 45 50 35"
                    stroke="#60A5FA"
                    strokeWidth="2"
                    fill="none"
                    strokeDasharray="5,5"
                    markerEnd="url(#arrowhead)"
                  />
                </svg>
              </>
            )}
          </div>

          <div className="flex items-center gap-4 mt-4">
            <span className="text-sm text-gray-400">Legend:</span>
            {['blood_spatter', 'fingerprint', 'weapon', 'footprint', 'dna'].map((type) => (
              <div key={type} className="flex items-center gap-1">
                <div className={`w-3 h-3 rounded-full ${getEvidenceColor(type)}`}></div>
                <span className="text-xs text-gray-400 capitalize">{type.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-medium mb-3">Reconstruction Status</h3>
            {reconstruction ? (
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Status</span>
                  <span className="text-green-400 capitalize">{reconstruction.status}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Scene Type</span>
                  <span className="capitalize">{reconstruction.scene_type}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Evidence Items</span>
                  <span>{reconstruction.evidence_count}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-400">Confidence</span>
                  <span>{(reconstruction.confidence_score * 100).toFixed(0)}%</span>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">No reconstruction data</p>
            )}
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-medium mb-3">Selected Evidence</h3>
            {selectedEvidence ? (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getEvidenceColor(selectedEvidence.evidence_type)}`}></div>
                  <span className="text-sm capitalize">{selectedEvidence.evidence_type.replace('_', ' ')}</span>
                </div>
                <p className="text-sm text-gray-400">{selectedEvidence.description}</p>
                <div className="text-xs text-gray-500">
                  Position: ({selectedEvidence.position.x}, {selectedEvidence.position.y}, {selectedEvidence.position.z})
                </div>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">Click on evidence marker to view details</p>
            )}
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="font-medium mb-3">Reconstructed Timeline</h3>
            <div className="space-y-3">
              {timeline.map((event, index) => (
                <div key={index} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    {index < timeline.length - 1 && (
                      <div className="w-0.5 h-8 bg-gray-600"></div>
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium">{event.time}</span>
                      <span className="text-xs text-gray-400">
                        {(event.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-400">{event.event}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
