import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Download, FileText, Share2, Printer } from "lucide-react";
import { toast } from "sonner";
import { useRef } from "react";
import html2pdf from "html2pdf.js";

const Report = () => {
  const reportRef = useRef<HTMLDivElement>(null);

  const generatePDFContent = () => {
    const container = document.createElement('div');
    container.innerHTML = `
      <div style="
        font-family: Arial, sans-serif;
        background-color: #ffffff;
        color: #000000;
        padding: 40px;
        max-width: 8.5in;
        line-height: 1.6;
      ">
        <!-- Title Page Header -->
        <div style="text-align: center; margin-bottom: 40px; padding-bottom: 20px; border-bottom: 2px solid #333;">
          <h1 style="font-size: 28px; font-weight: bold; margin-bottom: 10px; color: #1a1a1a;">
            EXOPLANET TRANSIT DETECTION REPORT
          </h1>
          <p style="font-size: 14px; color: #666; margin-bottom: 5px;">
            Candidate Analysis: KIC 8462852
          </p>
          <p style="font-size: 12px; color: #888;">
            Generated: ${new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>

        <!-- Classification and Metadata -->
        <div style="margin-bottom: 30px; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #2563eb;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span style="font-weight: bold; font-size: 14px;">Classification:</span>
            <span style="color: #16a34a; font-weight: bold;">High Confidence Detection</span>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
            <div><strong>Target ID:</strong> KIC 8462852</div>
            <div><strong>Mission:</strong> Kepler</div>
            <div><strong>Analysis Date:</strong> 2025-01-15</div>
            <div><strong>Detection Probability:</strong> 0.94 (94%)</div>
          </div>
        </div>

        <!-- Executive Summary -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            EXECUTIVE SUMMARY
          </h2>
          <p style="font-size: 12px; text-align: justify; line-height: 1.8;">
            Analysis of light curve data from KIC 8462852 reveals a high-confidence exoplanet transit
            candidate with probability 0.94. The signal exhibits a periodic transit depth of 1.2% with
            period 3.52 days, consistent with a planetary companion. Multiple validation checks including
            odd/even transit comparison, secondary eclipse search, and shape analysis support the
            planetary hypothesis and rule out common false positive scenarios.
          </p>
        </div>

        <!-- Key Metrics -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            KEY ORBITAL PARAMETERS
          </h2>
          <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;">
            <div style="padding: 15px; background-color: #f8f9fa; border: 1px solid #ddd; text-align: center;">
              <div style="font-size: 10px; color: #666; margin-bottom: 5px;">ORBITAL PERIOD</div>
              <div style="font-size: 20px; font-weight: bold;">3.52 days</div>
            </div>
            <div style="padding: 15px; background-color: #f8f9fa; border: 1px solid #ddd; text-align: center;">
              <div style="font-size: 10px; color: #666; margin-bottom: 5px;">TRANSIT DEPTH</div>
              <div style="font-size: 20px; font-weight: bold;">1.2%</div>
            </div>
            <div style="padding: 15px; background-color: #f8f9fa; border: 1px solid #ddd; text-align: center;">
              <div style="font-size: 10px; color: #666; margin-bottom: 5px;">SIGNAL-TO-NOISE</div>
              <div style="font-size: 20px; font-weight: bold;">12.4</div>
            </div>
          </div>
        </div>

        <!-- Validation Tests -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            VALIDATION TEST RESULTS
          </h2>
          <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
            <thead>
              <tr style="background-color: #f1f5f9;">
                <th style="padding: 10px; text-align: left; border: 1px solid #ddd;">Test Name</th>
                <th style="padding: 10px; text-align: center; border: 1px solid #ddd;">Result</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Odd vs Even Transit Depth</td>
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: #16a34a; font-weight: bold;">PASS</td>
              </tr>
              <tr style="background-color: #fafafa;">
                <td style="padding: 8px; border: 1px solid #ddd;">Secondary Eclipse Search</td>
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: #16a34a; font-weight: bold;">PASS</td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Transit Shape Analysis</td>
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: #16a34a; font-weight: bold;">PASS</td>
              </tr>
              <tr style="background-color: #fafafa;">
                <td style="padding: 8px; border: 1px solid #ddd;">Centroid Motion Check</td>
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: #16a34a; font-weight: bold;">PASS</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Methodology -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            DETECTION METHODOLOGY
          </h2>
          <p style="font-size: 12px; text-align: justify; line-height: 1.8; margin-bottom: 10px;">
            Detection employed a physics-informed neural network trained on validated Kepler transits,
            followed by Box-fitting Least Squares period search and phase-folding analysis. All
            candidates undergo systematic vetting including odd-even transit comparison to detect
            eclipsing binaries, secondary eclipse search to identify stellar companions, and shape
            analysis to distinguish planetary transits from grazing binary eclipses.
          </p>
        </div>

        <!-- Limitations -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            LIMITATIONS & UNCERTAINTIES
          </h2>
          <ul style="font-size: 12px; line-height: 1.8; padding-left: 20px;">
            <li style="margin-bottom: 5px;">Confidence reflects bootstrap uncertainty across light curve segments</li>
            <li style="margin-bottom: 5px;">Follow-up spectroscopy recommended for mass determination</li>
            <li style="margin-bottom: 5px;">Centroid analysis based on proxy metrics pending pixel-level validation</li>
            <li style="margin-bottom: 5px;">Period uncertainty: ±0.02 days based on BLS search window</li>
          </ul>
        </div>

        <!-- Recommendations -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            RECOMMENDED NEXT STEPS
          </h2>
          <ol style="font-size: 12px; line-height: 1.8; padding-left: 20px;">
            <li style="margin-bottom: 5px;">Schedule follow-up radial velocity observations for mass confirmation</li>
            <li style="margin-bottom: 5px;">Obtain high-resolution imaging to rule out nearby stellar companions</li>
            <li style="margin-bottom: 5px;">Submit to TESS observing program for additional transit coverage</li>
            <li style="margin-bottom: 5px;">Include in comparative study of short-period planetary systems</li>
          </ol>
        </div>

        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 10px; color: #666; text-align: center;">
          <p style="margin-bottom: 5px;">Resonant Exoplanets Detection Pipeline v1.0</p>
          <p style="margin-bottom: 5px;">NASA Space Apps Challenge 2025</p>
          <p>github.com/resonant-exoplanets</p>
        </div>
      </div>
    `;
    return container.firstElementChild as HTMLElement;
  };

  const handleExport = async (format: string) => {
    switch (format) {
      case 'PDF':
        toast.loading("Generating PDF...");
  
        try {
          const pdfContent = generatePDFContent();
          
          const opt = {
            margin: [0.75, 0.75, 0.75, 0.75] as [number, number, number, number],
            filename: `exoplanet-report-KIC-8462852-${new Date().toISOString().split('T')[0]}.pdf`,
            image: { type: 'jpeg' as const, quality: 0.98 },
            html2canvas: { 
              scale: 2, 
              useCORS: true, 
              logging: false,
              backgroundColor: '#ffffff'
            },
            jsPDF: { unit: 'in' as const, format: 'letter' as const, orientation: 'portrait' as const },
            pagebreak: { mode: ['avoid-all', 'css', 'legacy'] as any }
          };
  
          await html2pdf().set(opt).from(pdfContent).save();
          toast.success("PDF exported successfully!");
        } catch (error) {
          toast.error("Failed to generate PDF");
          console.error("PDF generation error:", error);
        }
        break;
      
       case 'CSV':
         try {
           // CSV data for the report
           const csvData = `id,name,mission,probability,period,depth,duration,snr,validations_oddEven,validations_secondary,validations_shape,validations_centroid,baselineProbability,baselineFlags,description,isConfirmed,isFalsePositive
KIC-8462852,"KIC 8462852",Kepler,0.94,3.52,0.012,2.8,12.4,true,true,true,true,0.88,"Passed standard checks","High-confidence detection with strong periodic signal. Both pipelines agree this is a genuine planetary candidate.",true,false`;

           // Create blob and download
           const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
           const link = document.createElement('a');
           const url = URL.createObjectURL(blob);
           
           link.setAttribute('href', url);
           link.setAttribute('download', `exoplanet-data-KIC-8462852-${new Date().toISOString().split('T')[0]}.csv`);
           link.style.visibility = 'hidden';
           
           document.body.appendChild(link);
           link.click();
           document.body.removeChild(link);
           
           URL.revokeObjectURL(url);
           
           toast.success("CSV exported successfully!");
         } catch (error) {
           toast.dismiss();
           toast.error("Failed to generate CSV");
           console.error("CSV generation error:", error);
         }
         break;
       default:
         break;
    }

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
          <Card ref={reportRef}>
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
