import Footer from "@/app/components/Footer";
import Hero from "@/app/components/Hero";
import NavBar from "@/app/components/NavBar";
import "@/app/globals.css";

const index = () => {
  return (
    <>
      <header className="">
        <NavBar />
      </header>
      <main>
        <Hero />
      </main>
      <footer className="">
        <Footer />
      </footer>
    </>
  );
};

export default index;
