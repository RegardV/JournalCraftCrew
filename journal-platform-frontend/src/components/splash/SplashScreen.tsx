import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BookOpen, Brain, Users, Zap, Shield, Star, Sparkles } from 'lucide-react';

const SplashScreen: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [loadedFeatures, setLoadedFeatures] = useState<number[]>([]);

  useEffect(() => {
    setIsVisible(true);

    // Animate features loading in sequence
    const timer = setTimeout(() => {
      setLoadedFeatures([0]);
    }, 300);

    const timers = [1, 2, 3, 4, 5].map((index) =>
      setTimeout(() => {
        setLoadedFeatures(prev => [...prev, index]);
      }, 600 + (index * 200))
    );

    return () => {
      clearTimeout(timer);
      timers.forEach(clearTimeout);
    };
  }, []);

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Intelligence",
      description: "9 specialized CrewAI agents working together to create personalized journal content"
    },
    {
      icon: BookOpen,
      title: "Professional Quality",
      description: "Generate publish-ready journals with expert research and polished content"
    },
    {
      icon: Users,
      title: "Personalized Experience",
      description: "Tailored content based on your unique preferences and writing style"
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Real-time progress tracking with instant AI generation and updates"
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Enterprise-grade security with encrypted data storage and privacy protection"
    },
    {
      icon: Star,
      title: "Expert Content",
      description: "Research-backed insights from bestselling authors and industry experts"
    }
  ];

  return (
    <div className="min-h-screen gradient-bg overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-600"></div>
      </div>

      {/* Main Content */}
      <div className="relative z-10">
        {/* Header */}
        <header className="glass-effect border-b border-white/20">
          <div className="section-container">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-5 h-5 text-white" />
                </div>
                <span className="font-bold text-xl gradient-text">Journal Craft Crew</span>
              </div>
              <Link
                to="/auth/login"
                className="text-gray-600 hover:text-gray-900 font-medium transition-colors"
              >
                Sign In
              </Link>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="section-container py-20">
          <div className={`text-center max-w-4xl mx-auto transition-all duration-1000 ${
            isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'
          }`}>
            <div className="mb-8">
              <div className="inline-flex items-center gap-2 bg-white/80 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                <Zap className="w-4 h-4 text-indigo-600" />
                <span className="text-sm font-medium text-gray-900">AI-Powered Journal Generation</span>
              </div>
            </div>

            <h1 className="text-display mb-6 gradient-text">
              Transform Your Ideas Into
              <br />
              Beautiful Journals
            </h1>

            <p className="text-2xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed">
              Experience the power of 9 specialized AI agents working together to create
              personalized, professional-quality journals in minutes, not months.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                to="/auth/register"
                className="btn btn-primary text-lg px-8 py-4 flex items-center gap-3 group"
              >
                Get Started Now
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>

  
              <button className="btn btn-outline text-lg px-8 py-4">
                Watch Demo
              </button>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 bg-white/60 backdrop-blur-sm">
          <div className="section-container">
            <div className="text-center mb-16">
              <h2 className="text-heading mb-4">Powered by Advanced AI Technology</h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Our CrewAI system combines multiple specialized agents to deliver
                unparalleled journal creation capabilities
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
              {features.map((feature, index) => {
                const Icon = feature.icon;
                const isLoaded = loadedFeatures.includes(index);

                return (
                  <div
                    key={index}
                    className={`content-card transition-all duration-700 ${
                      isLoaded
                        ? 'opacity-100 translate-y-0'
                        : 'opacity-0 translate-y-10'
                    }`}
                  >
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0">
                        <div className="w-12 h-12 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-xl flex items-center justify-center">
                          <Icon className="w-6 h-6 text-white" />
                        </div>
                      </div>
                      <div>
                        <h3 className="text-subheading font-semibold text-gray-900 mb-2">
                          {feature.title}
                        </h3>
                        <p className="text-body text-gray-600 leading-relaxed">
                          {feature.description}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-20">
          <div className="section-container">
            <div className="content-card text-center max-w-3xl mx-auto">
              <h2 className="text-heading mb-4">
                Ready to Create Your First AI-Powered Journal?
              </h2>
              <p className="text-xl text-gray-600 mb-8">
                Join thousands of users who are already transforming their ideas
                into beautiful, personalized journals with our AI technology.
              </p>

              <Link
                to="/auth/register"
                className="btn btn-primary text-lg px-8 py-4 inline-flex items-center gap-3 group"
              >
                Start Creating Today
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>

              <p className="text-sm text-gray-500 mt-6">
                No credit card required • Free to start • Cancel anytime
              </p>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-gray-200 bg-white/80 backdrop-blur-sm">
          <div className="section-container py-12">
            <div className="text-center">
              <div className="flex items-center justify-center gap-2 mb-4">
                <div className="w-6 h-6 bg-gradient-to-br from-indigo-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <BookOpen className="w-4 h-4 text-white" />
                </div>
                <span className="font-bold text-lg gradient-text">Journal Craft Crew</span>
              </div>
              <p className="text-gray-600">
                © 2025 Journal Craft Crew. Empowering writers with AI technology.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default SplashScreen;