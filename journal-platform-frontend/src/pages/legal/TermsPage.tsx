import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, FileText } from 'lucide-react';

const TermsPage: React.FC = () => {
  return (
    <div className="min-h-screen gradient-bg">
      <div className="section-container py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Link
              to="/auth/register"
              className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Register
            </Link>

            <div className="flex items-center gap-4 mb-4">
              <div className="w-12 h-12 bg-indigo-100 rounded-xl flex items-center justify-center">
                <FileText className="w-6 h-6 text-indigo-600" />
              </div>
              <h1 className="text-4xl font-bold text-gray-900">Terms of Service</h1>
            </div>
            <p className="text-gray-600">
              Last updated: {new Date().toLocaleDateString()}
            </p>
          </div>

          {/* Content */}
          <div className="content-card p-8">
            <div className="prose prose-lg max-w-none">
              <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
              <p className="text-gray-600 mb-6">
                By accessing and using Journal Craft Crew, you accept and agree to be bound by the terms and provision of this agreement.
              </p>

              <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Use License</h2>
              <p className="text-gray-600 mb-6">
                Permission is granted to temporarily download one copy of the materials on Journal Craft Crew for personal, non-commercial transitory viewing only.
              </p>

              <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Disclaimer</h2>
              <p className="text-gray-600 mb-6">
                The materials on Journal Craft Crew are provided on an 'as is' basis. Journal Craft Crew makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties.
              </p>

              <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Limitations</h2>
              <p className="text-gray-600 mb-6">
                In no event shall Journal Craft Crew or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials.
              </p>

              <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Privacy Policy</h2>
              <p className="text-gray-600 mb-6">
                Your Privacy Policy is incorporated into this Agreement by reference. Please review our Privacy Policy, which also governs the Site.
              </p>

              <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Revisions and Errata</h2>
              <p className="text-gray-600 mb-6">
                The materials appearing on Journal Craft Crew could include technical, typographical, or photographic errors.
              </p>

              <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Governing Law</h2>
              <p className="text-gray-600 mb-6">
                These terms and conditions are governed by and construed in accordance with the laws and you irrevocably submit to the exclusive jurisdiction of the courts.
              </p>
            </div>

            <div className="mt-8 pt-8 border-t border-gray-200">
              <p className="text-center text-gray-600">
                For questions about these Terms of Service, please contact us at:
                <br />
                <a href="mailto:support@journalcraftcrew.com" className="text-indigo-600 hover:text-indigo-700">
                  support@journalcraftcrew.com
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsPage;