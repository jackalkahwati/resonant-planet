import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ChevronRight, ChevronLeft, Sparkles, TrendingDown, CheckCircle, X } from "lucide-react";

interface WalkthroughStep {
  title: string;
  description: string;
  visual: string;
  icon: any;
}

const steps: WalkthroughStep[] = [
  {
    title: "The Starlight Dip",
    description: "When a planet crosses in front of its star, it blocks a tiny fraction of starlight. This creates a characteristic dip in brightness we can detect.",
    visual: "Light curve showing periodic dips",
    icon: TrendingDown,
  },
  {
    title: "The Physics Fit",
    description: "We fold the light curve at the detected period and fit a transit model. The flat bottom and symmetric shape are telltale signs of a planetary transit.",
    visual: "Phase-folded curve with model overlay",
    icon: Sparkles,
  },
  {
    title: "Validation Tests",
    description: "To rule out false positives, we check if odd and even transits have the same depth, search for secondary eclipses, and verify the transit shape.",
    visual: "Validation checks dashboard",
    icon: CheckCircle,
  },
  {
    title: "High Confidence Detection",
    description: "All tests passed! This signal shows all the characteristics of a genuine planetary transit. The classic pipeline might have flagged it for manual review, but our physics-first approach confidently validates it.",
    visual: "Final report with confidence score",
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

          {/* Visual placeholder */}
          <div className="aspect-video bg-muted rounded-lg flex items-center justify-center border border-border mb-4">
            <p className="text-sm text-muted-foreground">{step.visual}</p>
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
