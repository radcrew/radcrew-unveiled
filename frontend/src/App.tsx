import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { PageTransitionLayout } from "@components/PageTransitionLayout";
import { Toaster as Sonner } from "@components/ui/sonner";
import { Toaster } from "@components/ui/toaster";
import { TooltipProvider } from "@components/ui/tooltip";
import { ChatWidget } from "@components/chat-widget";
import { BackToTop } from "@components/BackToTop";
import { ScrollProgress } from "@components/motion/ScrollProgress";
import Index from "./pages/Index.tsx";
import WorkIndex from "./pages/WorkIndex.tsx";
import CaseStudy from "./pages/CaseStudy.tsx";
import JournalIndex from "./pages/JournalIndex.tsx";
import JournalPost from "./pages/JournalPost.tsx";
import NotFound from "./pages/NotFound.tsx";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <ScrollProgress />
        <Routes>
          <Route element={<PageTransitionLayout />}>
            <Route path="/" element={<Index />} />
            <Route path="/work" element={<WorkIndex />} />
            <Route path="/work/:slug" element={<CaseStudy />} />
            <Route path="/journal" element={<JournalIndex />} />
            <Route path="/journal/:slug" element={<JournalPost />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
        <ChatWidget />
        <BackToTop />
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
