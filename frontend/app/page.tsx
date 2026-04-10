import Navbar from "@/components/navbar"
import Footer from "@/components/footer"
import HeroSection from "@/components/hero-section"
import StatsSection from "@/components/stats-section"
import HowItWorks from "@/components/how-it-works"
import FeaturesSection from "@/components/features-section"
import CTA from "@/components/cta-section"

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1">
        <HeroSection />
        <StatsSection />
        <FeaturesSection />
        <HowItWorks />
        <CTA />
      </main>
      <Footer />
    </div>
  )
}
