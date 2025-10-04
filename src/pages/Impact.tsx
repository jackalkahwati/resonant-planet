import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Telescope, Cpu, GraduationCap, Users, Lightbulb, Target } from "lucide-react";

const Impact = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary/20 mb-4">
          <Target className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-4xl font-bold mb-2">Impact & Vision</h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          How Resonant Exoplanets advances exoplanet science, technology, and public engagement
        </p>
      </div>

      <div className="max-w-4xl mx-auto space-y-6">
        {/* Scientific Impact */}
        <Card className="border-2 border-primary/30">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="bg-primary/20 rounded-full p-3">
                <Telescope className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-2xl">Scientific Impact</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Advancing exoplanet detection and validation
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="font-semibold text-primary">Detection Improvements</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Better sensitivity:</strong> Detect shallow transits that classic pipelines miss,
                      especially long-period planets in habitable zones
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Reduced false positives:</strong> Physics validation catches eclipsing binaries
                      and instrumental artifacts that fool SNR-based methods
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Transparent confidence:</strong> Bootstrap uncertainty quantification shows
                      reliability of each detection
                    </span>
                  </li>
                </ul>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold text-primary">Research Applications</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Archive reanalysis:</strong> Discover missed candidates in Kepler, K2, and TESS archives
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Follow-up prioritization:</strong> Confidence scores and validation tests guide telescope time allocation
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Comparative planetology:</strong> Robust detection enables statistical studies of planetary populations
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            <Card className="bg-muted/50 border-none">
              <CardContent className="pt-4">
                <div className="flex items-start gap-3">
                  <Badge className="mt-1">Case Study</Badge>
                  <p className="text-sm text-muted-foreground">
                    <strong className="text-foreground">Kepler-452b detection:</strong> Our system confidently
                    validated this Earth cousin with 91% probability despite its long period (385 days) and shallow
                    depth (0.3%). Classic pipeline flagged it at only 52% confidence due to insufficient data coverage,
                    requiring extensive manual vetting.
                  </p>
                </div>
              </CardContent>
            </Card>
          </CardContent>
        </Card>

        {/* Technical Impact */}
        <Card className="border-2 border-primary/30">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="bg-primary/20 rounded-full p-3">
                <Cpu className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-2xl">Technical Innovation</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  AI + physics + explainability architecture
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="font-semibold text-primary">Architecture Innovations</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Physics-informed ML:</strong> Neural network learns astrophysics constraints rather
                      than pure pattern matching
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Multi-stage validation:</strong> Automated tests replicate expert astronomer vetting
                      at scale
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Interpretable AI:</strong> Saliency maps and attention weights show what the model
                      sees in the data
                    </span>
                  </li>
                </ul>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold text-primary">Technical Benefits</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Scalability:</strong> Process millions of light curves faster than human review
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Reproducibility:</strong> Documented pipeline enables consistent reanalysis
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Extensibility:</strong> Framework adapts to future missions (Roman, PLATO)
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            <Card className="bg-muted/50 border-none">
              <CardContent className="pt-4">
                <div className="flex items-start gap-3">
                  <Lightbulb className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-muted-foreground">
                    <strong className="text-foreground">Key Innovation:</strong> Unlike black-box ML systems,
                    every Resonant detection includes a human-readable explanation grounded in physics. This bridges
                    the gap between AI speed and scientific rigor.
                  </p>
                </div>
              </CardContent>
            </Card>
          </CardContent>
        </Card>

        {/* Educational Impact */}
        <Card className="border-2 border-primary/30">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="bg-primary/20 rounded-full p-3">
                <GraduationCap className="h-6 w-6 text-primary" />
              </div>
              <div>
                <CardTitle className="text-2xl">Educational Impact</CardTitle>
                <p className="text-sm text-muted-foreground mt-1">
                  Making exoplanet science accessible
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-3">
                <h4 className="font-semibold text-primary">Learning Opportunities</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Interactive exploration:</strong> Students see real NASA data and understand
                      detection methods through hands-on experience
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Physics explanations:</strong> Rationale callouts teach concepts like odd/even tests
                      and secondary eclipses in context
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Scientific method:</strong> Validation workflow demonstrates hypothesis testing and
                      false positive screening
                    </span>
                  </li>
                </ul>
              </div>

              <div className="space-y-3">
                <h4 className="font-semibold text-primary">Audience Reach</h4>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Undergraduate courses:</strong> Astronomy labs can use the platform for transit
                      detection assignments
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Citizen science:</strong> Amateur astronomers can validate their own observations
                    </span>
                  </li>
                  <li className="flex gap-2">
                    <span className="text-primary font-bold">•</span>
                    <span>
                      <strong>Public outreach:</strong> Intuitive UI and storytelling make discoveries accessible
                      to general audiences
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            <Card className="bg-muted/50 border-none">
              <CardContent className="pt-4">
                <div className="flex items-start gap-3">
                  <Users className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                  <p className="text-sm text-muted-foreground">
                    <strong className="text-foreground">Outreach Vision:</strong> "Help us discover the next
                    Kepler-22b" - By making sophisticated detection tools accessible, we empower the next generation
                    of scientists and inspire curiosity about worlds beyond our solar system.
                  </p>
                </div>
              </CardContent>
            </Card>
          </CardContent>
        </Card>

        {/* Future Vision */}
        <Card className="bg-gradient-cosmic border-2 border-primary">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Future Vision</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="text-center space-y-2">
                <div className="bg-primary/20 rounded-full w-12 h-12 flex items-center justify-center mx-auto">
                  <Telescope className="h-6 w-6 text-primary" />
                </div>
                <h4 className="font-semibold">Mission Integration</h4>
                <p className="text-sm text-muted-foreground">
                  Deploy in NASA mission operations for real-time candidate screening
                </p>
              </div>

              <div className="text-center space-y-2">
                <div className="bg-primary/20 rounded-full w-12 h-12 flex items-center justify-center mx-auto">
                  <Cpu className="h-6 w-6 text-primary" />
                </div>
                <h4 className="font-semibold">Enhanced AI</h4>
                <p className="text-sm text-muted-foreground">
                  Incorporate reinforcement learning for adaptive validation thresholds
                </p>
              </div>

              <div className="text-center space-y-2">
                <div className="bg-primary/20 rounded-full w-12 h-12 flex items-center justify-center mx-auto">
                  <GraduationCap className="h-6 w-6 text-primary" />
                </div>
                <h4 className="font-semibold">Open Platform</h4>
                <p className="text-sm text-muted-foreground">
                  Build community of contributors for continuous improvement
                </p>
              </div>
            </div>

            <div className="text-center pt-4 border-t border-border">
              <p className="text-sm text-muted-foreground">
                <strong className="text-foreground">Our Goal:</strong> Make exoplanet detection as reliable,
                transparent, and accessible as possible - accelerating the search for worlds beyond our own
                while maintaining scientific integrity.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Impact;
