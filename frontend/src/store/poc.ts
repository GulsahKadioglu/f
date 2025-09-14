import { create } from 'zustand';

interface PocState {
  data: any;
  setData: (data: any) => void;
}

export const usePocStore = create<PocState>((set) => ({
  data: null,
  setData: (data) => set({ data }),
}));
