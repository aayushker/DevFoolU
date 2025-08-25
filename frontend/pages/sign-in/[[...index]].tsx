import { SignIn } from "@clerk/nextjs";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-800">
      <SignIn
        fallbackRedirectUrl="/project"
        appearance={{
          elements: {
            formButtonPrimary: "bg-blue-900 hover:bg-blue-800",
            footerActionLink: "text-blue-900 hover:text-blue-800",
          },
        }}
      />
    </div>
  );
}
