import Navbar from "@/components/Navbar";
import Hero49 from "@/components/originkit/hero-49";
import FeatureCards from "@/components/FeatureCards";
import SystemFacts from "@/components/SystemFacts";
import ConditionCards from "@/components/ConditionCards";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <main className="flex-grow">
      <Navbar />
      <Hero49 />
      <FeatureCards />
      <SystemFacts />
      <ConditionCards />
      <Footer />
    </main>
  );
}
