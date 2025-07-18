
-- 1. set trigger
SELECT
    'CREATE TRIGGER before_update BEFORE UPDATE ON '
    || tablename || ' '
    || 'FOR EACH ROW EXECUTE FUNCTION set_updated_time();'
FROM (
    SELECT
        table_name AS tablename
    FROM
        information_schema.tables
    WHERE column_name = 'updated_time'
        AND table_schema = 'public'
    GROUP BY table_name;
) AS tables;

-- updated_time 자동 갱신 트리거 함수
CREATE OR REPLACE FUNCTION set_updated_time() 
RETURNS trigger AS $set_updated_time$
    BEGIN
        NEW.updated_time := current_timestamp::timestamp(0);
        RETURN NEW;
    END;
$set_updated_time$ LANGUAGE plpgsql;

-- 2. create tables
-- 유저 정보
-- 샵 매니저 / 디자이너 / 일반 고객

CREATE TABLE "public"."users" (
    "seq" SERIAL PRIMARY KEY, 
    "id" VARCHAR(50) UNIQUE NOT NULL, 
    "user_type" VARCHAR(10) NOT NULL,
    "name" VARCHAR(100) NOT NULL, 
    "hashed_password" VARCHAR NOT NULL, 
    "phone_number" VARCHAR(20) UNIQUE,
    "created_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    "updated_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0)
);

COMMENT ON COLUMN "public"."users"."seq" IS 'users 테이블의 고유 시퀀스';
COMMENT ON COLUMN "public"."users"."id" IS '사용자 고유 ID';
COMMENT ON COLUMN "public"."users"."user_type" IS 'shop, designer, customer';
COMMENT ON COLUMN "public"."users"."name" IS '사용자 이름';
COMMENT ON COLUMN "public"."users"."hashed_password" IS '사용자 비밀번호';
COMMENT ON COLUMN "public"."users"."phone_number" IS '휴대폰 번호';
COMMENT ON COLUMN "public"."users"."created_time" IS '생성 시간';
COMMENT ON COLUMN "public"."users"."updated_time" IS '최종 수정 시간';

CREATE TRIGGER before_update BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION set_updated_time();

-- 샵 정보
-- 샵 고유 ID / 샵 이름 / 샵 전화번호 / 사업자등록번호 / 생성일시 / 수정일시

CREATE TABLE  "public"."shops" (
    seq SERIAL PRIMARY KEY, 
    id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    number VARCHAR(20) NOT NULL,
    biz_number VARCHAR(20) NOT NULL,
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    updated_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
);

COMMENT ON COLUMN shops.seq IS 'shops테이블의 고유 시퀀스';
COMMENT ON COLUMN shops.id IS '샵 고유 ID';
COMMENT ON COLUMN shops.name IS '샵 이름';
COMMENT ON COLUMN shops.number IS '샵 전화번호';
COMMENT ON COLUMN shops.biz_number IS '사업자등록번호';
COMMENT ON COLUMN shops.created_time IS '생성일시';
COMMENT ON COLUMN shops.updated_time IS '수정일시';

-- updated_time 자동 갱신 트리거
CREATE TRIGGER before_update_shops
    BEFORE UPDATE ON shops
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_time();

-- 디자이너 정보
-- 디자이너 고유 ID / 디자이너 이름 / 디자이너 전화번호 / 생성일시 / 수정일시

CREATE TABLE  "public"."designers" (
    seq SERIAL PRIMARY KEY, 
    id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    belonging_shop_id VARCHAR(50), -- 소속 샵
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    updated_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    memo VARCHAR(4000),
    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (belonging_shop_id) REFERENCES shops(id)
);

COMMENT ON COLUMN designers.seq IS 'designers 테이블의 고유 시퀀스';
COMMENT ON COLUMN designers.id IS '디자이너 고유 id';
COMMENT ON COLUMN designers.name IS '디자이너 이름';
COMMENT ON COLUMN designers.is_active IS '디자이너 활성화 여부';
COMMENT ON COLUMN designers.belonging_shop_id IS '소속된 샵의 id';
COMMENT ON COLUMN designers.created_time IS '생성일시';
COMMENT ON COLUMN designers.updated_time IS '수정일시';
COMMENT ON COLUMN designers.memo IS '메모';

