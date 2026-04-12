import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/hooks/useAuth";
import ProtectedRoute from "@/components/ProtectedRoute";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import DashboardLayout from "./components/Dashboard/DashboardLayout";
import DashboardHome from "./pages/dashboard/DashboardHome";
import UploadPage from "./pages/dashboard/UploadPage";
import WorkspacePage from "./pages/dashboard/WorkspacePage";
import ChatPage from "./pages/dashboard/ChatPage";
import InsightsPage from "./pages/dashboard/InsightsPage";
import HistoryPage from "./pages/dashboard/HistoryPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <DashboardLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardHome />} />
              <Route path="upload" element={<UploadPage />} />
              <Route path="workspace" element={<WorkspacePage />} />
              <Route path="chat" element={<ChatPage />} />
              <Route path="insights" element={<InsightsPage />} />
              <Route path="history" element={<HistoryPage />} />
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
