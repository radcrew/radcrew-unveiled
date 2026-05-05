import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { PageTransitionLayout } from "@components/PageTransitionLayout";
import { Toaster as Sonner } from "@components/ui/sonner";
import { Toaster } from "@components/ui/toaster";
import { TooltipProvider } from "@components/ui/tooltip";
import { ChatWidget } from "@components/chat-widget";
import Index from "./pages/Index.tsx";
import TeamMember from "./pages/TeamMember.tsx";
import NotFound from "./pages/NotFound.tsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route element={<PageTransitionLayout />}>
            <Route path="/" element={<Index />} />
            <Route path="/team/:memberId" element={<TeamMember />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
        <ChatWidget />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
