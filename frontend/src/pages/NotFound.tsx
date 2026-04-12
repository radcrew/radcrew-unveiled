import { useLocation, Link } from "react-router-dom";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";
import { CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { RadCard } from "@/components/ui/rad-card";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <div className="not-found-root">
      <RadCard className="mx-auto w-full max-w-md text-center shadow-sm">
        <CardHeader>
          <CardTitle className="text-4xl">404</CardTitle>
          <CardDescription className="text-base">Oops! Page not found</CardDescription>
        </CardHeader>
        <CardFooter className="justify-center pb-6 pt-0">
          <Button asChild>
            <Link to="/">Return to Home</Link>
          </Button>
        </CardFooter>
      </RadCard>
    </div>
  );
};

export default NotFound;
