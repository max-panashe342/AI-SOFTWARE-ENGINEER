import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import type { Session, User } from '@supabase/supabase-js'

import { supabase, supabaseConfigError } from '../lib/supabase'

type AuthContextValue = {
  user: User | null
  isLoading: boolean
  error: string | null
  signIn: (email: string, password: string) => Promise<{ needsConfirmation: boolean; error: string | null }>
  signUp: (email: string, password: string) => Promise<{ needsConfirmation: boolean; error: string | null }>
  signOut: () => Promise<{ error: string | null }>
  clearError: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

function getErrorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.'
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(supabaseConfigError)

  useEffect(() => {
    if (!supabase) {
      setIsLoading(false)
      return
    }

    let isMounted = true
    void supabase.auth.getSession().then(({ data, error: sessionError }) => {
      if (!isMounted) return
      if (sessionError) setError(getErrorMessage(sessionError))
      setSession(data.session)
      setIsLoading(false)
    })

    const { data: listener } = supabase.auth.onAuthStateChange((_event, nextSession) => {
      if (isMounted) setSession(nextSession)
    })

    return () => {
      isMounted = false
      listener.subscription.unsubscribe()
    }
  }, [])

  const value = useMemo<AuthContextValue>(() => ({
    user: session?.user ?? null,
    isLoading,
    error,
    clearError: () => setError(null),
    signIn: async (email, password) => {
      if (!supabase) return { needsConfirmation: false, error: supabaseConfigError }
      const { error: signInError } = await supabase.auth.signInWithPassword({ email, password })
      if (signInError) {
        const message = getErrorMessage(signInError)
        setError(message)
        return { needsConfirmation: false, error: message }
      }
      setError(null)
      return { needsConfirmation: false, error: null }
    },
    signUp: async (email, password) => {
      if (!supabase) return { needsConfirmation: false, error: supabaseConfigError }
      const { data, error: signUpError } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: `${window.location.origin}/workspace`,
        },
      })
      if (signUpError) {
        const message = getErrorMessage(signUpError)
        setError(message)
        return { needsConfirmation: false, error: message }
      }
      setError(null)
      return { needsConfirmation: !data.session, error: null }
    },
    signOut: async () => {
      if (!supabase) return { error: supabaseConfigError }
      const { error: signOutError } = await supabase.auth.signOut()
      if (signOutError) {
        const message = getErrorMessage(signOutError)
        setError(message)
        return { error: message }
      }
      setError(null)
      return { error: null }
    },
  }), [error, isLoading, session])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
