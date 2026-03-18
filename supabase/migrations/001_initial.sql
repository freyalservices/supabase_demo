-- ================================================================
-- InfraSight — Initial Database Schema
-- Apply in Supabase SQL Editor or via supabase db push
-- ================================================================

-- Detections table: stores metadata for each image detection run
CREATE TABLE IF NOT EXISTS public.detections (
    id                  UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id             UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_image_url  TEXT        NOT NULL,
    processed_image_url TEXT,
    algorithm           TEXT        NOT NULL DEFAULT 'DW-LCM'
                            CHECK (algorithm IN ('DW-LCM', 'MW-IPI')),
    status              TEXT        NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    targets             JSONB,
    target_count        INTEGER     DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at          TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Automatically keep updated_at current
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_detections_updated_at
    BEFORE UPDATE ON public.detections
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Index for fast per-user lookups ordered by newest first
CREATE INDEX IF NOT EXISTS idx_detections_user_created
    ON public.detections (user_id, created_at DESC);

-- ================================================================
-- Row Level Security — users can only access their own rows
-- ================================================================
ALTER TABLE public.detections ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can select own detections"
    ON public.detections FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own detections"
    ON public.detections FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own detections"
    ON public.detections FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own detections"
    ON public.detections FOR DELETE
    USING (auth.uid() = user_id);

-- ================================================================
-- Storage bucket: infrared-images (run in Supabase dashboard or
-- via supabase storage commands if using the CLI)
-- ================================================================
-- INSERT INTO storage.buckets (id, name, public)
-- VALUES ('infrared-images', 'infrared-images', true)
-- ON CONFLICT (id) DO NOTHING;
