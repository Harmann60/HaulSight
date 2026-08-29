import { create } from 'zustand';

export const useAIStore = create((set, get) => ({
  visibility: {
    estimated_visibility_m: null,
    fog_severity: 'UNKNOWN',
    confidence: 0,
    inputs: {},
    data_mode: 'SIMULATION',
    updated_at: null,
  },
  hotspots: {
    zones: [],
    total_alerts: 0,
    max_score: 0,
    updated_at: null,
  },
  production: {
    normal_cycle_min: 0,
    predicted_cycle_min: 0,
    increase_pct: 0,
    production_impact_pct: 0,
    confidence: 0,
    updated_at: null,
  },
  radarClassifications: [],

  setVisibility: (visibility) => set({ visibility }),
  setHotspots: (hotspots) => set({ hotspots }),
  setProduction: (production) => set({ production }),

  addRadarClassification: (classification) => {
    const current = get().radarClassifications;
    set({ radarClassifications: [classification, ...current].slice(0, 10) });
  },

  setRadarClassifications: (list) => set({ radarClassifications: list.slice(0, 10) }),
}));
