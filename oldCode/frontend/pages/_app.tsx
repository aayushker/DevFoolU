import type { AppProps } from "next/app";
import { ClerkProvider } from "@clerk/nextjs";
import { NextUIProvider } from "@nextui-org/react";
import { dark } from "@clerk/themes";
import "@/app/globals.css";

export default function App({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      appearance={{
        baseTheme: dark,
        elements: {
          formButtonPrimary: "bg-blue-900 hover:bg-blue-800",
          footerActionLink: "text-blue-900 hover:text-blue-800",
        },
      }}
    >
      <NextUIProvider>
        <Component {...pageProps} />
      </NextUIProvider>
    </ClerkProvider>
  );
}
