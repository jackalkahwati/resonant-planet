import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronRight, ChevronLeft, Sparkles, TrendingDown, CheckCircle, X, Check, AlertTriangle } from "lucide-react";

interface WalkthroughStep {
  title: string;
  description: string;
  visual: React.ReactNode;
  icon: any;
}

// Visual component for Step 1: Light curve with periodic dips
const LightCurveVisual = () => (
  <svg viewBox="0 0 400 150" className="w-full h-full">
    {/* Grid lines */}
    <line x1="0" y1="75" x2="400" y2="75" stroke="currentColor" strokeOpacity="0.1" strokeDasharray="2,2" />
    <line x1="0" y1="25" x2="400" y2="25" stroke="currentColor" strokeOpacity="0.1" strokeDasharray="2,2" />
    <line x1="0" y1="125" x2="400" y2="125" stroke="currentColor" strokeOpacity="0.1" strokeDasharray="2,2" />
    
    {/* Baseline flux */}
    <path
      d="M 0,30 Q 50,28 100,32 Q 150,29 200,31 Q 250,30 300,29 Q 350,31 400,30"
      stroke="hsl(var(--primary))"
      strokeWidth="2"
      fill="none"
      opacity="0.6"
    />
    
    {/* Transit dips */}
    {[80, 180, 280].map((x) => (
      <g key={x}>
        <path
          d={`M ${x - 15},30 L ${x - 10},30 Q ${x - 5},30 ${x - 3},50 L ${x + 3},50 Q ${x + 5},30 ${x + 10},30 L ${x + 15},30`}
          stroke="hsl(var(--primary))"
          strokeWidth="2.5"
          fill="none"
        />
        {/* Transit marker */}
        <circle cx={x} cy="50" r="2" fill="hsl(var(--destructive))" />
      </g>
    ))}
    
    {/* Labels */}
    <text x="10" y="20" fontSize="10" fill="currentColor" opacity="0.5">100%</text>
    <text x="10" y="140" fontSize="10" fill="currentColor" opacity="0.5">99%</text>
    <text x="180" y="145" fontSize="12" fill="currentColor" opacity="0.7" textAnchor="middle">Time →</text>
  </svg>
);

// Visual component for Step 2: Phase-folded transit
const PhaseFoldedVisual = () => (
  <svg viewBox="0 0 400 150" className="w-full h-full">
    {/* Grid */}
    <line x1="0" y1="75" x2="400" y2="75" stroke="currentColor" strokeOpacity="0.1" strokeDasharray="2,2" />
    
    {/* Data points (scattered) */}
    {Array.from({ length: 50 }, (_, i) => {
      const x = 50 + i * 6;
      const phase = (x - 200) / 100;
      const inTransit = Math.abs(phase) < 0.15;
      const y = inTransit ? 90 + Math.random() * 5 : 30 + Math.random() * 8;
      return <circle key={i} cx={x} cy={y} r="1.5" fill="hsl(var(--primary))" opacity="0.5" />;
    })}
    
    {/* Model fit (smooth line) */}
    <path
      d="M 50,33 L 140,33 Q 155,33 165,80 L 235,80 Q 245,33 260,33 L 350,33"
      stroke="hsl(var(--destructive))"
      strokeWidth="2"
      fill="none"
    />
    
    {/* Transit depth indicator */}
    <line x1="360" y1="33" x2="360" y2="80" stroke="hsl(var(--destructive))" strokeWidth="1" strokeDasharray="3,3" />
    <text x="365" y="60" fontSize="10" fill="hsl(var(--destructive))">Depth</text>
    
    {/* Labels */}
    <text x="200" y="20" fontSize="12" fill="currentColor" opacity="0.7" textAnchor="middle">Phase-Folded Transit</text>
    <text x="200" y="145" fontSize="10" fill="currentColor" opacity="0.5" textAnchor="middle">Orbital Phase</text>
  </svg>
);

// Visual component for Step 3: Validation checks
const ValidationVisual = () => (
  <div className="grid grid-cols-2 gap-3 p-4">
    <div className="flex items-center gap-2 p-3 bg-green-500/10 rounded-lg border border-green-500/30">
      <Check className="h-5 w-5 text-green-500" />
      <div>
        <div className="text-sm font-medium">Odd/Even Match</div>
        <div className="text-xs text-muted-foreground">Δ 2.3%</div>
      </div>
    </div>
    
    <div className="flex items-center gap-2 p-3 bg-green-500/10 rounded-lg border border-green-500/30">
      <Check className="h-5 w-5 text-green-500" />
      <div>
        <div className="text-sm font-medium">No Secondary</div>
        <div className="text-xs text-muted-foreground">SNR 1.2σ</div>
      </div>
    </div>
    
    <div className="flex items-center gap-2 p-3 bg-green-500/10 rounded-lg border border-green-500/30">
      <Check className="h-5 w-5 text-green-500" />
      <div>
        <div className="text-sm font-medium">U-Shaped</div>
        <div className="text-xs text-muted-foreground">Score 0.89</div>
      </div>
    </div>
    
    <div className="flex items-center gap-2 p-3 bg-green-500/10 rounded-lg border border-green-500/30">
      <Check className="h-5 w-5 text-green-500" />
      <div>
        <div className="text-sm font-medium">Density OK</div>
        <div className="text-xs text-muted-foreground">2.3 g/cm³</div>
      </div>
    </div>
  </div>
);

