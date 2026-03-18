-- InfraSight — Supabase schema migration
-- Run this in the Supabase SQL Editor or via the Supabase CLI

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────
-- Table: detections
-- ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.detections (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id             UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_image_url  TEXT NOT NULL,
    processed_image_url TEXT,
    algorithm           TEXT NOT NULL CHECK (algorithm IN ('DW-LCM', 'MW-IPI')),
    status              TEXT NOT NULL DEFAULT 'processing'
                            CHECK (status IN ('processing', 'completed', 'failed')),
    targets             JSONB DEFAULT '[]'::jsonb,
    target_count        INTEGER DEFAULT 0,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER detections_updated_at
    BEFORE UPDATE ON public.detections
    FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ─────────────────────────────────────────────
-- Row-Level Security (RLS)
-- ─────────────────────────────────────────────
ALTER TABLE public.detections ENABLE ROW LEVEL SECURITY;

-- Users can only see their own detections
CREATE POLICY "Users can read own detections"
    ON public.detections FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own detections
CREATE POLICY "Users can insert own detections"
    ON public.detections FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own detections
CREATE POLICY "Users can update own detections"
    ON public.detections FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can delete their own detections
CREATE POLICY "Users can delete own detections"
    ON public.detections FOR DELETE
    USING (auth.uid() = user_id);

-- Service role bypass (used by gateway service via service-role key)
CREATE POLICY "Service role full access"
    ON public.detections
    USING (auth.role() = 'service_role');

-- ─────────────────────────────────────────────
-- Storage bucket: infrared-images
-- ─────────────────────────────────────────────
INSERT INTO storage.buckets (id, name, public)
VALUES ('infrared-images', 'infrared-images', true)
ON CONFLICT (id) DO NOTHING;

-- Allow authenticated users to upload to their own folder
CREATE POLICY "Authenticated users can upload images"
    ON storage.objects FOR INSERT
    WITH CHECK (
        bucket_id = 'infrared-images'
        AND auth.role() = 'authenticated'
    );

-- Allow public read of processed images
CREATE POLICY "Public can read infrared images"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'infrared-images');

-- Users can delete their own files
CREATE POLICY "Users can delete own images"
    ON storage.objects FOR DELETE
    USING (
        bucket_id = 'infrared-images'
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- ─────────────────────────────────────────────
-- Indexes
-- ─────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_detections_user_id    ON public.detections(user_id);
CREATE INDEX IF NOT EXISTS idx_detections_created_at ON public.detections(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_detections_status     ON public.detections(status);
