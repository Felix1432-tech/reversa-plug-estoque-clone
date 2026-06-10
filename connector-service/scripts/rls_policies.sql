-- Row Level Security policies for Supabase
-- Execute this in the Supabase SQL editor after running migrations

-- distributor_configs
ALTER TABLE distributor_configs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users manage own distributor configs"
  ON distributor_configs
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- products (via join with distributor_configs)
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own products"
  ON products
  FOR SELECT
  USING (
    distributor_config_id IN (
      SELECT id FROM distributor_configs WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Service role manages products"
  ON products
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');

-- connector_logs (via join with distributor_configs)
ALTER TABLE connector_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own logs"
  ON connector_logs
  FOR SELECT
  USING (
    distributor_config_id IN (
      SELECT id FROM distributor_configs WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Service role manages logs"
  ON connector_logs
  FOR ALL
  USING (auth.role() = 'service_role')
  WITH CHECK (auth.role() = 'service_role');
