import { create } from 'zustand';

export const useAlertStore = create((set, get) => ({
  activeAlerts: [],
  alertHistory: [],

  setActiveAlerts: (alerts) => set({ activeAlerts: alerts }),

  addAlert: (alert) => {
    const current = get().activeAlerts;
    if (!current.find((a) => a.alert_id === alert.alert_id)) {
      set({ activeAlerts: [...current, alert] });
    }
  },

  updateAlert: (alert) => {
    set({
      activeAlerts: get().activeAlerts.map((a) =>
        a.alert_id === alert.alert_id ? { ...a, ...alert } : a
      ),
    });
  },

  removeAlert: (alertId) => {
    const removed = get().activeAlerts.find((a) => a.alert_id === alertId);
    set({ activeAlerts: get().activeAlerts.filter((a) => a.alert_id !== alertId) });
    if (removed) {
      set({ alertHistory: [removed, ...get().alertHistory].slice(0, 100) });
    }
  },

  setAlertHistory: (history) => set({ alertHistory: history }),
}));