-- updated_time 자동 갱신 트리거
CREATE TRIGGER before_update_designers
    BEFORE UPDATE ON designers
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_time();

-- 고객-디자이너 매핑 테이블 (N:M 관계)
CREATE TABLE customer_designer_mapping (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL, -- users.id (user_type=customer)
    designer_id VARCHAR(50) NOT NULL, -- users.id (user_type=designer)
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 요청 상태: pending, accepted, rejected
    requested_by VARCHAR(50) NOT NULL, -- 요청자 (디자이너)
    requested_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    responded_time TIMESTAMP,          -- 고객이 수락/거절한 시간
    memo  VARCHAR(4000),                        -- 비고/메모
    
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_designer FOREIGN KEY (designer_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 인덱스: 한 고객-디자이너 쌍은 중복 불가
CREATE UNIQUE INDEX uq_customer_designer ON customer_designer_mapping (customer_id, designer_id);

-- 디폴트(공통) 항목 ex. 얼굴형 - 계란형, 다이아몬드형, ...
CREATE TABLE chart_item_default_options (
    id VARCHAR(100) PRIMARY KEY, -- default + seq 형태 (예: default_face_shape_001)
    category_id VARCHAR(50) NOT NULL, -- ex. face_shape
    category_name VARCHAR(50) NOT NULL, -- ex. 얼굴형
    option_name VARCHAR(100) NOT NULL, -- ex. 계란형, 다이아몬드형
    image_source VARCHAR(500)
);
CREATE UNIQUE INDEX uq_category_option ON public.chart_item_default_options USING btree (category_id, option_name);


-- 사용자별 카테고리별 시퀀스 관리 테이블
CREATE TABLE user_category_sequence (
    user_id VARCHAR(50) NOT NULL,
    category_id VARCHAR(50) NOT NULL,
    current_seq INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, category_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 유저별 커스텀 항목 테이블
CREATE TABLE chart_item_user_options (
    id VARCHAR(100) PRIMARY KEY, -- userId + seq 형태 (예: user123_face_shape_001)
    user_id VARCHAR(50) NOT NULL,
    category_id VARCHAR(50) NOT NULL, -- ex. face_shape
    category_name VARCHAR(50) NOT NULL, -- ex. 얼굴형
    option_name VARCHAR(100) NOT NULL, -- ex. 계란형, 다이아몬드형
    image_source VARCHAR(500),
    created_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    updated_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX uq_user_category_option ON public.chart_item_user_options USING btree (user_id, category_id, option_name);

-- 시퀀스 생성을 위한 함수
CREATE OR REPLACE FUNCTION generate_user_option_id()
RETURNS TRIGGER AS $$
DECLARE
    next_seq INTEGER;
BEGIN
    -- 시퀀스 테이블에서 현재 시퀀스 값을 가져오거나 새로 생성
    INSERT INTO user_category_sequence (user_id, category_id, current_seq)
    VALUES (NEW.user_id, NEW.category_id, 1)
    ON CONFLICT (user_id, category_id)
    DO UPDATE SET current_seq = user_category_sequence.current_seq + 1
    RETURNING current_seq INTO next_seq;
    
    -- ID 생성: userId_categoryId_seq 형태
    NEW.id := NEW.user_id || '_' || NEW.category_id || '_' || LPAD(next_seq::TEXT, 3, '0');
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
CREATE TRIGGER trigger_generate_user_option_id
    BEFORE INSERT ON chart_item_user_options
    FOR EACH ROW
    EXECUTE FUNCTION generate_user_option_id();

-- updated_time 자동 갱신 트리거
CREATE TRIGGER before_update_chart_item_user_options
    BEFORE UPDATE ON chart_item_user_options
    FOR EACH ROW
    EXECUTE FUNCTION set_updated_time();

