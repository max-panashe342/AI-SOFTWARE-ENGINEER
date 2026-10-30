export type AssessmentSummary = {
  id: number
  slug: string
  name: string
  description: string
  department_name: string
  version: number
}

export type AssessmentQuestion = {
  id: number
  position: number
  type: string
  prompt: string
  instructions: string | null
  starter_code: string | null
  language: string | null
  max_score: number
  competency: {
    id: number
    name: string
    slug: string
    description: string
  }
}

export type AssessmentDetail = {
  id: number
  slug: string
  name: string
  description: string
  department_name: string
  version: {
    id: number
    version_number: number
    instructions: string
    time_limit_minutes: number | null
    questions: AssessmentQuestion[]
  }
}
