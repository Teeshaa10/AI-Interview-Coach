import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "@/layouts/AppLayout";
import { ProtectedRoute } from "@/routes/ProtectedRoute";
import { PublicOnlyRoute } from "@/routes/PublicOnlyRoute";

import { LoginPage } from "@/pages/auth/LoginPage";
import { RegisterPage } from "@/pages/auth/RegisterPage";
import { DashboardPage } from "@/pages/dashboard/DashboardPage";
import { ResumePage } from "@/pages/resume/ResumePage";
import { ResumeUploadPage } from "@/pages/resume/ResumeUploadPage";
import { ResumeDetailPage } from "@/pages/resume/ResumeDetailPage";
import { ResumeSearchPage } from "@/pages/resume/ResumeSearchPage";
import { InterviewsPage } from "@/pages/interview/InterviewsPage";
import { InterviewSetupPage } from "@/pages/interview/InterviewSetupPage";
import { InterviewSessionPage } from "@/pages/interview/InterviewSessionPage";
import { InterviewCompletePage } from "@/pages/interview/InterviewCompletePage";
import { VoiceInterviewSetupPage } from "@/pages/voice/VoiceInterviewSetupPage";
import { VoiceInterviewSessionPage } from "@/pages/voice/VoiceInterviewSessionPage";
import { VoiceInterviewCompletePage } from "@/pages/voice/VoiceInterviewCompletePage";
import { CodingInterviewSetupPage } from "@/pages/coding/CodingInterviewSetupPage";
import { CodingInterviewSessionPage } from "@/pages/coding/CodingInterviewSessionPage";
import { CodingInterviewCompletePage } from "@/pages/coding/CodingInterviewCompletePage";
import { CoachingDashboardPage } from "@/pages/coaching/CoachingDashboardPage";
import { ReportsDashboardPage } from "@/pages/reports/ReportsDashboardPage";
import { ReportHistoryPage } from "@/pages/reports/ReportHistoryPage";
import { ReportDetailPage } from "@/pages/reports/ReportDetailPage";
import { UnifiedHistoryPage } from "@/pages/sessions/UnifiedHistoryPage";
import { NotFoundPage } from "@/pages/NotFoundPage";

function App() {
  return (
    <Routes>
      <Route element={<PublicOnlyRoute />}>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<DashboardPage />} />

          <Route path="/resumes" element={<ResumePage />} />
          <Route path="/resumes/upload" element={<ResumeUploadPage />} />
          <Route path="/resumes/search" element={<ResumeSearchPage />} />
          <Route path="/resumes/:resumeId" element={<ResumeDetailPage />} />

          <Route path="/interviews" element={<InterviewsPage />} />
          <Route path="/interviews/setup" element={<InterviewSetupPage />} />
          <Route path="/interviews/:sessionId" element={<InterviewSessionPage />} />
          <Route path="/interviews/:sessionId/complete" element={<InterviewCompletePage />} />

          <Route path="/voice/setup" element={<VoiceInterviewSetupPage />} />
          <Route path="/voice/:sessionId" element={<VoiceInterviewSessionPage />} />
          <Route path="/voice/:sessionId/complete" element={<VoiceInterviewCompletePage />} />

          <Route path="/coding/setup" element={<CodingInterviewSetupPage />} />
          <Route path="/coding/:sessionId" element={<CodingInterviewSessionPage />} />
          <Route path="/coding/:sessionId/complete" element={<CodingInterviewCompletePage />} />

          <Route path="/coaching" element={<CoachingDashboardPage />} />

          <Route path="/reports" element={<ReportsDashboardPage />} />
          <Route path="/reports/history" element={<ReportHistoryPage />} />
          <Route path="/reports/interview/:interviewId" element={<ReportDetailPage />} />

          <Route path="/history" element={<UnifiedHistoryPage />} />
        </Route>
      </Route>

      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}

export default App;
