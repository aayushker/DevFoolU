import Footer from "@/app/components/Footer";
import Hero from "@/app/components/Hero";
import NavBar from "@/app/components/NavBar";
import "@/app/globals.css";
import { ClerkProvider } from "@clerk/nextjs";

const index = () => {
  return (
    <ClerkProvider>
      <header className="">
        <NavBar />
      </header>
      <main>
        <Hero />
      </main>
      <footer className="">
        <Footer />
      </footer>
    </ClerkProvider>
  );
};

export default index;