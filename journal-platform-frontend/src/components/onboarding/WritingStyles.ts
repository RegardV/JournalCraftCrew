// Writing style classifications for journal themes (copyright-free)

export const getWritingStylesForTheme = (theme: string) => {
  const styleMap = {
    'mindfulness': [
      {
        name: 'Zen Contemplative Style',
        style: 'Gentle presence with mindful awareness and compassionate observation',
        examples: ['Breathing in, I calm my body and mind...', 'Return to your true home in the present moment...', 'Walk as if you are kissing the Earth with each step...']
      },
      {
        name: 'Scientific Mindfulness Approach',
        style: 'Evidence-based mindfulness with focus on present moment awareness and non-judgmental observation',
        examples: ['Notice what\'s arising in this moment without judgment...', 'Bring curiosity to your experience...', 'There is more right with you than wrong with you...']
      },
      {
        name: 'Compassionate Psychology Style',
        style: 'Buddhist psychology with radical compassion and acceptance of imperfection',
        examples: ['Allow this moment to be exactly as it is...', 'Recognize the belonging that\'s already here...', 'Trust in your basic goodness and wisdom...']
      },
      {
        name: 'Wisdom Teaching Method',
        style: 'Ancient wisdom with gentle encouragement to stay with difficult emotions',
        examples: ['Stay with the discomfort and let it teach you...', 'Lean into the sharp points of life...', 'This very moment is the perfect teacher...']
      },
      {
        name: 'Heart-Centered Narrative',
        style: 'Story-based wisdom with practical insights and emotional intelligence',
        examples: ['The heart knows the way when the mind is unclear...', 'Your troubles are blessings in disguise...', 'Compassion is our true nature...']
      }
    ],
    'productivity': [
      {
        name: 'Atomic Habits Method',
        style: 'Small improvements focus with systems thinking and identity-based change',
        examples: ['What 1% improvement can you make today?', 'Build systems, not just goals...', 'Your habits shape your identity and future...']
      },
      {
        name: 'Deep Work Philosophy',
        style: 'Focused concentration with emphasis on eliminating distractions and digital minimalism',
        examples: ['What deep work will you accomplish today?', 'Eliminate shallow work and protect your focus...', 'Focus is the new IQ in our distracted world...']
      },
      {
        name: 'Efficiency Optimization',
        style: 'Biohacking approach with emphasis on lifestyle optimization and rapid learning',
        examples: ['What\'s the 80/20 of this task or project?', 'Test assumptions and measure everything...', 'Less is more when it comes to productivity...']
      },
      {
        name: 'Principle-Driven Effectiveness',
        style: 'Mission-oriented with focus on what truly matters and time management wisdom',
        examples: ['Begin with the end in mind and work backwards...', 'What are your highest priorities right now?', 'Sharpen the saw to maintain effectiveness...']
      },
      {
        name: 'Externalized System Approach',
        style: 'Getting Things Done methodology with focus on capturing and organizing commitments',
        examples: ['What\'s your very next action?', 'Capture everything in a trusted system...', 'Your mind is for having ideas, not holding them...']
      }
    ],
    'self development': [
      {
        name: 'Growth Mindset Framework',
        style: 'Continuous improvement with focus on potential development and learning from challenges',
        examples: ['What can you learn from this experience?', 'Embrace challenges as opportunities...', 'Your abilities can be developed through dedication...']
      },
      {
        name: 'Habit Formation Science',
        style: 'Behavioral psychology with emphasis on building positive routines and breaking negative patterns',
        examples: ['What small habit will transform your life?', 'Consistency beats intensity every time...', 'Your identity follows your actions...']
      },
      {
        name: 'Neuroscience-Based Optimization',
        style: 'Brain performance with focus on protocols and biological enhancement',
        examples: ['How can you optimize your cognitive performance today?', 'Use morning sunlight to set your rhythm...', 'Leverage your nervous system for peak performance...']
      },
      {
        name: 'Values-Driven Living',
        style: 'Purpose-centered approach with focus on alignment and meaningful action',
        examples: ['What matters most to you right now?', 'Live in accordance with your core values...', 'Authenticity creates lasting fulfillment...']
      },
      {
        name: 'Resilience Training Method',
        style: 'Mental toughness with emphasis on bouncing back and emotional regulation',
        examples: ['How can you grow stronger through this challenge?', 'Adaptability is the key to thriving...', 'Every setback contains a gift...']
      }
    ],
    'creativity': [
      {
        name: 'Magical Curiosity Style',
        style: 'Fearless creativity with relationship to inspiration and wonder',
        examples: ['What does your creative genius want today?', 'Make things for the delight of making them...', 'Your creativity is a gift to be shared...']
      },
      {
        name: 'Remix Culture Method',
        style: 'Modern appropriation art with emphasis on remixing and sharing creative work',
        examples: ['What can you remix and transform today?', 'Share your creative process with others...', 'Creativity is often about subtraction...']
      },
      {
        name: 'Disciplined Practice Approach',
        style: 'Creative habits and rituals with focus on consistency and artistic practice',
        examples: ['What creative muscle will you strengthen today?', 'Show up and do the work regardless of mood...', 'Creativity flourishes through consistent practice...']
      },
      {
        name: 'Minimal Essence Style',
        style: 'Mystical minimalism with focus on removing obstacles to reveal core creativity',
        examples: ['What can you remove to reveal the essential idea?', 'The creation already exists within you...', 'Become a conduit for creative flow...']
      },
      {
        name: 'Spiritual Recovery Method',
        style: 'Inner artist work with focus on morning pages and creative unblocking',
        examples: ['What does your inner artist need today?', 'Take yourself on an artist date...', 'Creativity is a spiritual path of self-discovery...']
      }
    ],
    'gratitude': [
      {
        name: 'Research-Based Gratitude',
        style: 'Scientific approach with vulnerability and wholehearted living practices',
        examples: ['What are you grateful for right now, in this moment?', 'Practice gratitude even when it feels difficult...', 'Gratitude helps make sense of our past experiences...']
      },
      {
        name: 'Inspirational Storytelling',
        style: 'Personal transformation with narrative emphasis and uplifting messages',
        examples: ['What\'s your gratitude list for today?', 'Turn your wounds into wisdom and strength...', 'Thank you is the simplest yet most powerful prayer...']
      },
      {
        name: 'Beauty Awareness Method',
        style: 'Photographic gratitude with focus on natural beauty and mindful observation',
        examples: ['Notice the beauty in this ordinary moment...', 'Gratitude unlocks the fullness of everyday life...', 'Open your eyes to wonder and appreciation...']
      },
      {
        name: 'Spiritual Abundance Style',
        style: 'Consciousness-based gratitude with awareness of natural abundance',
        examples: ['What abundance already surrounds you?', 'Gratitude opens the heart to receive more...', 'Be present in the miracle of this very life...']
      },
      {
        name: 'Self-Compassion Practice',
        style: 'Mindful acceptance with gratitude for imperfection and personal growth',
        examples: ['How can you be kind to yourself today?', 'Embrace your shared humanity with others...', 'Self-compassion is a profound form of gratitude...']
      }
    ]
  };

  // Default styles for any theme
  const defaultStyles = [
    {
      name: 'Contemporary Inspirational',
      style: 'Modern motivational writing with personal growth emphasis and actionable wisdom',
      examples: ['What growth will you consciously choose today?', 'Your potential is truly limitless...', 'Every single day is a new beginning...']
    },
    {
      name: 'Practical Scientific',
      style: 'Evidence-based approach with research-backed insights and measurable results',
      examples: ['What does current research reveal about this?', 'Trust the proven process...', 'When data meets ancient wisdom...']
    },
    {
      name: 'Mindful Contemplative',
      style: 'Thoughtful reflection with present moment awareness and inner peace',
      examples: ['What is present in this very moment?', 'Breathe deeply and simply notice...', 'Stillness often speaks the loudest...']
    },
    {
      name: 'Action-Oriented',
      style: 'Dynamic approach with emphasis on doing, implementing, and creating momentum',
      examples: ['What immediate action will you take today?', 'Small consistent steps create massive results...', 'Progress always beats perfection...']
    },
    {
      name: 'Holistic Integration',
      style: 'Balanced approach combining mind, body, and spiritual wellness practices',
      examples: ['How can you nurture your whole self today?', 'True health integrates all aspects of being...', 'Wellness is a journey, not a destination...']
    }
  ];

  return styleMap[theme] || defaultStyles;
};