import { SignUp } from "@clerk/nextjs";

export default function SignUpPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-800">
      <SignUp
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
