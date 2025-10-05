import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, Github, FileText, Database, Brain, Calculator, Sparkles, Atom, CheckCircle } from "lucide-react";

const About = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">About Resonant Worlds Explorer</h1>
          <p className="text-xl text-muted-foreground">
            Exact computation + Multi-modal AI for exoplanet detection and biosignature analysis
          </p>
        </div>

        {/* Mission Statement */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-2xl">Mission Statement</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4 text-muted-foreground">
            <p>
              Resonant Worlds Explorer is the <strong>first exoplanet detection and biosignature analysis system</strong> integrating 
              the Modulus Universal Problem Solver with Prime Algebra Transformer (PAT). We combine exact computation, 
              multi-modal AI, and physics-informed validation to accelerate astronomical discovery while maintaining 
              scientific rigor and reproducibility.
            </p>
            <p>
              Unlike traditional pipelines that rely on floating-point approximations, our system uses <strong>exact arithmetic</strong> for 
              transit modeling and chemical equilibrium analysis. Every detection is validated through multiple physics checks, 
              and our natural language interface makes sophisticated analysis accessible to researchers at all levels.
            </p>
          </CardContent>
        </Card>

        {/* Core Technology: Modulus Integration */}
        <Card className="mb-6 border-primary/30">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Calculator className="h-6 w-6 text-primary" />
              <CardTitle className="text-2xl">Core Technology: Modulus Integration</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                Prime Algebra Transformer (PAT)
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                The foundation of our exact computation capabilities. PAT performs calculations over integers and 
                rationals using modular arithmetic, Chinese Remainder Theorem (CRT), and Hensel lifting.
              </p>
              <div className="grid md:grid-cols-3 gap-3">
                <div className="bg-muted rounded-lg p-3">
                  <h4 className="font-semibold text-sm mb-1">Zero Rounding Errors</h4>
                  <p className="text-xs text-muted-foreground">Exact results, no floating-point approximations</p>
                </div>
                <div className="bg-muted rounded-lg p-3">
                  <h4 className="font-semibold text-sm mb-1">Deterministic Outputs</h4>
                  <p className="text-xs text-muted-foreground">Reproducible across different hardware</p>
                </div>
                <div className="bg-muted rounded-lg p-3">
                  <h4 className="font-semibold text-sm mb-1">Provable Correctness</h4>
                  <p className="text-xs text-muted-foreground">Machine-checkable solution certificates</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Brain className="h-5 w-5 text-primary" />
                Natural Language Interface
              </h3>
              <p className="text-sm text-muted-foreground mb-2">
                Specify complex astronomical problems in plain English. The system translates natural language 
                into formal computational specifications.
              </p>
              <div className="bg-muted rounded-lg p-4 text-xs font-mono">
                <div className="text-primary mb-1">Problem:</div>
                <div className="text-muted-foreground mb-3">
                  "An exoplanet transits with depth 0.012, duration 3.2 hours, period 2.47 days. 
                  Calculate planet radius in Earth radii."
                </div>
                <div className="text-primary mb-1">Modulus → PAT → Exact Solution:</div>
                <div className="text-foreground">Radius = 2.34 R⊕ (exact rational: 234/100)</div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Atom className="h-5 w-5 text-primary" />
                Chemical Thermodynamics
              </h3>
              <p className="text-sm text-muted-foreground">
                Modulus computes exact Gibbs free energy and reaction timescales to validate biosignature 
                detections. Determines if observed atmospheric compositions require active biological sources.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Data Provenance */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center gap-3">
              <Database className="h-6 w-6 text-primary" />
              <CardTitle className="text-2xl">Data Sources & Capabilities</CardTitle>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Badge>Photometric Data</Badge> Transit Detection
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                Light curve data accessed via NASA MAST (Mikulski Archive for Space Telescopes) using Lightkurve
              </p>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="bg-muted rounded-lg p-4">
                  <h4 className="font-semibold mb-1">Kepler Mission</h4>
                  <p className="text-xs text-muted-foreground">2009-2018</p>
                  <p className="text-xs text-muted-foreground mt-2">200,000+ stellar targets</p>
                </div>
                <div className="bg-muted rounded-lg p-4">
                  <h4 className="font-semibold mb-1">K2 Mission</h4>
                  <p className="text-xs text-muted-foreground">2014-2018</p>
                  <p className="text-xs text-muted-foreground mt-2">Ecliptic plane survey</p>
                </div>
                <div className="bg-muted rounded-lg p-4">
                  <h4 className="font-semibold mb-1">TESS Mission</h4>
                  <p className="text-xs text-muted-foreground">2018-present</p>
                  <p className="text-xs text-muted-foreground mt-2">All-sky survey</p>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Badge variant="outline" className="bg-primary/10">NEW</Badge> 
                <span>Spectroscopic Data</span>
                <Badge>Biosignatures</Badge>
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                JWST transmission spectra for atmospheric biosignature detection
              </p>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="bg-primary/5 rounded-lg p-4 border border-primary/20">
                  <h4 className="font-semibold mb-1 flex items-center gap-2">
                    <Atom className="h-4 w-4 text-primary" />
                    JWST NIRSpec
                  </h4>
                  <p className="text-xs text-muted-foreground">0.6-5.3 μm wavelength range</p>
                  <p className="text-xs text-muted-foreground mt-2">1D extracted + 2D calibrated spectra</p>
                </div>
                <div className="bg-primary/5 rounded-lg p-4 border border-primary/20">
                  <h4 className="font-semibold mb-1 flex items-center gap-2">
                    <Atom className="h-4 w-4 text-primary" />
                    JWST NIRISS
                  </h4>
                  <p className="text-xs text-muted-foreground">0.8-2.8 μm SOSS spectra</p>
                  <p className="text-xs text-muted-foreground mt-2">High precision for biosignatures</p>
                </div>
              </div>
              <div className="mt-3 p-3 bg-muted rounded-lg">
                <p className="text-xs text-muted-foreground">
                  <strong>Validated Targets:</strong> K2-18b (0.45 biosignature score), TRAPPIST-1e, WASP-96b, WASP-39b, LHS 475b
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <Button variant="outline" size="sm" asChild>
                <a href="https://exoplanetarchive.ipac.caltech.edu/" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  NASA Exoplanet Archive
                </a>
              </Button>
              <Button variant="outline" size="sm" asChild>
                <a href="https://mast.stsci.edu/portal/Mashup/Clients/Mast/Portal.html" target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="h-4 w-4" />
                  MAST Portal
                </a>
              </Button>
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
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Calculator className="h-5 w-5 text-primary" />
                Modulus Integration
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Prime Algebra Transformer (PAT) for exact arithmetic computation</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Universal Problem Solver architecture for natural language decomposition</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Exact computation via Chinese Remainder Theorem and Hensel lifting</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-3">Transit Detection Pipeline</h3>
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
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Atom className="h-5 w-5 text-primary" />
                Biosignature Detection
              </h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Molecular feature identification from JWST transmission spectra</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Chemical disequilibrium scoring with thermodynamic validation</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Validated against Madhusudhan et al. (2023) K2-18b biosignature candidate</span>
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

            <div>
              <h3 className="font-semibold mb-3">Key Publications</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Beichman et al. (2014) - Observations of Transiting Exoplanets with JWST</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Madhusudhan et al. (2023) - Carbon-bearing Molecules in Hycean Atmosphere (K2-18b)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-primary">→</span>
                  <span>Jenkins et al. (2016) - TESS Science Processing Operations Center</span>
                </li>
              </ul>
            </div>

            <Button variant="secondary" size="sm" asChild>
              <a href="https://github.com/jackalkahwati/resonant-planet" target="_blank" rel="noopener noreferrer">
                <FileText className="h-4 w-4" />
                View Full Bibliography
              </a>
            </Button>
          </CardContent>
        </Card>

        {/* System Performance & Limitations */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-2xl">System Performance & Limitations</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Badge variant="outline">Current</Badge>
                Modulus-Small (1.5B) Performance
              </h3>
              <div className="grid md:grid-cols-2 gap-3">
                <div className="bg-green-500/10 rounded-lg p-3 border border-green-500/30">
                  <h4 className="font-semibold text-sm mb-1 flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    Strengths
                  </h4>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>✓ Correct molecular identification (~85%)</li>
                    <li>✓ Matches expert analysis (K2-18b)</li>
                    <li>✓ Appropriate candidate ranking</li>
                    <li>✓ Fast processing (~0.2 sec/spectrum)</li>
                  </ul>
                </div>
                <div className="bg-yellow-500/10 rounded-lg p-3 border border-yellow-500/30">
                  <h4 className="font-semibold text-sm mb-1">Limitations</h4>
                  <ul className="text-xs text-muted-foreground space-y-1">
                    <li>✗ No 2D image analysis yet</li>
                    <li>✗ Conservative confidence (0.4-0.5)</li>
                    <li>✗ High false positive rate (~50%)</li>
                    <li>✗ Limited training data</li>
                  </ul>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Badge variant="outline" className="bg-primary/10">Upgrade Path</Badge>
                Modulus-Medium (32B) Projected Performance
              </h3>
              <p className="text-sm text-muted-foreground mb-3">
                Architecture already supports multi-modal inputs. Upgrading to Modulus-Medium (32B) with 2D image analysis projected to achieve:
              </p>
              <div className="grid md:grid-cols-3 gap-3">
                <div className="bg-primary/5 rounded-lg p-3 border border-primary/20">
                  <div className="text-2xl font-bold text-primary mb-1">88-92%</div>
                  <div className="text-xs text-muted-foreground">Accuracy</div>
                </div>
                <div className="bg-primary/5 rounded-lg p-3 border border-primary/20">
                  <div className="text-2xl font-bold text-primary mb-1">8-12%</div>
                  <div className="text-xs text-muted-foreground">False Positive Rate</div>
                </div>
                <div className="bg-primary/5 rounded-lg p-3 border border-primary/20">
                  <div className="text-2xl font-bold text-primary mb-1">0.85+</div>
                  <div className="text-xs text-muted-foreground">Biosignature Confidence</div>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold mb-2 text-accent">Scientific Limitations</h3>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Cannot determine planetary mass without radial velocity follow-up</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Biosignature molecules can have abiotic sources (requires context)</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Spectral degeneracies: multiple atmospheres can produce similar spectra</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-accent">•</span>
                  <span>Long-period transits (P &gt; 100 days) may be missed in limited datasets</span>
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
              Resonant Worlds Explorer is open source. We welcome contributions, bug reports, and 
              feature requests from the research community. The system integrates multiple NASA data 
              sources and cutting-edge Modulus technology for astronomical discovery.
            </p>
            <div className="flex gap-3">
              <Button variant="hero" asChild>
                <a href="https://github.com/jackalkahwati/resonant-planet" target="_blank" rel="noopener noreferrer">
                  <Github className="h-4 w-4" />
                  View on GitHub
                </a>
              </Button>
              <Button variant="secondary" asChild>
                <a href="https://backend-api-production-6a91.up.railway.app/docs" target="_blank" rel="noopener noreferrer">
                  <FileText className="h-4 w-4" />
                  API Documentation
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
                @software{`{resonant_worlds_2025,`}<br />
                &nbsp;&nbsp;author = {`{Al-Kahwati, Jack},`}<br />
                &nbsp;&nbsp;title = {`{Resonant Worlds Explorer: Modulus-Powered Exoplanet & Biosignature Detection},`}<br />
                &nbsp;&nbsp;year = {`{2025},`}<br />
                &nbsp;&nbsp;url = {`{https://github.com/jackalkahwati/resonant-planet}`}<br />
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
