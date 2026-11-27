import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import FeatureCards from "@/components/FeatureCards";
import ConditionCards from "@/components/ConditionCards";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="flex-grow">
      <Navbar />
      <Hero />
      <FeatureCards />
      <ConditionCards />
      <Footer />
    </main>
  );
}
