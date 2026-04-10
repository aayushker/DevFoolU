"use client";

import { useAuth } from "@/lib/auth0-provider";
import LoginButton from "./LoginButton";
import UserProfile from "./UserProfile";

export default function AuthNav() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="h-8 w-20 animate-pulse rounded bg-gray-200"></div>;
  }

  return <div>{isAuthenticated ? <UserProfile /> : <LoginButton />}</div>;
}
