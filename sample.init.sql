create table "__EFMigrationsHistory"
(
    "MigrationId"    varchar(150) not null
        constraint "PK___EFMigrationsHistory"
            primary key,
    "ProductVersion" varchar(32)  not null
);

create table "Case"
(
    "Id"          bigint generated by default as identity
        constraint "PK_Case"
            primary key,
    "DisplayId"   varchar(10)              not null,
    "Name"        varchar(90)              not null,
    "DisplayName" varchar(100)             not null,
    "Status"      varchar(50)              not null,
    "Accessed"    timestamp with time zone not null,
    "Created"     timestamp with time zone not null,
    "Modified"    timestamp with time zone not null
);

create table "User"
(
    "EmailAddress" varchar(320)             not null
        constraint "PK_User"
            primary key,
    "JobTitle"     varchar(100)             not null,
    "DisplayName"  varchar(200)             not null,
    "GivenName"    varchar(100)             not null,
    "LastName"     varchar(100)             not null,
    "Created"      timestamp with time zone not null,
    "Modified"     timestamp with time zone not null
);

create table "Exhibit"
(
    "Id"                     bigint generated by default as identity
        constraint "PK_Exhibit"
            primary key,
    "Reference"              varchar(10)              not null,
    "Description"            varchar(200)             not null,
    "DateTimeSeizedProduced" timestamp with time zone not null,
    "WhereSeizedProduced"    varchar(200)             not null,
    "SeizedBy"               varchar(200)             not null,
    "CaseId"                 bigint
        constraint "FK_Exhibit_Case_CaseId"
            references "Case",
    "Created"                timestamp with time zone not null,
    "Modified"               timestamp with time zone not null
);

create index "IX_Exhibit_CaseId"
    on "Exhibit" ("CaseId");

create table "SharedHash"
(
    "Id"         bigint generated by default as identity
        constraint "PK_SharedHash"
            primary key,
    "ObjectName" varchar(1024) not null,
    "VersionId"  varchar(255)  not null,
    "Md5Hash"    varchar(32)   not null,
    "ShaHash"    varchar(64)   not null,
    "CaseId"     bigint
        constraint "FK_SharedHash_Case_CaseId"
            references "Case"
);

create index "IX_SharedHash_CaseId"
    on "SharedHash" ("CaseId");

create table "CaseUser"
(
    "Id"                 bigint generated by default as identity
        constraint "PK_CaseUser"
            primary key,
    "UserEmailAddress"   varchar(320)             not null
        constraint "FK_CaseUser_User_UserEmailAddress"
            references "User"
            on delete cascade,
    "IsLeadInvestigator" boolean                  not null,
    "CaseId"             bigint                   not null
        constraint "FK_CaseUser_Case_CaseId"
            references "Case"
            on delete cascade,
    "Created"            timestamp with time zone not null,
    "Modified"           timestamp with time zone not null
);

create index "IX_CaseUser_CaseId"
    on "CaseUser" ("CaseId");

create index "IX_CaseUser_UserEmailAddress"
    on "CaseUser" ("UserEmailAddress");

create table "Event"
(
    "Id"           bigint generated by default as identity
        constraint "PK_Event"
            primary key,
    "Created"      timestamp with time zone default now() not null,
    "Updated"      timestamp with time zone default now() not null,
    "Data"         jsonb                                  not null,
    "EventType"    varchar(50)                            not null,
    "EmailAddress" varchar(320)
        constraint "FK_Event_User_EmailAddress"
            references "User"
);

create index "IX_Event_EmailAddress"
    on "Event" ("EmailAddress");

create table "SharedContemporaneousNote"
(
    "Id"                  bigint generated by default as identity
        constraint "PK_SharedContemporaneousNote"
            primary key,
    "CreatorEmailAddress" varchar(320)
        constraint "FK_SharedContemporaneousNote_User_CreatorEmailAddress"
            references "User",
    "CaseId"              bigint
        constraint "FK_SharedContemporaneousNote_Case_CaseId"
            references "Case",
    "Created"             timestamp with time zone not null,
    "Modified"            timestamp with time zone not null
);

create index "IX_SharedContemporaneousNote_CaseId"
    on "SharedContemporaneousNote" ("CaseId");

create index "IX_SharedContemporaneousNote_CreatorEmailAddress"
    on "SharedContemporaneousNote" ("CreatorEmailAddress");

create table "SharedTab"
(
    "Id"                  bigint generated by default as identity
        constraint "PK_SharedTab"
            primary key,
    "Name"                varchar(50)              not null,
    "CreatorEmailAddress" varchar(320)             not null
        constraint "FK_SharedTab_User_CreatorEmailAddress"
            references "User"
            on delete cascade,
    "CaseId"              bigint                   not null
        constraint "FK_SharedTab_Case_CaseId"
            references "Case"
            on delete cascade,
    "Created"             timestamp with time zone not null,
    "Modified"            timestamp with time zone not null
);

create index "IX_SharedTab_CaseId"
    on "SharedTab" ("CaseId");

create index "IX_SharedTab_CreatorEmailAddress"
    on "SharedTab" ("CreatorEmailAddress");

create table "UserSettings"
(
    "Id"           bigint generated by default as identity
        constraint "PK_UserSettings"
            primary key,
    "EmailAddress" varchar(320)
        constraint "FK_UserSettings_User_EmailAddress"
            references "User",
    "TimeZone"     varchar(100)             not null,
    "DateFormat"   varchar(50)              not null,
    "TimeFormat"   varchar(50)              not null,
    "Locale"       varchar(5)               not null,
    "Created"      timestamp with time zone not null,
    "Modified"     timestamp with time zone not null
);

create unique index "IX_UserSettings_EmailAddress"
    on "UserSettings" ("EmailAddress");

create table "ContemporaneousNote"
(
    "Id"         bigint generated by default as identity
        constraint "PK_ContemporaneousNote"
            primary key,
    "CaseUserId" bigint
        constraint "FK_ContemporaneousNote_CaseUser_CaseUserId"
            references "CaseUser",
    "Created"    timestamp with time zone not null,
    "Modified"   timestamp with time zone not null
);

create index "IX_ContemporaneousNote_CaseUserId"
    on "ContemporaneousNote" ("CaseUserId");

create table "Hash"
(
    "Id"         bigint generated by default as identity
        constraint "PK_Hash"
            primary key,
    "ObjectName" varchar(1024)            not null,
    "VersionId"  varchar(255)             not null,
    "Md5Hash"    varchar(32)              not null,
    "ShaHash"    varchar(64)              not null,
    "CaseUserId" bigint
        constraint "FK_Hash_CaseUser_CaseUserId"
            references "CaseUser",
    "Created"    timestamp with time zone not null,
    "Modified"   timestamp with time zone not null
);

create index "IX_Hash_CaseUserId"
    on "Hash" ("CaseUserId");

create table "Tab"
(
    "Id"         bigint generated by default as identity
        constraint "PK_Tab"
            primary key,
    "Name"       varchar(50)              not null,
    "CaseUserId" bigint
        constraint "FK_Tab_CaseUser_CaseUserId"
            references "CaseUser",
    "Created"    timestamp with time zone not null,
    "Modified"   timestamp with time zone not null
);

create index "IX_Tab_CaseUserId"
    on "Tab" ("CaseUserId");

