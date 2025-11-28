CREATE TABLE IF NOT EXISTS embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  namespace TEXT NOT NULL DEFAULT 'default',
  content TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  embedding VECTOR(1536) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_embeddings_namespace ON embeddings (namespace);
CREATE INDEX IF NOT EXISTS idx_embeddings_created_at ON embeddings (created_at);
CREATE INDEX IF NOT EXISTS idx_embeddings_metadata_gin ON embeddings USING GIN (metadata);
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_embeddings_vec_ivfflat') THEN
    EXECUTE 'CREATE INDEX idx_embeddings_vec_ivfflat ON embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);';
  END IF;
EXCEPTION WHEN OTHERS THEN
  RAISE NOTICE 'IVFFLAT not created';
END $$;
