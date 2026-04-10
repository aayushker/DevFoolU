"use client";

import { useAuth } from "@/lib/auth0-provider";
import { Button } from "@/components/ui/button";

export default function LoginButton() {
  const { loginWithRedirect, isLoading } = useAuth();

  const handleLogin = async () => {
    await loginWithRedirect({
      appState: {
        returnTo: window.location.pathname,
      },
    });
  };

  return (
    <Button
      onClick={handleLogin}
      disabled={isLoading}
      className="bg-blue-600 hover:bg-blue-700 text-white"
    >
      {isLoading ? "Loading..." : "Log In"}
    </Button>
  );
}
