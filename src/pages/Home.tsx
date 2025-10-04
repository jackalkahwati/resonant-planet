import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Telescope, Database, Brain, TrendingUp, Download, Rocket } from "lucide-react";
import { StorytellingWalkthrough } from "@/components/StorytellingWalkthrough";
import heroImage from "@/assets/hero-exoplanet.jpg";

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-space" />
        <div
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `url(${heroImage})`,
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        />
        <div className="relative container mx-auto px-4 py-24 md:py-32">
          <div className="max-w-3xl animate-fade-in">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 text-balance">
              Find new worlds with{" "}
              <span className="text-primary">physics-first AI</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 text-balance">
              Detect exoplanet transits with scientific rigor, understand model decisions with
              transparent explainability, and validate candidates with proven physics checks.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/detect">
                <Button variant="hero" size="lg">
                  <Telescope className="h-5 w-5" />
                  Try a Demo
                </Button>
              </Link>
              <Link to="/detect">
                <Button variant="secondary" size="lg">
                  <Database className="h-5 w-5" />
                  Upload Data
                </Button>
              </Link>
              <Link to="/about">
                <Button variant="outline" size="lg">
                  Learn the Method
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="grid md:grid-cols-3 gap-6">
          <Card className="bg-card border-border hover:border-primary/50 transition-colors">
            <CardHeader>
              <Database className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Data Sources</CardTitle>
              <CardDescription>
                Access Kepler, K2, and TESS light curves with instant search and upload capabilities
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li>• Public NASA mission archives</li>
                <li>• Custom data upload support</li>
                <li>• Automated preprocessing</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-card border-border hover:border-primary/50 transition-colors">
            <CardHeader>
              <Brain className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Physics-First Detection</CardTitle>
              <CardDescription>
                AI-powered transit detection with built-in astrophysics validation checks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li>• Deep learning inference</li>
                <li>• BLS periodogram analysis</li>
                <li>• False positive screening</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-card border-border hover:border-primary/50 transition-colors">
            <CardHeader>
              <TrendingUp className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Transparent Explainability</CardTitle>
              <CardDescription>
                Understand every detection with phase-folded curves, saliency maps, and quality metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li>• Phase-folded visualizations</li>
                <li>• Odd vs even transit checks</li>
                <li>• Secondary eclipse analysis</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Method Overview */}
      <section className="bg-gradient-data py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Method Overview</h2>
            <p className="text-lg text-muted-foreground mb-8">
              Our approach combines state-of-the-art deep learning with rigorous astrophysics validation.
              Every candidate is subjected to multiple independent tests to rule out false positives.
            </p>
            <div className="grid md:grid-cols-2 gap-6 text-left">
              <div className="bg-card/50 backdrop-blur border border-border rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-3 text-primary">Detection Pipeline</h3>
                <ol className="text-sm text-muted-foreground space-y-2">
                  <li>1. Light curve preprocessing and normalization</li>
                  <li>2. Neural network transit probability inference</li>
                  <li>3. Box-fitting Least Squares period search</li>
                  <li>4. Phase-fold and model fit</li>
                </ol>
              </div>
              <div className="bg-card/50 backdrop-blur border border-border rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-3 text-primary">Validation Tests</h3>
                <ol className="text-sm text-muted-foreground space-y-2">
                  <li>1. Odd vs even transit depth consistency</li>
                  <li>2. Secondary eclipse presence check</li>
                  <li>3. Transit shape vs V-shape test</li>
                  <li>4. Centroid shift analysis proxy</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Storytelling Walkthrough */}
      <section className="container mx-auto px-4 py-8">
        <StorytellingWalkthrough />
      </section>

      {/* Why This Matters */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <Rocket className="h-12 w-12 text-primary mx-auto mb-4" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Why This Matters</h2>
            <p className="text-lg text-muted-foreground">
              Advancing exoplanet science through better detection and validation
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            <Card className="bg-card border-border">
              <CardHeader>
                <Telescope className="h-8 w-8 text-primary mb-2" />
                <CardTitle className="text-lg">Scientific Impact</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Detect planets classic pipelines miss, reduce false positives, and validate candidates with confidence
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardHeader>
                <Brain className="h-8 w-8 text-primary mb-2" />
                <CardTitle className="text-lg">Technical Innovation</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Physics-informed AI with transparent explainability and reproducible analysis pipelines
              </CardContent>
            </Card>
            <Card className="bg-card border-border">
              <CardHeader>
                <TrendingUp className="h-8 w-8 text-primary mb-2" />
                <CardTitle className="text-lg">Educational Value</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                Make sophisticated detection accessible to students, researchers, and the curious public
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      <section className="bg-gradient-cosmic py-16 md:py-24">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Discover?</h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Start exploring exoplanet candidates with pre-loaded demo data. See the difference
            physics-first validation makes in under 10 seconds.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/detect">
              <Button variant="hero" size="lg">
                <Telescope className="h-5 w-5" />
                Try Demo Detection
              </Button>
            </Link>
            <Link to="/impact">
              <Button variant="outline" size="lg">
                <Rocket className="h-5 w-5" />
                View Impact
              </Button>
            </Link>
            <Button variant="secondary" size="lg">
              <Download className="h-5 w-5" />
              Download Reports
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
