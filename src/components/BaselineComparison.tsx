import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { ArrowRight, AlertTriangle, CheckCircle, TrendingUp } from "lucide-react";
import { Candidate } from "@/data/sampleCandidates";

interface BaselineComparisonProps {
  candidate: Candidate;
}

export const BaselineComparison = ({ candidate }: BaselineComparisonProps) => {
  const improvementPercent = Math.round(
    ((candidate.probability - candidate.baselineProbability) / candidate.baselineProbability) * 100
  );
  
  const showImprovement = candidate.probability > candidate.baselineProbability + 0.15;

  return (
    <div className="space-y-4">
      <div className="text-center mb-6">
        <h3 className="text-lg font-semibold mb-2">Classic Pipeline vs. Resonant System</h3>
        <p className="text-sm text-muted-foreground">
          See how physics-first validation improves detection accuracy
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Classic Pipeline */}
        <Card className="border-muted">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Classic BLS Pipeline</CardTitle>
              <Badge variant="outline">Baseline</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center py-4">
              <p className="text-sm text-muted-foreground mb-2">Detection Confidence</p>
              <p className="text-4xl font-bold text-muted-foreground">
                {candidate.baselineProbability.toFixed(2)}
              </p>
            </div>

            <div className="space-y-2">
              <p className="text-xs font-semibold text-muted-foreground">System Flags:</p>
              {candidate.baselineFlags.map((flag, idx) => (
                <div key={idx} className="flex items-start gap-2 text-xs">
                  <AlertTriangle className="h-3 w-3 text-accent mt-0.5 flex-shrink-0" />
                  <span className="text-muted-foreground">{flag}</span>
                </div>
              ))}
            </div>

            <Alert className="bg-muted/50">
              <AlertDescription className="text-xs">
                Relies primarily on BLS power and SNR thresholds without physics validation
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>

        {/* Arrow */}
        <div className="hidden md:flex items-center justify-center absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
          <div className="bg-background rounded-full p-3 border-2 border-primary shadow-lg">
            <ArrowRight className="h-6 w-6 text-primary" />
          </div>
        </div>

        {/* Resonant System */}
        <Card className={`border-2 ${candidate.isFalsePositive ? 'border-primary' : 'border-primary'}`}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Resonant System</CardTitle>
              <Badge>Physics-First</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-center py-4">
              <p className="text-sm text-muted-foreground mb-2">Detection Confidence</p>
              <p className={`text-4xl font-bold ${candidate.probability > 0.8 ? 'text-primary' : 'text-accent'}`}>
                {candidate.probability.toFixed(2)}
              </p>
              {showImprovement && (
                <div className="flex items-center justify-center gap-1 mt-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  <span className="text-sm text-primary font-semibold">
                    {improvementPercent > 0 ? '+' : ''}{improvementPercent}% confidence
                  </span>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <p className="text-xs font-semibold">Physics Validation:</p>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(candidate.validations).map(([key, passed]) => (
                  <div key={key} className="flex items-center gap-1 text-xs">
                    {passed ? (
                      <CheckCircle className="h-3 w-3 text-primary" />
                    ) : (
                      <AlertTriangle className="h-3 w-3 text-accent" />
                    )}
                    <span className="capitalize">{key.replace(/([A-Z])/g, ' $1').trim()}</span>
                  </div>
                ))}
              </div>
            </div>

            <Alert className={candidate.isFalsePositive ? "border-primary bg-primary/10" : "border-primary bg-primary/10"}>
              <AlertDescription className="text-xs">
                {candidate.isFalsePositive
                  ? "Successfully identified false positive through validation tests"
                  : "All physics checks passed - high confidence genuine transit"
                }
              </AlertDescription>
            </Alert>
          </CardContent>
        </Card>
      </div>

      {/* Key Insight */}
      <Card className="bg-gradient-data border-primary/30">
        <CardContent className="pt-6">
          <div className="flex items-start gap-3">
            <div className="bg-primary/20 rounded-full p-2">
              <TrendingUp className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1">
              <h4 className="font-semibold mb-1">Key Insight</h4>
              <p className="text-sm text-muted-foreground">{candidate.description}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
