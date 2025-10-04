import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Share2, Printer } from "lucide-react";
import { toast } from "sonner";

const Report = () => {
  const handleExport = (format: string) => {
    toast.success(`Exporting report as ${format}...`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Generate Report</h1>
        <p className="text-muted-foreground">
          Create exportable reports with plots, metrics, and scientific narrative
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Report Preview</CardTitle>
              <CardDescription>Candidate KIC 8462852 Analysis Report</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Title Section */}
              <div className="border-b border-border pb-6">
                <h2 className="text-2xl font-bold mb-2">Exoplanet Transit Detection Report</h2>
                <div className="flex items-center gap-2 mb-4">
                  <Badge>High Confidence</Badge>
                  <Badge variant="outline">Validated</Badge>
                </div>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Target ID</p>
                    <p className="font-semibold">KIC 8462852</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Analysis Date</p>
                    <p className="font-semibold">2025-01-15</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Mission</p>
                    <p className="font-semibold">Kepler</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Detection Probability</p>
                    <p className="font-semibold">0.94</p>
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Executive Summary</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Analysis of light curve data from KIC 8462852 reveals a high-confidence exoplanet transit
                  candidate with probability 0.94. The signal exhibits a periodic transit depth of 1.2% with
                  period 3.52 days, consistent with a planetary companion. Multiple validation checks including
                  odd/even transit comparison, secondary eclipse search, and shape analysis support the
                  planetary hypothesis and rule out common false positive scenarios.
                </p>
              </div>

              {/* Key Metrics */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Key Metrics</h3>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-xs text-muted-foreground mb-1">Orbital Period</p>
                    <p className="text-2xl font-bold">3.52 days</p>
                  </div>
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-xs text-muted-foreground mb-1">Transit Depth</p>
                    <p className="text-2xl font-bold">1.2%</p>
                  </div>
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-xs text-muted-foreground mb-1">Signal-to-Noise</p>
                    <p className="text-2xl font-bold">12.4</p>
                  </div>
                </div>
              </div>

              {/* Validation Results */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Validation Tests</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Odd vs Even Transit Depth</span>
                    <Badge>Pass</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Secondary Eclipse Search</span>
                    <Badge>Pass</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Transit Shape Analysis</span>
                    <Badge>Pass</Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Centroid Motion Check</span>
                    <Badge>Pass</Badge>
                  </div>
                </div>
              </div>

              {/* Method Summary */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Method Summary</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Detection employed a physics-informed neural network trained on validated Kepler transits,
                  followed by Box-fitting Least Squares period search and phase-folding analysis. All
                  candidates undergo systematic vetting including odd-even transit comparison to detect
                  eclipsing binaries, secondary eclipse search to identify stellar companions, and shape
                  analysis to distinguish planetary transits from grazing binary eclipses.
                </p>
              </div>

              {/* Limitations */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Limitations & Uncertainties</h3>
                <ul className="text-sm text-muted-foreground space-y-2">
                  <li>• Confidence reflects bootstrap uncertainty across light curve segments</li>
                  <li>• Follow-up spectroscopy recommended for mass determination</li>
                  <li>• Centroid analysis based on proxy metrics pending pixel-level validation</li>
                  <li>• Period uncertainty: ±0.02 days based on BLS search window</li>
                </ul>
              </div>

              {/* Next Steps */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Recommended Next Steps</h3>
                <ol className="text-sm text-muted-foreground space-y-2">
                  <li>1. Schedule follow-up radial velocity observations for mass confirmation</li>
                  <li>2. Obtain high-resolution imaging to rule out nearby stellar companions</li>
                  <li>3. Submit to TESS observing program for additional transit coverage</li>
                  <li>4. Include in comparative study of short-period planetary systems</li>
                </ol>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Export Options */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Export Options</CardTitle>
              <CardDescription>Download report in various formats</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button 
                className="w-full" 
                variant="hero"
                onClick={() => handleExport('PDF')}
              >
                <Download className="h-4 w-4" />
                Export as PDF
              </Button>
              <Button 
                className="w-full" 
                variant="secondary"
                onClick={() => handleExport('CSV')}
              >
                <FileText className="h-4 w-4" />
                Export Data (CSV)
              </Button>
              <Button 
                className="w-full" 
                variant="outline"
                onClick={() => handleExport('slides')}
              >
                <Share2 className="h-4 w-4" />
                Generate Slides
              </Button>
              <Button 
                className="w-full" 
                variant="outline"
                onClick={() => window.print()}
              >
                <Printer className="h-4 w-4" />
                Print Report
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Report Contents</CardTitle>
            </CardHeader>
            <CardContent className="text-sm space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Candidate Summary</span>
                <span className="text-primary">✓</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Phase-Folded Curve</span>
                <span className="text-primary">✓</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">BLS Periodogram</span>
                <span className="text-primary">✓</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Validation Results</span>
                <span className="text-primary">✓</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Method Documentation</span>
                <span className="text-primary">✓</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Limitations</span>
                <span className="text-primary">✓</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Citation</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground font-mono leading-relaxed">
                Resonant Exoplanets Detection Pipeline v1.0, NASA Space Apps Challenge 2025.
                Available at: github.com/resonant-exoplanets
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Report;
