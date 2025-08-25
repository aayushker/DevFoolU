import { UserButton, useUser } from "@clerk/nextjs";
import { motion } from "framer-motion";

export default function UserProfile() {
  const { isSignedIn, user } = useUser();

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-4"
    >
     
    </motion.div>
  );
}
