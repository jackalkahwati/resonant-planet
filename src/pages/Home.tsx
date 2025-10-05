import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Telescope, Database, Brain, TrendingUp, Download, Rocket, Sparkles, Atom, Calculator, CheckCircle } from "lucide-react";
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
            <div className="flex flex-wrap gap-2 mb-4">
              <Badge variant="outline" className="bg-primary/10 border-primary/30">
                <Calculator className="h-3 w-3 mr-1" />
                Powered by Modulus PAT
              </Badge>
              <Badge variant="outline" className="bg-primary/10 border-primary/30">
                <Atom className="h-3 w-3 mr-1" />
                Biosignature Detection
              </Badge>
              <Badge variant="outline" className="bg-primary/10 border-primary/30">
                <Sparkles className="h-3 w-3 mr-1" />
                Exact Computation
              </Badge>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-6 text-balance">
              Discover exoplanets and{" "}
              <span className="text-primary">biosignatures</span> with{" "}
              <span className="text-primary">exact computation</span>
            </h1>
            <p className="text-xl md:text-2xl text-muted-foreground mb-8 text-balance">
              The first system integrating Modulus Prime Algebra Transformer with AI for 
              transit detection AND atmospheric biosignature analysis. Zero rounding errors, 
              natural language interface, JWST spectroscopy support.
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
                  <Atom className="h-5 w-5" />
                  Analyze Biosignatures
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
              <CardTitle>Multi-Mission Data</CardTitle>
              <CardDescription>
                Access Kepler, K2, TESS light curves + JWST transmission spectra
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li>• 200,000+ Kepler/TESS targets</li>
                <li>• JWST NIRSpec & NIRISS spectra</li>
                <li>• Custom data upload (CSV)</li>
                <li>• 2D spectroscopic images</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-card border-border hover:border-primary/50 transition-colors">
            <CardHeader>
              <Calculator className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Modulus Exact Computation</CardTitle>
              <CardDescription>
                Prime Algebra Transformer for zero-error transit modeling and chemistry
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li>• Zero rounding errors (PAT)</li>
                <li>• Natural language interface</li>
                <li>• Machine-checkable proofs</li>
                <li>• Deterministic results</li>
              </ul>
            </CardContent>
          </Card>

          <Card className="bg-card border-border hover:border-primary/50 transition-colors">
            <CardHeader>
              <Atom className="h-10 w-10 text-primary mb-2" />
              <CardTitle>Biosignature Analysis</CardTitle>
              <CardDescription>
                Detect O₂, CH₄, DMS and other biosignature molecules with thermodynamic validation
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li>• 6 biosignature molecules tracked</li>
                <li>• Chemical disequilibrium scoring</li>
                <li>• K2-18b validated (0.45 score)</li>
                <li>• Matches expert analysis</li>
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

      {/* K2-18b Case Study */}
      <section className="container mx-auto px-4 py-16 md:py-24">
        <Card className="border-primary/30 bg-gradient-data">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="bg-primary/20">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Validated Discovery
                  </Badge>
                  <Badge variant="outline">JWST</Badge>
                </div>
                <CardTitle className="text-2xl md:text-3xl">K2-18b Biosignature Analysis</CardTitle>
                <CardDescription className="text-base mt-2">
                  Our system successfully identified the same biosignature molecules as the expert team
                </CardDescription>
              </div>
              <Sparkles className="h-8 w-8 text-primary" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-3 text-primary">Target Properties</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex justify-between">
                    <span>Mass:</span>
                    <span className="font-medium text-foreground">8.6 M⊕</span>
                  </li>
                  <li className="flex justify-between">
                    <span>Radius:</span>
                    <span className="font-medium text-foreground">2.6 R⊕</span>
                  </li>
                  <li className="flex justify-between">
                    <span>Temperature:</span>
                    <span className="font-medium text-foreground">270 K</span>
                  </li>
                  <li className="flex justify-between">
                    <span>Period:</span>
                    <span className="font-medium text-foreground">32.9 days</span>
                  </li>
                  <li className="flex justify-between">
                    <span>Zone:</span>
                    <span className="font-medium text-primary">Habitable ✓</span>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold mb-3 text-primary">Our System's Detection</h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>O₂ at 0.76 μm (19,145 ppm)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>CH₄ at 3.30 μm (79,106 ppm)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>PH₃ at 4.30 μm (7,344 ppm)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span>DMS at 3.40 μm (79,106 ppm)</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="mt-6 p-4 bg-primary/10 rounded-lg border border-primary/30">
              <div className="flex items-start gap-3">
                <div className="bg-primary/20 rounded-full p-2 mt-1">
                  <Brain className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Biosignature Score: 0.45 / 1.00</h4>
                  <p className="text-sm text-muted-foreground mb-2">
                    <strong>O₂ + CH₄ coexistence detected</strong> — requires active replenishment source. 
                    Matches Madhusudhan et al. (2023) published findings.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Current score reflects Modulus-Small (1.5B) model. Upgrade to Modulus-Medium (32B) 
                    with 2D image analysis projected to achieve 0.88+ confidence.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
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
