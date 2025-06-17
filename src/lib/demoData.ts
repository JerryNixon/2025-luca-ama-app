import { Event, Question, User } from '@/types';

// Demo users
export const demoUsers: User[] = [
  {
    id: '1',
    email: 'demo@microsoft.com',
    name: 'Demo User',
    role: 'user',
  },
  {
    id: '2',
    email: 'presenter@microsoft.com',
    name: 'Jane Presenter',
    role: 'presenter',
  },
  {
    id: '3',
    email: 'moderator@microsoft.com',
    name: 'John Moderator',
    role: 'moderator',
  },
];

// Demo events
export const demoEvents: Event[] = [
  {
    id: '1',
    name: 'Microsoft Q4 All-Hands',
    openDate: new Date('2025-06-15T09:00:00'),
    closeDate: new Date('2025-06-20T17:00:00'),
    createdBy: '3',
    moderators: ['3'],
    participants: ['1', '2', '3'],
    shareLink: 'https://ama.microsoft.com/join/q4-all-hands',
    isActive: true,
    createdAt: new Date('2025-06-10T10:00:00'),
    updatedAt: new Date('2025-06-15T10:00:00'),
  },
  {
    id: '2',
    name: 'Azure Team Sync',
    openDate: new Date('2025-06-18T14:00:00'),
    closeDate: new Date('2025-06-18T16:00:00'),
    createdBy: '2',
    moderators: ['2', '3'],
    participants: ['1', '2', '3'],
    shareLink: 'https://ama.microsoft.com/join/azure-sync',
    isActive: true,
    createdAt: new Date('2025-06-12T14:00:00'),
    updatedAt: new Date('2025-06-16T14:00:00'),
  },
  {
    id: '3',
    name: 'Product Roadmap Discussion',
    openDate: new Date('2025-06-25T10:00:00'),
    closeDate: new Date('2025-06-25T12:00:00'),
    createdBy: '3',
    moderators: ['3'],
    participants: ['1', '2', '3'],
    shareLink: 'https://ama.microsoft.com/join/product-roadmap',
    isActive: false,
    createdAt: new Date('2025-06-14T10:00:00'),
    updatedAt: new Date('2025-06-14T10:00:00'),
  },
];

// Demo questions
export const demoQuestions: Question[] = [
  {
    id: '1',
    eventId: '1',
    text: 'What are the key priorities for Microsoft in 2025?',
    author: demoUsers[0],
    isAnonymous: false,
    upvotes: 15,
    hasUserUpvoted: false,
    isAnswered: false,
    isStarred: true,
    isStaged: true,
    presenterNotes: 'Focus on AI integration and cloud services',
    aiSummary: 'Question about Microsoft strategic priorities for the upcoming year',
    tags: ['strategy', 'priorities', '2025'],
    createdAt: new Date('2025-06-15T09:30:00'),
    updatedAt: new Date('2025-06-17T14:20:00'),
  },
  {
    id: '2',
    eventId: '1',
    text: 'How will the new AI features impact our daily workflow?',
    author: demoUsers[1],
    isAnonymous: false,
    upvotes: 12,
    hasUserUpvoted: true,
    isAnswered: true,
    isStarred: false,
    isStaged: false,
    aiSummary: 'Question about AI impact on workplace productivity',
    tags: ['ai', 'workflow', 'productivity'],
    createdAt: new Date('2025-06-15T10:15:00'),
    updatedAt: new Date('2025-06-16T11:30:00'),
  },
  {
    id: '3',
    eventId: '1',
    text: 'Can we expect more remote work flexibility policies?',
    author: demoUsers[0],
    isAnonymous: true,
    upvotes: 8,
    hasUserUpvoted: false,
    isAnswered: false,
    isStarred: false,
    isStaged: false,
    tags: ['remote-work', 'policy', 'flexibility'],
    createdAt: new Date('2025-06-15T11:00:00'),
    updatedAt: new Date('2025-06-15T11:00:00'),
  },
  {
    id: '4',
    eventId: '2',
    text: 'What are the latest updates on Azure security features?',
    author: demoUsers[2],
    isAnonymous: false,
    upvotes: 6,
    hasUserUpvoted: false,
    isAnswered: false,
    isStarred: true,
    isStaged: false,
    presenterNotes: 'Cover Zero Trust architecture and new compliance features',
    tags: ['azure', 'security', 'compliance'],
    createdAt: new Date('2025-06-16T09:00:00'),
    updatedAt: new Date('2025-06-16T09:00:00'),
  },
  {
    id: '5',
    eventId: '1',
    text: 'How is Microsoft handling sustainability initiatives?',
    author: demoUsers[1],
    isAnonymous: false,
    upvotes: 10,
    hasUserUpvoted: false,
    isAnswered: false,
    isStarred: false,
    isStaged: false,
    tags: ['sustainability', 'environment', 'corporate-responsibility'],
    createdAt: new Date('2025-06-15T12:30:00'),
    updatedAt: new Date('2025-06-15T12:30:00'),
  },
];

