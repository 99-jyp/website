BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "auth_group" (
	"id"	integer NOT NULL,
	"name"	varchar(150) NOT NULL UNIQUE,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "auth_group_permissions" (
	"id"	integer NOT NULL,
	"group_id"	integer NOT NULL,
	"permission_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("permission_id") REFERENCES "auth_permission"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_permission" (
	"id"	integer NOT NULL,
	"content_type_id"	integer NOT NULL,
	"codename"	varchar(100) NOT NULL,
	"name"	varchar(255) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("content_type_id") REFERENCES "django_content_type"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_user" (
	"id"	integer NOT NULL,
	"password"	varchar(128) NOT NULL,
	"last_login"	datetime,
	"is_superuser"	bool NOT NULL,
	"username"	varchar(150) NOT NULL UNIQUE,
	"last_name"	varchar(150) NOT NULL,
	"email"	varchar(254) NOT NULL,
	"is_staff"	bool NOT NULL,
	"is_active"	bool NOT NULL,
	"date_joined"	datetime NOT NULL,
	"first_name"	varchar(150) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "auth_user_groups" (
	"id"	integer NOT NULL,
	"user_id"	integer NOT NULL,
	"group_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("group_id") REFERENCES "auth_group"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "auth_user_user_permissions" (
	"id"	integer NOT NULL,
	"user_id"	integer NOT NULL,
	"permission_id"	integer NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("permission_id") REFERENCES "auth_permission"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "core_notification" (
	"id"	integer NOT NULL,
	"message"	text NOT NULL,
	"level"	varchar(20) NOT NULL,
	"created_at"	datetime NOT NULL,
	"is_read"	bool NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "django_admin_log" (
	"id"	integer NOT NULL,
	"object_id"	text,
	"object_repr"	varchar(200) NOT NULL,
	"action_flag"	smallint unsigned NOT NULL CHECK("action_flag" >= 0),
	"change_message"	text NOT NULL,
	"content_type_id"	integer,
	"user_id"	integer NOT NULL,
	"action_time"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("content_type_id") REFERENCES "django_content_type"("id") DEFERRABLE INITIALLY DEFERRED,
	FOREIGN KEY("user_id") REFERENCES "auth_user"("id") DEFERRABLE INITIALLY DEFERRED
);
CREATE TABLE IF NOT EXISTS "django_content_type" (
	"id"	integer NOT NULL,
	"app_label"	varchar(100) NOT NULL,
	"model"	varchar(100) NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "django_migrations" (
	"id"	integer NOT NULL,
	"app"	varchar(255) NOT NULL,
	"name"	varchar(255) NOT NULL,
	"applied"	datetime NOT NULL,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "django_session" (
	"session_key"	varchar(40) NOT NULL,
	"session_data"	text NOT NULL,
	"expire_date"	datetime NOT NULL,
	PRIMARY KEY("session_key")
);
CREATE TABLE IF NOT EXISTS "employee" (
	"id"	INTEGER,
	"employee_no"	TEXT UNIQUE,
	"name"	TEXT NOT NULL,
	"department"	TEXT,
	"leave_days"	INTEGER DEFAULT 15,
	PRIMARY KEY("id" AUTOINCREMENT)
);
INSERT INTO "auth_permission" VALUES (1,1,'add_logentry','Can add log entry');
INSERT INTO "auth_permission" VALUES (2,1,'change_logentry','Can change log entry');
INSERT INTO "auth_permission" VALUES (3,1,'delete_logentry','Can delete log entry');
INSERT INTO "auth_permission" VALUES (4,1,'view_logentry','Can view log entry');
INSERT INTO "auth_permission" VALUES (5,2,'add_permission','Can add permission');
INSERT INTO "auth_permission" VALUES (6,2,'change_permission','Can change permission');
INSERT INTO "auth_permission" VALUES (7,2,'delete_permission','Can delete permission');
INSERT INTO "auth_permission" VALUES (8,2,'view_permission','Can view permission');
INSERT INTO "auth_permission" VALUES (9,3,'add_group','Can add group');
INSERT INTO "auth_permission" VALUES (10,3,'change_group','Can change group');
INSERT INTO "auth_permission" VALUES (11,3,'delete_group','Can delete group');
INSERT INTO "auth_permission" VALUES (12,3,'view_group','Can view group');
INSERT INTO "auth_permission" VALUES (13,4,'add_user','Can add user');
INSERT INTO "auth_permission" VALUES (14,4,'change_user','Can change user');
INSERT INTO "auth_permission" VALUES (15,4,'delete_user','Can delete user');
INSERT INTO "auth_permission" VALUES (16,4,'view_user','Can view user');
INSERT INTO "auth_permission" VALUES (17,5,'add_contenttype','Can add content type');
INSERT INTO "auth_permission" VALUES (18,5,'change_contenttype','Can change content type');
INSERT INTO "auth_permission" VALUES (19,5,'delete_contenttype','Can delete content type');
INSERT INTO "auth_permission" VALUES (20,5,'view_contenttype','Can view content type');
INSERT INTO "auth_permission" VALUES (21,6,'add_session','Can add session');
INSERT INTO "auth_permission" VALUES (22,6,'change_session','Can change session');
INSERT INTO "auth_permission" VALUES (23,6,'delete_session','Can delete session');
INSERT INTO "auth_permission" VALUES (24,6,'view_session','Can view session');
INSERT INTO "auth_permission" VALUES (25,7,'add_notification','Can add 알림');
INSERT INTO "auth_permission" VALUES (26,7,'change_notification','Can change 알림');
INSERT INTO "auth_permission" VALUES (27,7,'delete_notification','Can delete 알림');
INSERT INTO "auth_permission" VALUES (28,7,'view_notification','Can view 알림');
INSERT INTO "auth_user" VALUES (1,'pbkdf2_sha256$600000$ke5dPbN8PakZ4PIlMdT1uw$mDr/oOMhKNGew3RAPUdv7/9VjjXx944CdlQBYMvj7CU=','2026-07-10 10:10:21.239438',1,'admin','','admin@hospital.ai',1,1,'2026-07-10 09:55:28.848382','');
INSERT INTO "core_notification" VALUES (1,'📊 휴가 현황 리포트 생성 완료 – 3명','success','2026-07-10 10:13:31.189166',0);
INSERT INTO "django_content_type" VALUES (1,'admin','logentry');
INSERT INTO "django_content_type" VALUES (2,'auth','permission');
INSERT INTO "django_content_type" VALUES (3,'auth','group');
INSERT INTO "django_content_type" VALUES (4,'auth','user');
INSERT INTO "django_content_type" VALUES (5,'contenttypes','contenttype');
INSERT INTO "django_content_type" VALUES (6,'sessions','session');
INSERT INTO "django_content_type" VALUES (7,'core','notification');
INSERT INTO "django_content_type" VALUES (8,'core','employee');
INSERT INTO "django_migrations" VALUES (1,'contenttypes','0001_initial','2026-07-10 09:55:22.173411');
INSERT INTO "django_migrations" VALUES (2,'auth','0001_initial','2026-07-10 09:55:22.188357');
INSERT INTO "django_migrations" VALUES (3,'admin','0001_initial','2026-07-10 09:55:22.198327');
INSERT INTO "django_migrations" VALUES (4,'admin','0002_logentry_remove_auto_add','2026-07-10 09:55:22.207297');
INSERT INTO "django_migrations" VALUES (5,'admin','0003_logentry_add_action_flag_choices','2026-07-10 09:55:22.214274');
INSERT INTO "django_migrations" VALUES (6,'contenttypes','0002_remove_content_type_name','2026-07-10 09:55:22.225237');
INSERT INTO "django_migrations" VALUES (7,'auth','0002_alter_permission_name_max_length','2026-07-10 09:55:22.233207');
INSERT INTO "django_migrations" VALUES (8,'auth','0003_alter_user_email_max_length','2026-07-10 09:55:22.251150');
INSERT INTO "django_migrations" VALUES (9,'auth','0004_alter_user_username_opts','2026-07-10 09:55:22.257131');
INSERT INTO "django_migrations" VALUES (10,'auth','0005_alter_user_last_login_null','2026-07-10 09:55:22.265104');
INSERT INTO "django_migrations" VALUES (11,'auth','0006_require_contenttypes_0002','2026-07-10 09:55:22.268094');
INSERT INTO "django_migrations" VALUES (12,'auth','0007_alter_validators_add_error_messages','2026-07-10 09:55:22.275067');
INSERT INTO "django_migrations" VALUES (13,'auth','0008_alter_user_username_max_length','2026-07-10 09:55:22.283040');
INSERT INTO "django_migrations" VALUES (14,'auth','0009_alter_user_last_name_max_length','2026-07-10 09:55:22.291013');
INSERT INTO "django_migrations" VALUES (15,'auth','0010_alter_group_name_max_length','2026-07-10 09:55:22.298987');
INSERT INTO "django_migrations" VALUES (16,'auth','0011_update_proxy_permissions','2026-07-10 09:55:22.307956');
INSERT INTO "django_migrations" VALUES (17,'auth','0012_alter_user_first_name_max_length','2026-07-10 09:55:22.319917');
INSERT INTO "django_migrations" VALUES (18,'core','0001_initial','2026-07-10 09:55:22.324900');
INSERT INTO "django_migrations" VALUES (19,'sessions','0001_initial','2026-07-10 09:55:22.334867');
INSERT INTO "django_session" VALUES ('evq6aiib24hqud6flk31aqe0sfkps4yu','.eJxVjEEOwiAQRe_C2hBmoNRx6b5nIDCAVA0kpV0Z765NutDtf-_9l3B-W4vbelrcHMVFgDj9bsHzI9UdxLuvtya51XWZg9wVedAupxbT83q4fwfF9_KtjcEcFekzKRqyAmI0gFajDkA2ZMVjIEBIxnImjYk4eTCBI5IaRhbvD7DBNw4:1whzYF:OAfdSmNypqveWPa6q54t-W2VfqL5BpelLt2vp1gnm3c','2026-07-11 09:57:11.624183');
INSERT INTO "django_session" VALUES ('p00o7rrir79bwwne99ry3v9nuur7nzl7','.eJxVjEEOwiAQRe_C2hBmoNRx6b5nIDCAVA0kpV0Z765NutDtf-_9l3B-W4vbelrcHMVFgDj9bsHzI9UdxLuvtya51XWZg9wVedAupxbT83q4fwfF9_KtjcEcFekzKRqyAmI0gFajDkA2ZMVjIEBIxnImjYk4eTCBI5IaRhbvD7DBNw4:1whziQ:SlgW_ROxtVjT9Ljxmvv_PTrU_Z7TrqF4LV7HLOEIJpw','2026-07-11 10:07:42.303913');
INSERT INTO "django_session" VALUES ('avij57cw3d5rcdrx82f4y9pu0urr1e90','.eJxVjEEOwiAQRe_C2hBmoNRx6b5nIDCAVA0kpV0Z765NutDtf-_9l3B-W4vbelrcHMVFgDj9bsHzI9UdxLuvtya51XWZg9wVedAupxbT83q4fwfF9_KtjcEcFekzKRqyAmI0gFajDkA2ZMVjIEBIxnImjYk4eTCBI5IaRhbvD7DBNw4:1whzkz:O2Ew5-vmE1pbHuzS1DIiyWOZLk5fyXaQ_N8vzZVzvrI','2026-07-11 10:10:21.244421');
INSERT INTO "employee" VALUES (1,'2026001','홍길동','행정팀',15);
INSERT INTO "employee" VALUES (2,'2026002','김철수','원무과',12);
INSERT INTO "employee" VALUES (3,'2026003','이영희','간호부',18);
CREATE INDEX IF NOT EXISTS "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" (
	"group_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" (
	"group_id",
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" (
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_permission_content_type_id_2f476e4b" ON "auth_permission" (
	"content_type_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" (
	"content_type_id",
	"codename"
);
CREATE INDEX IF NOT EXISTS "auth_user_groups_group_id_97559544" ON "auth_user_groups" (
	"group_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" (
	"user_id",
	"group_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" (
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" (
	"user_id",
	"permission_id"
);
CREATE INDEX IF NOT EXISTS "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" (
	"content_type_id"
);
CREATE INDEX IF NOT EXISTS "django_admin_log_user_id_c564eba6" ON "django_admin_log" (
	"user_id"
);
CREATE UNIQUE INDEX IF NOT EXISTS "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" (
	"app_label",
	"model"
);
CREATE INDEX IF NOT EXISTS "django_session_expire_date_a5c62663" ON "django_session" (
	"expire_date"
);
COMMIT;
