'use client';

import React, { useState, useEffect } from 'react';

interface Hospital {
  hospital_id: string;
  name: string;
  status: string;
  total_beds: number;
  available_beds: number;
  icu_beds: number;
  icu_available: number;
  er_capacity: number;
  er_current: number;
  ambulance_divert: boolean;
  trauma_level: number;
}

interface TriagePatient {
  patient_id: string;
  triage_level: string;
  injury_type: string;
  transport_status: string;
  location_found: {
    lat: number;
    lng: number;
  };
}

interface MedicalMetrics {
  hospitals: {
    total: number;
    operational: number;
    on_divert: number;
    total_beds: number;
    available_beds: number;
  };
  ems: {
    total_units: number;
    available: number;
    on_call: number;
  };
  triage: {
    total_patients: number;
    immediate: number;
    delayed: number;
    minor: number;
    deceased: number;
  };
  supplies: {
    total_items: number;
    critical: number;
  };
}

interface CriticalStatus {
  hospitals_on_divert: number;
  icu_beds_available: number;
  immediate_patients: number;
  critical_supplies: number;
}

export default function MedicalSurgeForecastPanel() {
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [immediatePatients, setImmediatePatients] = useState<TriagePatient[]>([]);
  const [metrics, setMetrics] = useState<MedicalMetrics | null>(null);
  const [criticalStatus, setCriticalStatus] = useState<CriticalStatus | null>(null);
  const [activeTab, setActiveTab] = useState<'hospitals' | 'triage' | 'forecast'>('hospitals');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMedicalData();
    const interval = setInterval(fetchMedicalData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchMedicalData = async () => {
    try {
      const [hospitalsRes, triageRes, metricsRes, criticalRes] = await Promise.all([
        fetch('/api/emergency/medical/hospitals'),
        fetch('/api/emergency/medical/triage/immediate'),
        fetch('/api/emergency/medical/metrics'),
        fetch('/api/emergency/medical/critical-status'),
      ]);

      if (hospitalsRes.ok) setHospitals(await hospitalsRes.json());
      if (triageRes.ok) setImmediatePatients(await triageRes.json());
      if (metricsRes.ok) setMetrics(await metricsRes.json());
      if (criticalRes.ok) setCriticalStatus(await criticalRes.json());
    } catch (error) {
      console.error('Failed to fetch medical data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'operational': return 'text-green-400';
      case 'limited': return 'text-yellow-400';
      case 'critical': return 'text-orange-400';
      case 'closed': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getTriageLevelColor = (level: string): string => {
    switch (level) {
      case 'immediate': return 'bg-red-600';
      case 'delayed': return 'bg-yellow-600';
      case 'minor': return 'bg-green-600';
      case 'expectant': return 'bg-gray-600';
      case 'deceased': return 'bg-black';
      default: return 'bg-gray-600';
    }
  };

  const getCapacityColor = (available: number, total: number): string => {
    const percent = (available / total) * 100;
    if (percent <= 10) return 'text-red-400';
    if (percent <= 30) return 'text-yellow-400';
    return 'text-green-400';
  };

  if (loading) {
    return (
      <div className="bg-gray-900 rounded-lg p-6 h-full flex items-center justify-center">
        <div className="text-gray-400">Loading medical data...</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-lg p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span>🏥</span> Medical Surge Forecast
        </h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab('hospitals')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'hospitals' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Hospitals
          </button>
          <button
            onClick={() => setActiveTab('triage')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'triage' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Triage
          </button>
          <button
            onClick={() => setActiveTab('forecast')}
            className={`px-3 py-1 rounded text-sm ${
              activeTab === 'forecast' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-gray-300'
            }`}
          >
            Forecast
          </button>
        </div>
      </div>

      {criticalStatus && (
        <div className="grid grid-cols-4 gap-3 mb-4">
          <div className={`p-3 rounded ${criticalStatus.hospitals_on_divert > 0 ? 'bg-red-900/50' : 'bg-gray-800'}`}>
            <div className="text-gray-400 text-xs">On Divert</div>
            <div className={`text-lg font-bold ${criticalStatus.hospitals_on_divert > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {criticalStatus.hospitals_on_divert}
            </div>
          </div>
          <div className="bg-gray-800 p-3 rounded">
            <div className="text-gray-400 text-xs">ICU Available</div>
            <div className={`text-lg font-bold ${criticalStatus.icu_beds_available < 10 ? 'text-red-400' : 'text-white'}`}>
              {criticalStatus.icu_beds_available}
            </div>
          </div>
          <div className={`p-3 rounded ${criticalStatus.immediate_patients > 0 ? 'bg-red-900/50' : 'bg-gray-800'}`}>
            <div className="text-gray-400 text-xs">Immediate</div>
            <div className={`text-lg font-bold ${criticalStatus.immediate_patients > 0 ? 'text-red-400' : 'text-green-400'}`}>
              {criticalStatus.immediate_patients}
            </div>
          </div>
          <div className={`p-3 rounded ${criticalStatus.critical_supplies > 0 ? 'bg-yellow-900/50' : 'bg-gray-800'}`}>
            <div className="text-gray-400 text-xs">Critical Supplies</div>
            <div className={`text-lg font-bold ${criticalStatus.critical_supplies > 0 ? 'text-yellow-400' : 'text-green-400'}`}>
              {criticalStatus.critical_supplies}
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {activeTab === 'hospitals' && (
          <div className="space-y-2">
            {hospitals.length === 0 ? (
              <div className="text-gray-500 text-center py-8">No hospitals registered</div>
            ) : (
              hospitals.map(hospital => (
                <div key={hospital.hospital_id} className="bg-gray-800 p-4 rounded">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-white font-medium">{hospital.name}</span>
                        {hospital.trauma_level > 0 && (
                          <span className="bg-purple-600 text-white px-1.5 py-0.5 rounded text-xs">
                            Level {hospital.trauma_level}
                          </span>
                        )}
                      </div>
                      <div className={`text-sm ${getStatusColor(hospital.status)}`}>
                        {hospital.status.toUpperCase()}
                        {hospital.ambulance_divert && (
                          <span className="text-red-400 ml-2">• ON DIVERT</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400 text-xs">Beds</div>
                      <div className={getCapacityColor(hospital.available_beds, hospital.total_beds)}>
                        {hospital.available_beds} / {hospital.total_beds}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">ICU</div>
                      <div className={getCapacityColor(hospital.icu_available, hospital.icu_beds)}>
                        {hospital.icu_available} / {hospital.icu_beds}
                      </div>
                    </div>
                    <div>
                      <div className="text-gray-400 text-xs">ER</div>
                      <div className={getCapacityColor(hospital.er_capacity - hospital.er_current, hospital.er_capacity)}>
                        {hospital.er_current} / {hospital.er_capacity}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === 'triage' && (
          <div>
            {metrics?.triage && (
              <div className="grid grid-cols-5 gap-2 mb-4">
                <div className="bg-red-900/50 p-2 rounded text-center">
                  <div className="text-red-400 text-lg font-bold">{metrics.triage.immediate}</div>
                  <div className="text-gray-400 text-xs">Immediate</div>
                </div>
                <div className="bg-yellow-900/50 p-2 rounded text-center">
                  <div className="text-yellow-400 text-lg font-bold">{metrics.triage.delayed}</div>
                  <div className="text-gray-400 text-xs">Delayed</div>
                </div>
                <div className="bg-green-900/50 p-2 rounded text-center">
                  <div className="text-green-400 text-lg font-bold">{metrics.triage.minor}</div>
                  <div className="text-gray-400 text-xs">Minor</div>
                </div>
                <div className="bg-gray-800 p-2 rounded text-center">
                  <div className="text-gray-400 text-lg font-bold">{metrics.triage.deceased}</div>
                  <div className="text-gray-400 text-xs">Deceased</div>
                </div>
                <div className="bg-gray-800 p-2 rounded text-center">
                  <div className="text-white text-lg font-bold">{metrics.triage.total_patients}</div>
                  <div className="text-gray-400 text-xs">Total</div>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {immediatePatients.length === 0 ? (
                <div className="text-gray-500 text-center py-8">No immediate patients</div>
              ) : (
                <>
                  <div className="text-red-400 text-sm mb-2">🚨 Immediate Care Required</div>
                  {immediatePatients.map(patient => (
                    <div key={patient.patient_id} className="bg-gray-800 p-4 rounded border-l-4 border-red-500">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded text-xs text-white ${getTriageLevelColor(patient.triage_level)}`}>
                              {patient.triage_level.toUpperCase()}
                            </span>
                            <span className="text-white">{patient.injury_type}</span>
                          </div>
                          <div className="text-gray-400 text-sm mt-1">
                            Transport: {patient.transport_status}
                          </div>
                        </div>
                        <div className="text-gray-500 text-sm">
                          ID: {patient.patient_id.slice(0, 8)}
                        </div>
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>
          </div>
        )}

        {activeTab === 'forecast' && (
          <div className="bg-gray-800 p-4 rounded">
            <div className="text-center py-8">
              <div className="text-4xl mb-4">📊</div>
              <div className="text-white font-medium">Medical Surge Forecasting</div>
              <div className="text-gray-400 text-sm mt-2">
                Predict hospital load and EMS demand based on incident data
              </div>
              <button className="mt-4 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded">
                Generate Forecast
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
