-- 고객정보 날짜 / 이름 / ID / 고객번호(전화번호)

CREATE TABLE "public"."users" (
    "seq" SERIAL PRIMARY KEY, 
    "id" VARCHAR(50) UNIQUE NOT NULL, 
    "name" VARCHAR(100) NOT NULL, 
    "password" VARCHAR NOT NULL, 
    "phone_number" VARCHAR(20) UNIQUE,
    "created_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    "updated_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    "memo" VARCHAR
);

COMMENT ON COLUMN "public"."users"."seq" IS 'auto_increment sequence';
COMMENT ON COLUMN "public"."users"."id" IS 'user id';
COMMENT ON COLUMN "public"."users"."name" IS 'customer name';
COMMENT ON COLUMN "public"."users"."password" IS 'user password';
COMMENT ON COLUMN "public"."users"."phone_number" IS 'customer phone number';
COMMENT ON COLUMN "public"."users"."created_time" IS 'record creation time';
COMMENT ON COLUMN "public"."users"."updated_time" IS 'record last update time';
COMMENT ON COLUMN "public"."users"."memo" IS 'additional details';

-- 고객 상태 상담 정보
-- 해당 프로필 생성 날짜 / 얼굴형 / 두상 / 퍼스널 컬러 / 모발 / 두피

CREATE TABLE "public"."user_hair_profile" (
    "seq" SERIAL PRIMARY KEY, 
    "user_id" VARCHAR(50) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    -- 이후에 디자이너 입력값으로 변경될 수도 있어서, 우선 varchar로 둠
    "face_shape" VARCHAR,
    "head_shape" VARCHAR,
    "personal_color" VARCHAR,
    "hair_condition" VARCHAR,
    "scalp_condition" VARCHAR,
    "created_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    "updated_time" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
    "memo" VARCHAR
);

COMMENT ON COLUMN "public"."user_hair_profile"."seq" IS 'Auto increment sequence (Primary Key)';
COMMENT ON COLUMN "public"."user_hair_profile"."user_id" IS 'Foreign key referencing users(id)';
COMMENT ON COLUMN "public"."user_hair_profile"."face_shape" IS 'Face shape information (entered by designer)';
COMMENT ON COLUMN "public"."user_hair_profile"."head_shape" IS 'Head shape information (entered by designer)';
COMMENT ON COLUMN "public"."user_hair_profile"."personal_color" IS 'Personal color information (entered by designer)';
COMMENT ON COLUMN "public"."user_hair_profile"."hair_condition" IS 'Hair condition information (entered by designer)';
COMMENT ON COLUMN "public"."user_hair_profile"."scalp_condition" IS 'Scalp condition information (entered by designer)';
COMMENT ON COLUMN "public"."user_hair_profile"."created_time" IS 'Record creation timestamp';
COMMENT ON COLUMN "public"."user_hair_profile"."updated_time" IS 'Record last update timestamp';
COMMENT ON COLUMN "public"."user_hair_profile"."memo" IS 'Additional notes or free text entered by designer';
