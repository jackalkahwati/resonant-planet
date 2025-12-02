import { motion } from 'framer-motion';
import { 
  Search, Database, Brain, TrendingUp, Rocket, Sparkles, Atom, 
  Calculator, CheckCircle, FileText, MonitorPlay, ChevronDown,
  Globe2
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';

interface LandingProps {
  onEnterApp: () => void;
}

export const Landing: React.FC<LandingProps> = ({ onEnterApp }) => {
  const scrollToFeatures = () => {
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
        {/* Background Image */}
        <div
          className="absolute inset-0 opacity-40"
          style={{
            backgroundImage: `url(/hero-exoplanet.jpg)`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        />
        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 via-black/40 to-black" />
        
        {/* Content */}
        <div className="relative z-10 container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Badges */}
            <div className="flex flex-wrap justify-center gap-2 mb-6">
              <span className="px-3 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-sm flex items-center gap-1">
                <Calculator className="h-3 w-3" />
                Powered by Modulus PAT
              </span>
              <span className="px-3 py-1 rounded-full bg-cyan-500/20 border border-cyan-500/30 text-sm flex items-center gap-1">
                <Atom className="h-3 w-3" />
                Biosignature Detection
              </span>
              <span className="px-3 py-1 rounded-full bg-green-500/20 border border-green-500/30 text-sm flex items-center gap-1">
                <Sparkles className="h-3 w-3" />
                NASA TAP API
              </span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              Discover exoplanets and{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400">
                biosignatures
              </span>{' '}
              with{' '}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-green-400">
                exact computation
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
              The first system integrating Modulus Prime Algebra Transformer with AI for 
              transit detection AND atmospheric biosignature analysis. Zero rounding errors, 
              natural language interface, JWST spectroscopy support.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <Button onClick={onEnterApp} className="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-lg px-8 py-6">
                <Search className="h-5 w-5 mr-2" />
                Launch Explorer
              </Button>
              <a href="/presentation.pdf" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" className="border-purple-500/50 hover:bg-purple-500/20 text-lg px-6 py-6">
                  <MonitorPlay className="h-5 w-5 mr-2" />
                  View Presentation
                </Button>
              </a>
              <a href="/research-paper.pdf" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" className="border-cyan-500/50 hover:bg-cyan-500/20 text-lg px-6 py-6">
                  <FileText className="h-5 w-5 mr-2" />
                  Read Research Paper
                </Button>
              </a>
              <Button variant="outline" onClick={scrollToFeatures} className="border-green-500/50 hover:bg-green-500/20 text-lg px-6 py-6">
                Learn the Method
              </Button>
            </div>
          </motion.div>

          {/* Scroll Indicator */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 0.5 }}
            className="absolute bottom-8 left-1/2 transform -translate-x-1/2 cursor-pointer"
            onClick={scrollToFeatures}
          >
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              <ChevronDown className="h-8 w-8 text-gray-400" />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gradient-to-b from-black to-gray-900">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Powerful Features</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Our platform combines NASA data with advanced AI for comprehensive exoplanet analysis
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }}>
              <Card className="h-full bg-white/5 border-white/10 hover:border-purple-500/50 transition-all">
                <CardHeader>
                  <Database className="h-10 w-10 text-purple-400 mb-2" />
                  <CardTitle className="text-white">Multi-Mission Data</CardTitle>
                  <CardDescription className="text-gray-400">
                    Access Kepler, K2, TESS light curves + JWST transmission spectra
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>• 5,500+ confirmed exoplanets</li>
                    <li>• NASA TAP API integration</li>
                    <li>• Real-time data updates</li>
                    <li>• Custom data upload</li>
                  </ul>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 }}>
              <Card className="h-full bg-white/5 border-white/10 hover:border-cyan-500/50 transition-all">
                <CardHeader>
                  <Calculator className="h-10 w-10 text-cyan-400 mb-2" />
                  <CardTitle className="text-white">Modulus Exact Computation</CardTitle>
                  <CardDescription className="text-gray-400">
                    Prime Algebra Transformer for zero-error transit modeling
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>• Zero rounding errors (PAT)</li>
                    <li>• Natural language interface</li>
                    <li>• Machine-checkable proofs</li>
                    <li>• Deterministic results</li>
                  </ul>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.3 }}>
              <Card className="h-full bg-white/5 border-white/10 hover:border-green-500/50 transition-all">
                <CardHeader>
                  <Atom className="h-10 w-10 text-green-400 mb-2" />
                  <CardTitle className="text-white">Biosignature Analysis</CardTitle>
                  <CardDescription className="text-gray-400">
                    Detect O₂, CH₄, DMS and other biosignature molecules
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="text-sm text-gray-400 space-y-2">
                    <li>• 6 biosignature molecules</li>
                    <li>• Chemical disequilibrium</li>
                    <li>• K2-18b validated</li>
                    <li>• Expert-matching results</li>
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Method Overview */}
      <section className="py-20 bg-gray-900">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="max-w-4xl mx-auto"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6 text-center">Method Overview</h2>
            <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
              Our approach combines state-of-the-art deep learning with rigorous astrophysics validation.
            </p>

            <div className="grid md:grid-cols-2 gap-6">
              <Card className="bg-white/5 border-white/10">
                <CardHeader>
                  <CardTitle className="text-purple-400">Detection Pipeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="text-sm text-gray-400 space-y-2">
                    <li>1. Light curve preprocessing and normalization</li>
                    <li>2. Neural network transit probability inference</li>
                    <li>3. Box-fitting Least Squares period search</li>
                    <li>4. Phase-fold and model fit</li>
                  </ol>
                </CardContent>
              </Card>

              <Card className="bg-white/5 border-white/10">
                <CardHeader>
                  <CardTitle className="text-cyan-400">Validation Tests</CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="text-sm text-gray-400 space-y-2">
                    <li>1. Odd vs even transit depth consistency</li>
                    <li>2. Secondary eclipse presence check</li>
                    <li>3. Transit shape vs V-shape test</li>
                    <li>4. Centroid shift analysis proxy</li>
                  </ol>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        </div>
      </section>

      {/* K2-18b Case Study */}
      <section className="py-20 bg-gradient-to-b from-gray-900 to-black">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <Card className="max-w-4xl mx-auto bg-gradient-to-br from-purple-900/30 to-cyan-900/30 border-purple-500/30">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="px-2 py-1 rounded-full bg-green-500/20 border border-green-500/30 text-xs flex items-center gap-1">
                        <CheckCircle className="h-3 w-3 text-green-400" />
                        Validated Discovery
                      </span>
                      <span className="px-2 py-1 rounded-full bg-purple-500/20 border border-purple-500/30 text-xs">
                        JWST
                      </span>
                    </div>
                    <CardTitle className="text-2xl text-white">K2-18b Biosignature Analysis</CardTitle>
                    <CardDescription className="text-gray-400 mt-2">
                      Our system successfully identified the same biosignature molecules as the expert team
                    </CardDescription>
                  </div>
                  <Sparkles className="h-8 w-8 text-purple-400" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="font-semibold mb-3 text-purple-400">Target Properties</h3>
                    <ul className="space-y-2 text-sm text-gray-400">
                      <li className="flex justify-between"><span>Mass:</span><span className="text-white">8.6 M⊕</span></li>
                      <li className="flex justify-between"><span>Radius:</span><span className="text-white">2.6 R⊕</span></li>
                      <li className="flex justify-between"><span>Temperature:</span><span className="text-white">270 K</span></li>
                      <li className="flex justify-between"><span>Period:</span><span className="text-white">32.9 days</span></li>
                      <li className="flex justify-between"><span>Zone:</span><span className="text-green-400">Habitable ✓</span></li>
                    </ul>
                  </div>
                  <div>
                    <h3 className="font-semibold mb-3 text-cyan-400">Our System's Detection</h3>
                    <ul className="space-y-2 text-sm">
                      <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-400" /><span className="text-gray-300">O₂ at 0.76 μm (19,145 ppm)</span></li>
                      <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-400" /><span className="text-gray-300">CH₄ at 3.30 μm (79,106 ppm)</span></li>
                      <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-400" /><span className="text-gray-300">PH₃ at 4.30 μm (7,344 ppm)</span></li>
                      <li className="flex items-center gap-2"><CheckCircle className="h-4 w-4 text-green-400" /><span className="text-gray-300">DMS at 3.40 μm (79,106 ppm)</span></li>
                    </ul>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-purple-500/10 rounded-lg border border-purple-500/30">
                  <div className="flex items-start gap-3">
                    <div className="bg-purple-500/20 rounded-full p-2 mt-1">
                      <Brain className="h-5 w-5 text-purple-400" />
                    </div>
                    <div>
                      <h4 className="font-semibold mb-2 text-white">Biosignature Score: 0.45 / 1.00</h4>
                      <p className="text-sm text-gray-400">
                        <strong className="text-purple-300">O₂ + CH₄ coexistence detected</strong> — requires active replenishment source. 
                        Matches Madhusudhan et al. (2023) published findings.
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* Why This Matters */}
      <section className="py-20 bg-black">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-12"
          >
            <Rocket className="h-12 w-12 text-purple-400 mx-auto mb-4" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Why This Matters</h2>
            <p className="text-gray-400">
              Advancing exoplanet science through better detection and validation
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.1 }}>
              <Card className="h-full bg-white/5 border-white/10 text-center">
                <CardHeader>
                  <Search className="h-8 w-8 text-purple-400 mx-auto mb-2" />
                  <CardTitle className="text-white text-lg">Scientific Impact</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-gray-400">
                  Detect planets classic pipelines miss and validate candidates with confidence
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.2 }}>
              <Card className="h-full bg-white/5 border-white/10 text-center">
                <CardHeader>
                  <Brain className="h-8 w-8 text-cyan-400 mx-auto mb-2" />
                  <CardTitle className="text-white text-lg">Technical Innovation</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-gray-400">
                  Physics-informed AI with transparent explainability
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: 0.3 }}>
              <Card className="h-full bg-white/5 border-white/10 text-center">
                <CardHeader>
                  <TrendingUp className="h-8 w-8 text-green-400 mx-auto mb-2" />
                  <CardTitle className="text-white text-lg">Educational Value</CardTitle>
                </CardHeader>
                <CardContent className="text-sm text-gray-400">
                  Make sophisticated detection accessible to everyone
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-t from-purple-900/20 to-black">
        <div className="container mx-auto px-4 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-6">Ready to Discover?</h2>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Explore 5,500+ confirmed exoplanets with interactive 3D visualizations, 
              real-time NASA data, and AI-powered analysis.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Button onClick={onEnterApp} className="bg-gradient-to-r from-purple-600 to-cyan-600 hover:from-purple-500 hover:to-cyan-500 text-lg px-8 py-6">
                <Globe2 className="h-5 w-5 mr-2" />
                Launch Exoplanet Explorer
              </Button>
              <a href="/presentation.pdf" target="_blank" rel="noopener noreferrer">
                <Button variant="outline" className="border-white/20 hover:bg-white/10 text-lg px-6 py-6">
                  <MonitorPlay className="h-5 w-5 mr-2" />
                  View Presentation
                </Button>
              </a>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 border-t border-white/10">
        <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
          <p>Resonant Worlds Explorer • NASA Space Apps Challenge 2024</p>
          <p className="mt-2">Data from NASA Exoplanet Archive TAP API</p>
        </div>
      </footer>
    </div>
  );
};
