import { UserButton, useUser } from "@clerk/nextjs";
import { Button } from "@/app/components/ui/button";
import { motion } from "framer-motion";

export default function UserProfile() {
  const { isSignedIn, user } = useUser();

  if (!isSignedIn) {
    return (
      <div className="flex gap-4">
        <Button
          variant="outline"
          className="text-white border-white hover:bg-white hover:text-blue-900"
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
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-4"
    >
      {isSignedIn && user && (
        <>
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
        </>
      )}
    </motion.div>
  );
}
