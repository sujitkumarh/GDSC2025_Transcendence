import { create } from 'zustand'

interface AppState {
  currentLanguage: 'en' | 'pt-BR'
  currentPersona: string | null
  isLoading: boolean
  setLanguage: (language: 'en' | 'pt-BR') => void
  setCurrentPersona: (personaId: string | null) => void
  setLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  currentLanguage: 'pt-BR',
  currentPersona: null,
  isLoading: false,
  setLanguage: (language) => set({ currentLanguage: language }),
  setCurrentPersona: (personaId) => set({ currentPersona: personaId }),
  setLoading: (loading) => set({ isLoading: loading }),
}))