import { useState, useEffect, useRef } from "react";
import { useSearchParams, Link } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Download, FileText, Share2, Printer, Loader2, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import html2pdf from "html2pdf.js";
import api from "@/lib/api";

interface CandidateData {
  candidate_id: string;
  period_days: number;
  t0_bjd: number;
  depth_ppm: number;
  duration_hours: number;
  snr: number;
  probability: number;
  rl_action: string;
  flags: {
    odd_even_ok: boolean;
    secondary_low: boolean;
    shape_u_like: boolean;
    density_consistent: boolean;
  };
  plots?: {
    phase_fold_png?: string;
    bls_png?: string;
    oddeven_png?: string;
    secondary_png?: string;
  };
}

const Report = () => {
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [candidate, setCandidate] = useState<CandidateData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const reportRef = useRef<HTMLDivElement>(null);

  const jobId = searchParams.get("jobId");
  const candidateId = searchParams.get("candidateId");

  useEffect(() => {
    const fetchCandidate = async () => {
      if (!jobId) {
        setError("No job ID provided. Please run a detection first.");
        setLoading(false);
        return;
      }

      try {
        const results = await api.getResults(jobId);
        const foundCandidate = results.candidates.find(
          (c: CandidateData) => !candidateId || c.candidate_id === candidateId
        );

        if (foundCandidate) {
          setCandidate(foundCandidate);
        } else {
          setError("Candidate not found");
        }
      } catch (err: any) {
        console.error("Failed to fetch candidate:", err);
        setError("Failed to load candidate data");
      } finally {
        setLoading(false);
      }
    };

    fetchCandidate();
  }, [jobId, candidateId]);

  const generatePDFContent = () => {
    if (!candidate) return null;

    const today = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
    const classification = candidate.rl_action === "accept" 
      ? "High Confidence Detection" 
      : candidate.rl_action === "review" 
      ? "Requires Human Review" 
      : "Likely False Positive";
    
    const classificationColor = candidate.rl_action === "accept" ? "#16a34a" : candidate.rl_action === "review" ? "#ea580c" : "#dc2626";

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
            Candidate Analysis: ${candidate.candidate_id}
          </p>
          <p style="font-size: 12px; color: #888;">
            Generated: ${today}
          </p>
        </div>

        <!-- Classification and Metadata -->
        <div style="margin-bottom: 30px; padding: 15px; background-color: #f5f5f5; border-left: 4px solid #2563eb;">
          <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
            <span style="font-weight: bold; font-size: 14px;">Classification:</span>
            <span style="color: ${classificationColor}; font-weight: bold;">${classification}</span>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
            <div><strong>Candidate ID:</strong> ${candidate.candidate_id}</div>
            <div><strong>Analysis Date:</strong> ${today}</div>
            <div><strong>Detection Probability:</strong> ${(candidate.probability * 100).toFixed(0)}%</div>
            <div><strong>RL Action:</strong> ${candidate.rl_action.toUpperCase()}</div>
          </div>
        </div>

        <!-- Executive Summary -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            EXECUTIVE SUMMARY
          </h2>
          <p style="font-size: 12px; text-align: justify; line-height: 1.8;">
            Analysis reveals a ${candidate.rl_action === "accept" ? "high-confidence" : candidate.rl_action === "review" ? "moderate-confidence" : "low-confidence"} 
            exoplanet transit candidate with probability ${(candidate.probability * 100).toFixed(1)}%. 
            The signal exhibits a periodic transit depth of ${(candidate.depth_ppm / 10000).toFixed(2)}% with
            period ${candidate.period_days.toFixed(2)} days and SNR ${candidate.snr.toFixed(1)}, 
            ${candidate.rl_action === "accept" ? "consistent with a planetary companion" : "requiring additional validation"}. 
            ${Object.values(candidate.flags).filter(Boolean).length}/4 validation checks passed.
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
              <div style="font-size: 20px; font-weight: bold;">${candidate.period_days.toFixed(2)} days</div>
            </div>
            <div style="padding: 15px; background-color: #f8f9fa; border: 1px solid #ddd; text-align: center;">
              <div style="font-size: 10px; color: #666; margin-bottom: 5px;">TRANSIT DEPTH</div>
              <div style="font-size: 20px; font-weight: bold;">${(candidate.depth_ppm / 10000).toFixed(2)}%</div>
            </div>
            <div style="padding: 15px; background-color: #f8f9fa; border: 1px solid #ddd; text-align: center;">
              <div style="font-size: 10px; color: #666; margin-bottom: 5px;">SIGNAL-TO-NOISE</div>
              <div style="font-size: 20px; font-weight: bold;">${candidate.snr.toFixed(1)}</div>
            </div>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
            <div style="padding: 15px; background-color: #f8f9fa; border: 1px solid #ddd; text-align: center;">
              <div style="font-size: 10px; color: #666; margin-bottom: 5px;">TRANSIT DURATION</div>
              <div style="font-size: 20px; font-weight: bold;">${candidate.duration_hours.toFixed(1)} hours</div>
            </div>
            <div style="padding: 15px; background-color: #f8f9fa; border: 1px solid #ddd; text-align: center;">
              <div style="font-size: 10px; color: #666; margin-bottom: 5px;">EPOCH (BJD)</div>
              <div style="font-size: 20px; font-weight: bold;">${candidate.t0_bjd.toFixed(3)}</div>
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
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: ${candidate.flags.odd_even_ok ? '#16a34a' : '#dc2626'}; font-weight: bold;">
                  ${candidate.flags.odd_even_ok ? 'PASS' : 'FAIL'}
                </td>
              </tr>
              <tr style="background-color: #fafafa;">
                <td style="padding: 8px; border: 1px solid #ddd;">Secondary Eclipse Search</td>
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: ${candidate.flags.secondary_low ? '#16a34a' : '#dc2626'}; font-weight: bold;">
                  ${candidate.flags.secondary_low ? 'PASS' : 'FAIL'}
                </td>
              </tr>
              <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Transit Shape Analysis</td>
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: ${candidate.flags.shape_u_like ? '#16a34a' : '#dc2626'}; font-weight: bold;">
                  ${candidate.flags.shape_u_like ? 'PASS' : 'FAIL'}
                </td>
              </tr>
              <tr style="background-color: #fafafa;">
                <td style="padding: 8px; border: 1px solid #ddd;">Stellar Density Check</td>
                <td style="padding: 8px; text-align: center; border: 1px solid #ddd; color: ${candidate.flags.density_consistent ? '#16a34a' : '#dc2626'}; font-weight: bold;">
                  ${candidate.flags.density_consistent ? 'PASS' : 'FAIL'}
                </td>
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
            Detection employed a 9-stage physics-informed pipeline: (1) Data ingestion from NASA archives,
            (2) Preprocessing with sigma-clipping and detrending, (3) Box-Least-Squares period search,
            (4) Physics validation via Modulus exact computation, (5) Transit model fitting with Mandel-Agol,
            (6) Feature extraction using Qwen embeddings, (7) XGBoost classification, (8) Reinforcement learning
            triage (accept/reject/review), and (9) Explainability report generation. All candidates undergo
            systematic vetting including odd-even transit comparison, secondary eclipse search, shape analysis,
            and stellar density consistency checks.
          </p>
        </div>

        <!-- Limitations -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            LIMITATIONS & UNCERTAINTIES
          </h2>
          <ul style="font-size: 12px; line-height: 1.8; padding-left: 20px;">
            <li style="margin-bottom: 5px;">Detection confidence based on single-quarter light curve data</li>
            <li style="margin-bottom: 5px;">Follow-up observations recommended for confirmation</li>
            <li style="margin-bottom: 5px;">Mass determination requires radial velocity spectroscopy</li>
            <li style="margin-bottom: 5px;">Period uncertainty: ±0.01-0.05 days depending on data quality</li>
          </ul>
        </div>

        <!-- Recommendations -->
        <div style="margin-bottom: 30px;">
          <h2 style="font-size: 18px; font-weight: bold; margin-bottom: 12px; color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 5px;">
            RECOMMENDED NEXT STEPS
          </h2>
          <ol style="font-size: 12px; line-height: 1.8; padding-left: 20px;">
            ${candidate.rl_action === "accept" ? `
              <li style="margin-bottom: 5px;">Schedule follow-up radial velocity observations for mass confirmation</li>
              <li style="margin-bottom: 5px;">Obtain high-resolution imaging to rule out nearby stellar companions</li>
              <li style="margin-bottom: 5px;">Submit to TESS observing program for additional transit coverage</li>
              <li style="margin-bottom: 5px;">Cross-reference with NASA Exoplanet Archive for validation</li>
            ` : candidate.rl_action === "review" ? `
              <li style="margin-bottom: 5px;">Manual inspection of phase-folded light curve required</li>
              <li style="margin-bottom: 5px;">Check for stellar variability and systematic effects</li>
              <li style="margin-bottom: 5px;">Consider additional data quarters if available</li>
              <li style="margin-bottom: 5px;">Compare with known false positive catalogs</li>
            ` : `
              <li style="margin-bottom: 5px;">Likely false positive - no follow-up recommended</li>
              <li style="margin-bottom: 5px;">Check for instrumental artifacts or stellar activity</li>
              <li style="margin-bottom: 5px;">Consider for systematic false positive studies</li>
            `}
          </ol>
        </div>

        <!-- Footer -->
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 10px; color: #666; text-align: center;">
          <p style="margin-bottom: 5px;">Resonant Worlds Explorer v1.0</p>
          <p style="margin-bottom: 5px;">NASA Space Apps Challenge 2025</p>
          <p>github.com/jackalkahwati/resonant-planet</p>
        </div>
      </div>
    `;
    return container.firstElementChild as HTMLElement;
  };

  const handleExport = async (format: string) => {
    if (!candidate) {
      toast.error("No candidate data to export");
      return;
    }

    switch (format) {
      case 'PDF':
        toast.loading("Generating PDF...");
  
        try {
          const pdfContent = generatePDFContent();
          if (!pdfContent) {
            toast.error("Failed to generate PDF content");
            return;
          }
          
          const opt = {
            margin: [0.75, 0.75, 0.75, 0.75] as [number, number, number, number],
            filename: `exoplanet-report-${candidate.candidate_id}-${new Date().toISOString().split('T')[0]}.pdf`,
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
          const csvData = `id,period_days,depth_ppm,duration_hours,snr,probability,t0_bjd,rl_action,odd_even_ok,secondary_low,shape_u_like,density_consistent
${candidate.candidate_id},${candidate.period_days},${candidate.depth_ppm},${candidate.duration_hours},${candidate.snr},${candidate.probability},${candidate.t0_bjd},${candidate.rl_action},${candidate.flags.odd_even_ok},${candidate.flags.secondary_low},${candidate.flags.shape_u_like},${candidate.flags.density_consistent}`;

          const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
          const link = document.createElement('a');
          const url = URL.createObjectURL(blob);
          
          link.setAttribute('href', url);
          link.setAttribute('download', `exoplanet-data-${candidate.candidate_id}-${new Date().toISOString().split('T')[0]}.csv`);
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

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading candidate data...</p>
        </div>
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || "No candidate data available."}
            <Link to="/detect" className="underline ml-2">
              Run a detection first
            </Link>
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const classification = candidate.rl_action === "accept" 
    ? "High Confidence" 
    : candidate.rl_action === "review" 
    ? "Needs Review" 
    : "Low Confidence";

  const classificationVariant = candidate.rl_action === "accept" 
    ? "default" 
    : candidate.rl_action === "review" 
    ? "secondary" 
    : "destructive";

  const validationCount = Object.values(candidate.flags).filter(Boolean).length;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Generate Report</h1>
        <p className="text-muted-foreground">
          Export detection report with metrics, validation results, and recommendations
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card ref={reportRef}>
            <CardHeader>
              <CardTitle>Report Preview</CardTitle>
              <CardDescription>Candidate {candidate.candidate_id} Analysis Report</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Title Section */}
              <div className="border-b border-border pb-6">
                <h2 className="text-2xl font-bold mb-2">Exoplanet Transit Detection Report</h2>
                <div className="flex items-center gap-2 mb-4">
                  <Badge variant={classificationVariant}>{classification}</Badge>
                  {validationCount === 4 && <Badge variant="outline">Validated</Badge>}
                </div>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Candidate ID</p>
                    <p className="font-semibold">{candidate.candidate_id}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Analysis Date</p>
                    <p className="font-semibold">{new Date().toLocaleDateString()}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">RL Action</p>
                    <p className="font-semibold uppercase">{candidate.rl_action}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Detection Probability</p>
                    <p className="font-semibold">{(candidate.probability * 100).toFixed(1)}%</p>
                  </div>
                </div>
              </div>

              {/* Summary */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Executive Summary</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Analysis reveals a {candidate.rl_action === "accept" ? "high-confidence" : candidate.rl_action === "review" ? "moderate-confidence" : "low-confidence"} 
                  {" "}exoplanet transit candidate with probability {(candidate.probability * 100).toFixed(1)}%. 
                  The signal exhibits a periodic transit depth of {(candidate.depth_ppm / 10000).toFixed(2)}% with
                  period {candidate.period_days.toFixed(2)} days and SNR {candidate.snr.toFixed(1)}. 
                  {" "}{validationCount}/4 validation checks passed.
                </p>
              </div>

              {/* Key Metrics */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Key Orbital Parameters</h3>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-xs text-muted-foreground mb-1">Orbital Period</p>
                    <p className="text-2xl font-bold">{candidate.period_days.toFixed(2)} days</p>
                  </div>
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-xs text-muted-foreground mb-1">Transit Depth</p>
                    <p className="text-2xl font-bold">{(candidate.depth_ppm / 10000).toFixed(2)}%</p>
                  </div>
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-xs text-muted-foreground mb-1">Signal-to-Noise</p>
                    <p className="text-2xl font-bold">{candidate.snr.toFixed(1)}</p>
                  </div>
                  <div className="bg-muted rounded-lg p-4">
                    <p className="text-xs text-muted-foreground mb-1">Duration</p>
                    <p className="text-2xl font-bold">{candidate.duration_hours.toFixed(1)} hrs</p>
                  </div>
                  <div className="bg-muted rounded-lg p-4 md:col-span-2">
                    <p className="text-xs text-muted-foreground mb-1">Epoch (BJD)</p>
                    <p className="text-2xl font-bold">{candidate.t0_bjd.toFixed(3)}</p>
                  </div>
                </div>
              </div>

              {/* Validation Results */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Validation Tests</h3>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Odd vs Even Transit Depth</span>
                    <Badge variant={candidate.flags.odd_even_ok ? "default" : "destructive"}>
                      {candidate.flags.odd_even_ok ? "Pass" : "Fail"}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Secondary Eclipse Search</span>
                    <Badge variant={candidate.flags.secondary_low ? "default" : "destructive"}>
                      {candidate.flags.secondary_low ? "Pass" : "Fail"}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Transit Shape Analysis</span>
                    <Badge variant={candidate.flags.shape_u_like ? "default" : "destructive"}>
                      {candidate.flags.shape_u_like ? "Pass" : "Fail"}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <span className="text-sm">Stellar Density Check</span>
                    <Badge variant={candidate.flags.density_consistent ? "default" : "destructive"}>
                      {candidate.flags.density_consistent ? "Pass" : "Fail"}
                    </Badge>
                  </div>
                </div>
              </div>

              {/* Method Summary */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Detection Methodology</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Detection employed a 9-stage physics-informed pipeline with Box-Least-Squares period search,
                  Modulus exact computation for transit fitting, and comprehensive validation checks. The system
                  uses reinforcement learning triage to classify candidates as accept/reject/review based on
                  physical plausibility and validation test results.
                </p>
              </div>

              {/* Next Steps */}
              <div className="space-y-3">
                <h3 className="text-lg font-semibold">Recommended Next Steps</h3>
                <ol className="text-sm text-muted-foreground space-y-2">
                  {candidate.rl_action === "accept" ? (
                    <>
                      <li>1. Schedule follow-up radial velocity observations for mass confirmation</li>
                      <li>2. Obtain high-resolution imaging to rule out nearby stellar companions</li>
                      <li>3. Submit to TESS observing program for additional transit coverage</li>
                      <li>4. Cross-reference with NASA Exoplanet Archive for validation</li>
                    </>
                  ) : candidate.rl_action === "review" ? (
                    <>
                      <li>1. Manual inspection of phase-folded light curve required</li>
                      <li>2. Check for stellar variability and systematic effects</li>
                      <li>3. Consider additional data quarters if available</li>
                      <li>4. Compare with known false positive catalogs</li>
                    </>
                  ) : (
                    <>
                      <li>1. Likely false positive - no follow-up recommended</li>
                      <li>2. Check for instrumental artifacts or stellar activity</li>
                      <li>3. Consider for systematic false positive studies</li>
                    </>
                  )}
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
                <span className="text-muted-foreground">Orbital Parameters</span>
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
                <span className="text-muted-foreground">Recommendations</span>
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
                Resonant Worlds Explorer v1.0, NASA Space Apps Challenge 2025.
                Available at: https://github.com/jackalkahwati/resonant-planet
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Report;
