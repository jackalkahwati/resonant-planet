import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, Github, FileText, Database, Brain } from "lucide-react";

const About = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">About Resonant Exoplanets</h1>
          <p className="text-xl text-muted-foreground">
            Physics-first AI for exoplanet transit detection with transparent explainability
          </p>
        </div>

        {/* Mission Statement */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-2xl">Mission Statement</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-muted-foreground">
            <p>
              Resonant Exoplanets combines state-of-the-art deep learning with rigorous astrophysics validation
              to accelerate exoplanet discovery while maintaining scientific credibility. Our platform makes
              sophisticated transit detection accessible to researchers, educators, and enthusiasts through
              transparent explainability and reproducible analysis pipelines.
            </p>
            <p>
              Every detection is subjected to multiple independent physics checks that systematically rule out
              common false positive scenarios. We believe that AI-powered discovery tools must be interpretable,
              scientifically sound, and openly documented to earn the trust of the astronomical community.
            </p>
          </CardContent>
        </Card>

        {/* Data Provenance */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Database className="h-6 w-6 text-primary" />
              <CardTitle className="text-2xl">Data Provenance</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2 flex items-center gap-2">
                <Badge>Source</Badge> NASA Exoplanet Archive
              </h3>
              <p className="text-sm text-muted-foreground mb-2">
                Light curve data accessed via MAST (Mikulski Archive for Space Telescopes)
              </p>
              <Button variant="outline" size="sm" asChild>
                <a href="https://exoplanetarchive.ipac.caltech.edu/" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  Visit Archive
                </a>
              </Button>
            </div>

            <div className="grid md:grid-cols-3 gap-4 mt-4">
              <div className="bg-muted rounded-lg p-4">
                <h4 className="font-semibold mb-1">Kepler Mission</h4>
                <p className="text-xs text-muted-foreground">2009-2018</p>
                <p className="text-xs text-muted-foreground mt-2">150,000+ stars monitored</p>
              </div>
              <div className="bg-muted rounded-lg p-4">
                <h4 className="font-semibold mb-1">K2 Mission</h4>
                <p className="text-xs text-muted-foreground">2014-2018</p>
                <p className="text-xs text-muted-foreground mt-2">500,000+ light curves</p>
              </div>
              <div className="bg-muted rounded-lg p-4">
                <h4 className="font-semibold mb-1">TESS Mission</h4>
                <p className="text-xs text-muted-foreground">2018-present</p>
                <p className="text-xs text-muted-foreground mt-2">200M+ stars surveyed</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Method References */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Brain className="h-6 w-6 text-primary" />
              <CardTitle className="text-2xl">Method & References</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-3">Detection Pipeline</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Neural network architecture inspired by Shallue & Vanderburg (2018) AstroNet</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Box-fitting Least Squares (BLS) implementation following Kovács et al. (2002)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Light curve preprocessing based on Kepler Science Data Processing Pipeline</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-3">Validation Tests</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Odd-even depth test adapted from Desort et al. (2009)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Secondary eclipse methodology from Torres et al. (2011)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Transit shape analysis following Seager & Mallén-Ornelas (2003)</span>
                </li>
              </ul>
            </div>

            <Button variant="secondary" size="sm" asChild>
              <a href="https://github.com/resonant-exoplanets" target="_blank" rel="noopener noreferrer">
                <FileText className="h-4 w-4" />
                View Full Bibliography
              </a>
            </Button>
          </CardContent>
        </Card>

        {/* Assumptions & Limitations */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-2xl">Assumptions & Limitations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-2 text-accent">Key Assumptions</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Light curves have been corrected for systematic trends and outliers</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Target stars are single (not in tight binary systems)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Transit signals are strictly periodic</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Centroid analysis serves as proxy pending pixel-level validation</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-2 text-accent">Known Limitations</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Cannot determine planetary mass without radial velocity follow-up</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Long-period transits (P &gt; 100 days) may be missed in limited datasets</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>High-eccentricity orbits may yield incorrect period estimates</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Grazing transits with low SNR require manual vetting</span>
                </li>
              </ul>
            </div>
          </CardContent>
        </Card>

        {/* Open Source */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Github className="h-6 w-6 text-primary" />
              <CardTitle className="text-2xl">Open Source</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Resonant Exoplanets is open source and built for the NASA Space Apps Challenge 2025.
              We welcome contributions, bug reports, and feature requests from the community.
            </p>
            <div className="flex gap-3">
              <Button variant="hero" asChild>
                <a href="https://github.com/resonant-exoplanets" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4" />
                  View on GitHub
                </a>
              </Button>
              <Button variant="secondary" asChild>
                <a href="https://github.com/resonant-exoplanets/docs" target="_blank" rel="noopener noreferrer">
                  <FileText className="h-4 w-4" />
                  Documentation
                </a>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* License */}
        <Card>
          <CardHeader>
            <CardTitle>License & Citation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <Badge variant="outline">MIT License</Badge>
              <p className="text-sm text-muted-foreground mt-2">
                Free to use, modify, and distribute with attribution
              </p>
            </div>
            <div className="bg-muted rounded-lg p-4">
              <p className="text-xs font-mono text-muted-foreground leading-relaxed">
                @software{`{resonant_exoplanets_2025,`}<br />
                &nbsp;&nbsp;author = {`{Resonant Exoplanets Team},`}<br />
                &nbsp;&nbsp;title = {`{Resonant Exoplanets: Physics-First AI for Transit Detection},`}<br />
                &nbsp;&nbsp;year = {`{2025},`}<br />
                &nbsp;&nbsp;url = {`{https://github.com/resonant-exoplanets}`}<br />
                {`}`}
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default About;
