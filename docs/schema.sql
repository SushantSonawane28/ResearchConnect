-- PostgreSQL version of the schema (for your report / ER diagram / manual setup).
-- The app creates these tables automatically from backend/app/models.py,
-- so you do NOT need to run this file unless you want to set up by hand.

CREATE TABLE organizations (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) UNIQUE NOT NULL,
  org_type VARCHAR(20) NOT NULL DEFAULT 'college'      -- college | university | company
);

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(200) UNIQUE NOT NULL,
  password_hash VARCHAR(200) NOT NULL,
  role VARCHAR(20) NOT NULL DEFAULT 'researcher',      -- researcher | coordinator | industry | admin
  organization_id INT NOT NULL REFERENCES organizations(id),
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_users_email ON users(email);

CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL
);

CREATE TABLE profiles (
  id SERIAL PRIMARY KEY,
  user_id INT UNIQUE NOT NULL REFERENCES users(id),
  bio TEXT DEFAULT '',
  department VARCHAR(120) DEFAULT '',
  designation VARCHAR(120) DEFAULT '',
  visibility VARCHAR(10) DEFAULT 'public',             -- org | public
  looking_for_collab BOOLEAN DEFAULT TRUE,
  collab_area VARCHAR(200) DEFAULT '',
  email_alerts BOOLEAN DEFAULT TRUE                     -- consent to receive match emails
);

CREATE TABLE profile_tags (
  profile_id INT REFERENCES profiles(id) ON DELETE CASCADE,
  tag_id INT REFERENCES tags(id),
  kind VARCHAR(10),                                    -- skill | interest | expertise
  PRIMARY KEY (profile_id, tag_id, kind)
);
CREATE INDEX ix_profile_tags_tag ON profile_tags(tag_id);

CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  owner_id INT NOT NULL REFERENCES users(id),
  title VARCHAR(200) NOT NULL,
  description TEXT DEFAULT '',
  domain VARCHAR(120) DEFAULT '',
  status VARCHAR(20) DEFAULT 'ongoing',
  visibility VARCHAR(10) DEFAULT 'public',
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_projects_domain ON projects(domain);

CREATE TABLE project_tags (
  project_id INT REFERENCES projects(id) ON DELETE CASCADE,
  tag_id INT REFERENCES tags(id),
  PRIMARY KEY (project_id, tag_id)
);

CREATE TABLE opportunities (
  id SERIAL PRIMARY KEY,
  posted_by INT NOT NULL REFERENCES users(id),
  title VARCHAR(200) NOT NULL,
  description TEXT DEFAULT '',
  domain VARCHAR(120) DEFAULT '',
  opp_type VARCHAR(30) DEFAULT 'funding',              -- funding | conference | workshop | industry_challenge
  deadline TIMESTAMP,
  visibility VARCHAR(10) DEFAULT 'public'
);
CREATE INDEX ix_opportunities_deadline ON opportunities(deadline);

CREATE TABLE collaboration_requests (
  id SERIAL PRIMARY KEY,
  sender_id INT NOT NULL REFERENCES users(id),
  receiver_id INT NOT NULL REFERENCES users(id),
  project_id INT REFERENCES projects(id),
  message TEXT DEFAULT '',
  status VARCHAR(10) DEFAULT 'pending',                -- pending | accepted | rejected
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_requests_receiver ON collaboration_requests(receiver_id);

CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id),
  message VARCHAR(300) NOT NULL,
  kind VARCHAR(30) DEFAULT 'info',
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX ix_notifications_user ON notifications(user_id);

CREATE TABLE relevance_labels (                        -- faculty judgements = ground truth for evaluation
  id SERIAL PRIMARY KEY,
  user_a INT NOT NULL REFERENCES users(id),
  user_b INT NOT NULL REFERENCES users(id),
  relevant BOOLEAN NOT NULL,
  judged_by VARCHAR(120) DEFAULT ''
);

CREATE TABLE match_alerts (                            -- pairs already emailed, so nobody gets repeats
  id SERIAL PRIMARY KEY,
  user_low INT NOT NULL REFERENCES users(id),
  user_high INT NOT NULL REFERENCES users(id),
  score FLOAT NOT NULL,
  email_status VARCHAR(40) DEFAULT '',
  sent_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT uq_match_alert_pair UNIQUE (user_low, user_high)
);
