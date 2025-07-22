-- 🗄️ Quick SQL to Create Questions Table in Supabase
-- Run this in your Supabase SQL Editor to create the table

-- Create questions table
CREATE TABLE IF NOT EXISTS public.questions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    text TEXT NOT NULL,
    upvotes INTEGER DEFAULT 0,
    is_answered BOOLEAN DEFAULT false,
    is_anonymous BOOLEAN DEFAULT true,
    author_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- Enable Row Level Security (for authentication later)
ALTER TABLE public.questions ENABLE ROW LEVEL SECURITY;

-- Create policy to allow anonymous users to read/write (for testing)
CREATE POLICY "Allow anonymous access" ON public.questions
    FOR ALL USING (true);

-- Insert some sample data
INSERT INTO public.questions (text, upvotes, is_answered) VALUES 
    ('How does Supabase compare to Django?', 5, false),
    ('What are the benefits of REST APIs?', 3, false),
    ('Can I build a full app without a backend?', 8, true);

-- Verify the table was created
SELECT * FROM public.questions;
