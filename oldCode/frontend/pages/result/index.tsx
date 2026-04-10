import Footer from "@/app/components/Footer";
import Result from "@/app/components/Result";
import NavBar from "@/app/components/NavBar";
import "@/app/globals.css";

const index = () => {
  return (
    <div className="">
      <header className="">
        <NavBar />
      </header>
      <main>
        <Result />
      </main>
      <footer className="">
        <Footer />
      </footer>
    </div>
  );
};

export default index;
