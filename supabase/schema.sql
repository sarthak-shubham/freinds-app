-- ==========================================
-- 0. CLEANUP (Makes this script rerunnable)
-- ==========================================
DROP TABLE IF EXISTS public.stories CASCADE;
DROP TABLE IF EXISTS public.close_friends CASCADE;

-- ==========================================
-- 1. TABLE DEFINITIONS
-- ==========================================
CREATE TABLE public.stories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    -- THE FIX: Added UNIQUE so a user can only ever have 1 active story in the DB
    owner_id UUID REFERENCES auth.users(id) NOT NULL UNIQUE, 
    image_url TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE public.close_friends (
    owner_id UUID REFERENCES auth.users(id) NOT NULL,
    member_id UUID REFERENCES auth.users(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (owner_id, member_id)
);

-- ==========================================
-- 2. ENABLE ROW LEVEL SECURITY (RLS)
-- ==========================================
ALTER TABLE public.stories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.close_friends ENABLE ROW LEVEL SECURITY;

-- ==========================================
-- 3. RLS POLICIES FOR 'close_friends'
-- ==========================================
CREATE POLICY "Users can view close friends list rows related to them"
ON public.close_friends FOR SELECT
USING (auth.uid() = owner_id OR auth.uid() = member_id);

CREATE POLICY "Users can manage their own close friends list"
ON public.close_friends FOR ALL
USING (auth.uid() = owner_id);

-- ==========================================
-- 4. RLS POLICIES FOR 'stories'
-- ==========================================
CREATE POLICY "Users can manage their own stories"
ON public.stories FOR ALL
USING (auth.uid() = owner_id);

CREATE POLICY "Stories are visible to owners and close friends"
ON public.stories FOR SELECT
USING (
    auth.uid() = owner_id 
    OR 
    EXISTS (
        SELECT 1 FROM public.close_friends
        WHERE close_friends.owner_id = stories.owner_id
        AND close_friends.member_id = auth.uid()
    )
);