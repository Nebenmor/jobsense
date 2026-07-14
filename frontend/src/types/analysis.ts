export interface AnalysisResult {
  id: string;
  job_title: string;
  match_score: number;
  matching_skills: string[];
  missing_skills: string[];
  suggestions: string[];
  created_at: string;
  expires_at: string;
}

export interface AnalysisSummary {
  id: string;
  job_title: string;
  match_score: number;
  created_at: string;
}
