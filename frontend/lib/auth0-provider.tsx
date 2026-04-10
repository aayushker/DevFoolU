"use client";

import { Auth0Provider, useAuth0 } from "@auth0/auth0-react";
import { useRouter } from "next/navigation";
import React, { useEffect } from "react";

interface Auth0ProviderWithNavigateProps {
  children: React.ReactNode;
}

const Auth0ProviderWithHistory: React.FC<Auth0ProviderWithNavigateProps> = ({
  children,
}) => {
  const router = useRouter();

  const domain = process.env.NEXT_PUBLIC_AUTH0_DOMAIN!;
  const clientId = process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!;
  const audience = process.env.NEXT_PUBLIC_AUTH0_AUDIENCE!;
  const redirectUri =
    typeof window !== "undefined"
      ? window.location.origin
      : process.env.NEXT_PUBLIC_AUTH0_REDIRECT_URI || "http://localhost:3000";

  const onRedirectCallback = (appState?: any) => {
    router.push(appState?.returnTo || "/dashboard");
  };

  return (
    <Auth0Provider
      domain={domain}
      clientId={clientId}
      authorizationParams={{
        redirect_uri: redirectUri,
        audience: audience,
        scope: "openid profile email",
      }}
      onRedirectCallback={onRedirectCallback}
      cacheLocation="localstorage"
      useRefreshTokens={true}
    >
      {children}
    </Auth0Provider>
  );
};

export const Auth0ProviderWithNavigate: React.FC<
  Auth0ProviderWithNavigateProps
> = ({ children }) => {
  return <Auth0ProviderWithHistory>{children}</Auth0ProviderWithHistory>;
};

// Re-export useAuth0 as useAuth for consistency with existing code
export const useAuth = useAuth0;
