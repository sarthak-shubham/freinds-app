-- Create the private bucket (if it doesn't exist)
INSERT INTO storage.buckets (id, name, public) 
VALUES ('stories', 'stories', false) 
ON CONFLICT (id) DO NOTHING;

-- Cleanup old policies to make this script rerunnable
DROP POLICY IF EXISTS "Users can upload their own story images" ON storage.objects;
DROP POLICY IF EXISTS "Story images are visible to owners and close friends" ON storage.objects;
DROP POLICY IF EXISTS "Users can delete their own story images" ON storage.objects;

-- 1. UPLOAD POLICY: Users can only upload files to the 'stories' bucket, and they are marked as the owner
CREATE POLICY "Users can upload their own story images" 
ON storage.objects FOR INSERT TO authenticated 
WITH CHECK (bucket_id = 'stories' AND auth.uid() = owner);

-- 2. READ POLICY: Users can download the file if they own it, OR if they are in the close_friends table
CREATE POLICY "Story images are visible to owners and close friends" 
ON storage.objects FOR SELECT TO authenticated 
USING (
    bucket_id = 'stories' AND (
        auth.uid() = owner 
        OR 
        EXISTS (
            SELECT 1 FROM public.close_friends
            WHERE close_friends.owner_id = storage.objects.owner
            AND close_friends.member_id = auth.uid()
        )
    )
);

-- 3. DELETE/UPDATE POLICY: Only the owner can remove/replace their image
CREATE POLICY "Users can manage their own story images" 
ON storage.objects FOR ALL TO authenticated 
USING (bucket_id = 'stories' AND auth.uid() = owner);