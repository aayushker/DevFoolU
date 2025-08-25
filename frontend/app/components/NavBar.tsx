import { Button } from "@/app/components/ui/button";
import { Link } from "@nextui-org/react";
import { useUser, UserButton } from "@clerk/nextjs";

export default function NavBar() {
  const { isSignedIn, user } = useUser();

  return (
    <header className="bg-white shadow-sm">
      <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-blue-900">
          DevFoolU
        </Link>
        <div className="space-x-4 flex items-center">
          <Link href="/" className="text-blue-900 hover:text-blue-700">
            About
          </Link>
          <Link href="/" className="text-blue-900 hover:text-blue-700">
            Contact
          </Link>
          <Link href="/" className="text-blue-900 hover:text-blue-700">
            Results
          </Link>
        </div>
        <div>
          {!isSignedIn && !user && (
            <>
              <div className="flex gap-4">
                <Button
                  className="bg-white text-blue-900 hover:bg-blue-100"
                  onClick={() => (window.location.href = "/sign-in")}
                >
                  Sign In
                </Button>
                <Button
                  className="bg-white text-blue-900 hover:bg-blue-100"
                  onClick={() => (window.location.href = "/sign-up")}
                >
                  Sign Up
                </Button>
              </div>
            </>
          )}
          {isSignedIn && user && (
            <>
              <div className="flex items-center gap-4">
                <div className="text-right">
                  <p className="text-sm text-black">Welcome,</p>
                  <p className="font-medium text-black">
                    {user.firstName || user.username || "User"}
                  </p>
                </div>
                <UserButton
                  appearance={{
                    elements: {
                      userButtonAvatarBox: "w-10 h-10",
                    },
                  }}
                />
              </div>
            </>
          )}
        </div>
      </nav>
    </header>
  );
}