// Visual component for Step 4: Final confidence
const ConfidenceVisual = () => (
  <div className="p-6">
    <div className="relative mb-6">
      {/* Confidence circle */}
      <div className="relative w-32 h-32 mx-auto">
        <svg viewBox="0 0 100 100" className="transform -rotate-90">
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            opacity="0.1"
          />
          <circle
            cx="50"
            cy="50"
            r="45"
            fill="none"
            stroke="hsl(var(--primary))"
            strokeWidth="8"
            strokeDasharray="282.7"
            strokeDashoffset="28.27"
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center flex-col">
          <div className="text-3xl font-bold text-primary">90%</div>
          <div className="text-xs text-muted-foreground">Confidence</div>
        </div>
      </div>
    </div>
    
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">Period</span>
        <span className="font-medium">2.47 days</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">Depth</span>
        <span className="font-medium">1,240 ppm</span>
      </div>
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">SNR</span>
        <span className="font-medium">12.5σ</span>
      </div>
    </div>
    
    <div className="mt-4 p-3 bg-primary/10 rounded-lg border border-primary/30">
      <div className="flex items-center gap-2">
        <CheckCircle className="h-5 w-5 text-primary" />
        <span className="text-sm font-medium">Candidate Validated</span>
      </div>
    </div>
  </div>
);

const steps: WalkthroughStep[] = [
  {
    title: "The Starlight Dip",
    description: "When a planet crosses in front of its star, it blocks a tiny fraction of starlight. This creates a characteristic dip in brightness we can detect.",
    visual: <LightCurveVisual />,
    icon: TrendingDown,
  },
  {
    title: "The Physics Fit",
    description: "We fold the light curve at the detected period and fit a transit model. The flat bottom and symmetric shape are telltale signs of a planetary transit.",
    visual: <PhaseFoldedVisual />,
    icon: Sparkles,
  },
  {
    title: "Validation Tests",
    description: "To rule out false positives, we check if odd and even transits have the same depth, search for secondary eclipses, and verify the transit shape.",
    visual: <ValidationVisual />,
    icon: CheckCircle,
  },
  {
    title: "High Confidence Detection",
    description: "All tests passed! This signal shows all the characteristics of a genuine planetary transit. The classic pipeline might have flagged it for manual review, but our physics-first approach confidently validates it.",
    visual: <ConfidenceVisual />,
    icon: CheckCircle,
  },
];

export const StorytellingWalkthrough = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isOpen, setIsOpen] = useState(false);

  if (!isOpen) {
    return (
      <Card className="border-primary/30 bg-gradient-data">
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-primary/20 rounded-full p-2">
                <Sparkles className="h-5 w-5 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold">60-Second Walkthrough</h3>
                <p className="text-sm text-muted-foreground">
                  See how we detect and validate exoplanets
                </p>
              </div>
            </div>
            <Button variant="hero" onClick={() => setIsOpen(true)}>
              Start Tour
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  const step = steps[currentStep];
  const Icon = step.icon;
  const isLastStep = currentStep === steps.length - 1;

  return (
    <Card className="border-2 border-primary animate-fade-in">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between mb-4">
          <Badge variant="outline">
            Step {currentStep + 1} of {steps.length}
          </Badge>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              setIsOpen(false);
              setCurrentStep(0);
            }}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <div className="mb-6">
          <div className="flex items-center gap-3 mb-3">
            <div className="bg-primary/20 rounded-full p-3">
              <Icon className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-xl font-bold">{step.title}</h3>
          </div>
          
          <p className="text-muted-foreground mb-4">{step.description}</p>

          {/* Visual */}
          <div className="aspect-video bg-muted rounded-lg flex items-center justify-center border border-border mb-4 overflow-hidden">
            {step.visual}
          </div>

          {/* Progress bar */}
          <div className="flex gap-1">
            {steps.map((_, idx) => (
              <div
                key={idx}
                className={`h-1 flex-1 rounded-full transition-colors ${
                  idx === currentStep ? 'bg-primary' : idx < currentStep ? 'bg-primary/40' : 'bg-muted'
                }`}
              />
            ))}
          </div>
        </div>

        <div className="flex justify-between">
          <Button
            variant="outline"
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          
          {isLastStep ? (
            <Button
              variant="hero"
              onClick={() => {
                setIsOpen(false);
                setCurrentStep(0);
              }}
            >
              <CheckCircle className="h-4 w-4" />
              Got It!
            </Button>
          ) : (
            <Button
              variant="hero"
              onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
