import { lazy, Suspense } from "react";
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/contexts/ThemeContext";
import { UserProgressProvider } from "@/contexts/UserProgressContext";
import { ChatHistoryProvider } from "@/contexts/ChatHistoryContext";
import { AuthProvider } from "@/contexts/AuthContext";
import { TutorialProvider } from "@/contexts/TutorialContext";
import { AppLayout } from "@/components/layout/AppLayout";
import AchievementToast from "@/components/gamification/AchievementToast";
import CommandPalette from "@/components/CommandPalette";
import { Skeleton } from "@/components/ui/skeleton";

// Eager load critical pages
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";

// Lazy load non-critical pages for better initial load
const ChatPage = lazy(() => import("./pages/ChatPage"));
const TrainingPage = lazy(() => import("./pages/TrainingPage"));
const ModuleDetailPage = lazy(() => import("./pages/ModuleDetailPage"));
const LessonPage = lazy(() => import("./pages/LessonPage"));
const DashboardPage = lazy(() => import("./pages/DashboardPage"));
const AnalyticsPage = lazy(() => import("./pages/AnalyticsPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));
const AuthPage = lazy(() => import("./pages/AuthPage"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
      refetchOnWindowFocus: false, // Reduce unnecessary refetches
      retry: 1, // Reduce retry attempts for faster failure
    },
  },
});

// Optimized loading fallback component
const PageLoader = () => (
  <div className="p-4 sm:p-6 space-y-4 animate-fade-in">
    <Skeleton className="h-10 sm:h-12 w-48 sm:w-64" />
    <Skeleton className="h-5 sm:h-6 w-72 sm:w-96" />
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-6 sm:mt-8">
      <Skeleton className="h-40 sm:h-48 w-full" />
      <Skeleton className="h-40 sm:h-48 w-full hidden sm:block" />
      <Skeleton className="h-40 sm:h-48 w-full hidden lg:block" />
    </div>
  </div>
);

// Auth page has its own layout
const AuthPageWrapper = () => (
  <Suspense fallback={<PageLoader />}>
    <AuthPage />
  </Suspense>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <AuthProvider>
        <UserProgressProvider>
          <ChatHistoryProvider>
            <TutorialProvider>
              <TooltipProvider>
                <Toaster />
                <Sonner />
                <BrowserRouter>
                <AchievementToast />
                <CommandPalette />
                  <Routes>
                    {/* Auth page without AppLayout */}
                    <Route path="/auth" element={<AuthPageWrapper />} />
                    
                    {/* All other routes with AppLayout */}
                    <Route
                      path="/*"
                      element={
                        <AppLayout>
                          <Suspense fallback={<PageLoader />}>
                            <Routes>
                              <Route path="/" element={<Index />} />
                              <Route path="/chat" element={<ChatPage />} />
                              <Route path="/training" element={<TrainingPage />} />
                              <Route path="/training/:moduleId" element={<ModuleDetailPage />} />
                              <Route path="/training/:moduleId/lesson/:lessonId" element={<LessonPage />} />
                              <Route path="/dashboard" element={<DashboardPage />} />
                              <Route path="/analytics" element={<AnalyticsPage />} />
                              <Route path="/settings" element={<SettingsPage />} />
                              <Route path="*" element={<NotFound />} />
                            </Routes>
                          </Suspense>
                        </AppLayout>
                      }
                    />
                  </Routes>
                </BrowserRouter>
              </TooltipProvider>
            </TutorialProvider>
          </ChatHistoryProvider>
        </UserProgressProvider>
      </AuthProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
