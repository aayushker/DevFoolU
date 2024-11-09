import Footer from "@/app/components/Footer";
import Project from "@/app/components/Project";
import NavBar from "@/app/components/NavBar";
import "@/app/globals.css";

const index = () => {
  return (
    <div className="">
      <header className="">
        <NavBar />
      </header>
      <main>
        <Project />
      </main>
      <footer className="">
        <Footer />
      </footer>
    </div>
  );
};

export default index;
