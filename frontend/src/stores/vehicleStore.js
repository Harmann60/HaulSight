import { create } from 'zustand';

export const useVehicleStore = create((set, get) => ({
  vehicles: [],

  setVehicles: (vehicles) => set({ vehicles }),

  updateVehicle: (data) => {
    const current = get().vehicles;
    const idx = current.findIndex((v) => v.vehicle_id === data.vehicle_id);
    if (idx >= 0) {
      const updated = [...current];
      updated[idx] = { ...updated[idx], ...data };
      set({ vehicles: updated });
    } else {
      set({ vehicles: [...current, data] });
    }
  },

  removeVehicle: (vehicleId) => {
    set({ vehicles: get().vehicles.filter((v) => v.vehicle_id !== vehicleId) });
  },
}));