// Demo service for development
export const demoService = {
  // Current user simulation
  getCurrentUser: (): User => {
    return demoUsers[0]; // Default to demo user
  },

  // Authentication simulation
  login: async (email: string, password: string): Promise<{ user: User; token: string }> => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Find user by email
    const user = demoUsers.find(u => u.email === email);
    if (!user || password !== 'demo123') {
      throw new Error('Invalid credentials');
    }

    return {
      user,
      token: 'demo-jwt-token-' + user.id,
    };
  },

  // Events simulation
  getEvents: async (): Promise<Event[]> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return demoEvents;
  },

  getEvent: async (id: string): Promise<Event> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const event = demoEvents.find(e => e.id === id);
    if (!event) throw new Error('Event not found');
    return event;
  },

  // Questions simulation
  getQuestions: async (eventId: string): Promise<Question[]> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    return demoQuestions.filter(q => q.eventId === eventId);
  },

  createQuestion: async (eventId: string, text: string, isAnonymous: boolean): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const newQuestion: Question = {
      id: Date.now().toString(),
      eventId,
      text,
      author: demoUsers[0],
      isAnonymous,
      upvotes: 0,
      hasUserUpvoted: false,
      isAnswered: false,
      isStarred: false,
      isStaged: false,
      tags: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    demoQuestions.push(newQuestion);
    return newQuestion;
  },

  // Mock upvote toggle
  toggleUpvote: async (questionId: string): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const question = demoQuestions.find(q => q.id === questionId);
    if (!question) throw new Error('Question not found');

    if (question.hasUserUpvoted) {
      question.upvotes--;
      question.hasUserUpvoted = false;
    } else {
      question.upvotes++;
      question.hasUserUpvoted = true;
    }

    question.updatedAt = new Date();
    return question;
  },

  // Mock star toggle
  toggleStar: async (questionId: string): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const question = demoQuestions.find(q => q.id === questionId);
    if (!question) throw new Error('Question not found');

    question.isStarred = !question.isStarred;
    question.updatedAt = new Date();
    return question;
  },

  // Mock stage toggle
  toggleStage: async (questionId: string): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    // First, unstage any currently staged questions in the same event
    const question = demoQuestions.find(q => q.id === questionId);
    if (!question) throw new Error('Question not found');

    const eventQuestions = demoQuestions.filter(q => q.eventId === question.eventId);
    eventQuestions.forEach(q => {
      if (q.id !== questionId) {
        q.isStaged = false;
      }
    });

    question.isStaged = !question.isStaged;
    question.updatedAt = new Date();
    return question;
  },

  // Mock answer toggle
  toggleAnswer: async (questionId: string): Promise<Question> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const question = demoQuestions.find(q => q.id === questionId);
    if (!question) throw new Error('Question not found');

    question.isAnswered = !question.isAnswered;
    question.updatedAt = new Date();
    return question;
  },
};
