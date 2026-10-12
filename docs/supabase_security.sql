-- SUPABASE ONLY. Run in: Supabase dashboard -> SQL Editor.
-- The app already does this automatically on start-up (ENABLE_RLS=true), so this file is your manual backup.
-- Why: Supabase can publish tables through a public web API. Our users table holds password hashes,
-- so we switch on Row Level Security with no policies. The public API then returns nothing,
-- while our FastAPI backend (connecting as the database owner) still has full access.

ALTER TABLE organizations           ENABLE ROW LEVEL SECURITY;
ALTER TABLE users                   ENABLE ROW LEVEL SECURITY;
ALTER TABLE tags                    ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles                ENABLE ROW LEVEL SECURITY;
ALTER TABLE profile_tags            ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects                ENABLE ROW LEVEL SECURITY;
ALTER TABLE project_tags            ENABLE ROW LEVEL SECURITY;
ALTER TABLE opportunities           ENABLE ROW LEVEL SECURITY;
ALTER TABLE collaboration_requests  ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications           ENABLE ROW LEVEL SECURITY;
ALTER TABLE relevance_labels        ENABLE ROW LEVEL SECURITY;
ALTER TABLE match_alerts            ENABLE ROW LEVEL SECURITY;
