-- ============================================
-- Viewo SQLite Database Schema
-- ============================================

-- 부서 테이블 (departments.json 데이터용)
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    building TEXT NOT NULL,                -- 건물 (본관, 별관1동, 별관2동 등)
    floor TEXT NOT NULL,                   -- 층 (1층, 2층, 3층 등)
    department TEXT NOT NULL,              -- 부서명 (기획감사실, 미래전략실 등)
    team TEXT,                             -- 팀명 (기획팀, 예산팀 등) - NULL 가능
    position TEXT NOT NULL,                -- 직급 (실장, 팀장, 과장, 주무관 등)
    task TEXT,                             -- 담당업무 설명
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 부서 검색을 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_departments_building ON departments(building);
CREATE INDEX IF NOT EXISTS idx_departments_floor ON departments(floor);
CREATE INDEX IF NOT EXISTS idx_departments_department ON departments(department);
CREATE INDEX IF NOT EXISTS idx_departments_team ON departments(team);

-- ============================================
-- 어드민 토큰 관리 테이블
-- ============================================

-- 어드민 계정 테이블
CREATE TABLE IF NOT EXISTS admin_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,         -- 로그인 ID
    password_hash TEXT NOT NULL,           -- 비밀번호 해시 (bcrypt 등)
    name TEXT NOT NULL,                    -- 관리자 이름
    email TEXT,                            -- 이메일
    role TEXT DEFAULT 'admin',             -- 역할 (admin, super_admin 등)
    is_active INTEGER DEFAULT 1,           -- 활성화 상태 (1=활성, 0=비활성)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP                -- 마지막 로그인 시간
);

-- Refresh Token 테이블
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,             -- 연결된 어드민 ID
    token_hash TEXT NOT NULL UNIQUE,       -- Refresh Token 해시값
    device_info TEXT,                      -- 디바이스 정보 (User-Agent 등)
    ip_address TEXT,                       -- 접속 IP
    is_revoked INTEGER DEFAULT 0,          -- 취소 여부 (1=취소됨, 0=유효)
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 발급 시간
    expires_at TIMESTAMP NOT NULL,         -- 만료 시간
    revoked_at TIMESTAMP,                  -- 취소 시간 (취소된 경우)
    FOREIGN KEY (admin_id) REFERENCES admin_users(id) ON DELETE CASCADE
);

-- Refresh Token 조회를 위한 인덱스
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_admin_id ON refresh_tokens(admin_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token_hash ON refresh_tokens(token_hash);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);

-- ============================================
-- 토큰 블랙리스트 (로그아웃된 Access Token 관리용 - 선택적)
-- ============================================

CREATE TABLE IF NOT EXISTS token_blacklist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_jti TEXT NOT NULL UNIQUE,        -- JWT ID (jti claim)
    expires_at TIMESTAMP NOT NULL,         -- 토큰 원래 만료 시간
    blacklisted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_token_blacklist_jti ON token_blacklist(token_jti);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires ON token_blacklist(expires_at);
