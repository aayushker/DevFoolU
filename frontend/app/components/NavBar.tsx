import { Button } from "@/app/components/ui/button";
import { Link } from "@nextui-org/react";
// import { SignedIn, SignedOut, UserButton } from "@clerk/clerk-react";

export default function NavBar() {
  return (
    <header className="bg-white shadow-sm">
      <nav className="container mx-auto px-4 py-4 flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold text-blue-900">
          Devfoolio
        </Link>
        <div className="space-x-4 flex items-center">
          <Link href="/" className="text-blue-900 hover:text-blue-700">
            About
          </Link>
          <Link href="/" className="text-blue-900 hover:text-blue-700">
            Contact
          </Link>
          {/* <SignedOut> */}
            <Button variant="outline">Log In</Button>
          {/* </SignedOut>
          <SignedIn>
            <UserButton />
          </SignedIn> */}
        </div>
      </nav>
    </header>
  );
}
