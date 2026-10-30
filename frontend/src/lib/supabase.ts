import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabasePublishableKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY

export const supabaseConfigError =
  !supabaseUrl || !supabasePublishableKey
    ? 'Authentication is not configured. Add the Supabase environment variables and restart the frontend.'
    : null

export const supabase = supabaseConfigError
  ? null
  : createClient(supabaseUrl, supabasePublishableKey, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    })
