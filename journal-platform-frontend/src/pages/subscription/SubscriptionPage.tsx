import React from 'react';
import { ArrowLeftIcon, StarIcon, CheckIcon } from '@heroicons/react/24/outline';
import { Button } from '@/components/ui/Button';

const SubscriptionPage: React.FC = () => {
  const plans = [
    {
      name: 'Free',
      price: '$0',
      description: 'Perfect for getting started',
      features: [
        '3 AI-generated journals per month',
        'Basic themes and templates',
        'Standard export options',
        'Community support'
      ],
      cta: 'Current Plan',
      disabled: false,
      popular: false
    },
    {
      name: 'Premium',
      price: '$19',
      description: 'For serious journal creators',
      features: [
        'Unlimited AI-generated journals',
        'Premium themes and templates',
        'Advanced customization options',
        'Priority AI processing',
        'Export in multiple formats',
        'Email support'
      ],
      cta: 'Current Plan',
      disabled: false,
      popular: true
    },
    {
      name: 'Team',
      price: '$49',
      description: 'For teams and organizations',
      features: [
        'Everything in Premium',
        'Collaborative journals',
        'Team dashboard',
        'Custom integrations',
        'Priority phone support',
        'Advanced analytics'
      ],
      cta: 'Contact Sales',
      disabled: false,
      popular: false
    }
  ];

  return (
    <div className="min-h-screen gradient-bg">
      <div className="section-container py-8">
        <div className="mb-8">
          <Button
            variant="ghost"
            onClick={() => window.history.back()}
            className="mb-4"
          >
            <ArrowLeftIcon className="h-4 w-4 mr-2" />
            Back
          </Button>

          <h1 className="text-4xl font-bold gradient-text mb-2">Subscription Plans</h1>
          <p className="text-lg text-gray-600">Choose the plan that works best for your journaling needs</p>
        </div>

        <div className="grid gap-8 lg:grid-cols-3 mb-12">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`glass-effect rounded-2xl border p-8 hover:shadow-lg transition-all duration-200 ${
                plan.popular
                  ? 'border-color-primary ring-2 ring-color-primary/20'
                  : 'border-color-border'
              }`}
            >
              {plan.popular && (
                <div className="flex items-center justify-center mb-4">
                  <span className="bg-gradient-to-r from-amber-100 to-orange-100 text-amber-800 px-4 py-2 rounded-full text-sm font-semibold flex items-center gap-2">
                    <StarIcon className="h-4 w-4" />
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-8">
                <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold">{plan.price}</span>
                  <span className="text-gray-600">/month</span>
                </div>
                <p className="text-gray-600">{plan.description}</p>
              </div>

              <ul className="space-y-4 mb-8">
                {plan.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <CheckIcon className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                variant={plan.popular ? 'primary' : 'outline'}
                className="w-full"
                disabled={plan.disabled}
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>

        <div className="text-center">
          <div className="inline-flex items-center gap-3 p-6 bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl border border-green-200">
            <div className="text-left">
              <p className="font-semibold text-green-800">🎉 You are currently on the Premium plan!</p>
              <p className="text-sm text-green-600">Enjoy unlimited AI journal creation and all premium features</p>
            </div>
            <Button onClick={() => window.location.href = '/dashboard'}>
              Go to Dashboard
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubscriptionPage;