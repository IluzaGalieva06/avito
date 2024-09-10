--
-- PostgreSQL database dump
--

-- Dumped from database version 14.13 (Ubuntu 14.13-0ubuntu0.22.04.1)
-- Dumped by pg_dump version 14.13 (Ubuntu 14.13-0ubuntu0.22.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: organization_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.organization_type AS ENUM (
    'IE',
    'LLC',
    'JSC'
);


ALTER TYPE public.organization_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: bid; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bid (
    name character varying(100) NOT NULL,
    description text,
    status character varying(50),
    version integer,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    tender_id uuid,
    organization_id uuid,
    author_id uuid
);


ALTER TABLE public.bid OWNER TO postgres;

--
-- Name: employee; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee (
    username character varying(50) NOT NULL,
    first_name character varying(50),
    last_name character varying(50),
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL
);


ALTER TABLE public.employee OWNER TO postgres;

--
-- Name: organization; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organization (
    name character varying(100) NOT NULL,
    description text,
    type public.organization_type,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL
);


ALTER TABLE public.organization OWNER TO postgres;

--
-- Name: organization_responsibility; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organization_responsibility (
    user_id uuid NOT NULL,
    organization_id uuid
);


ALTER TABLE public.organization_responsibility OWNER TO postgres;

--
-- Name: tender; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tender (
    name character varying(100) NOT NULL,
    description text,
    status character varying(50),
    version integer,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone,
    "serviceType" character varying(50) DEFAULT 'Construction'::character varying NOT NULL,
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    "organizationId" uuid,
    creator_id uuid
);


ALTER TABLE public.tender OWNER TO postgres;

--
-- Name: employee employee_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (id);


--
-- Name: employee employee_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_username_key UNIQUE (username);


--
-- Name: organization_responsibility organization_responsibility_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organization_responsibility
    ADD CONSTRAINT organization_responsibility_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.employee(id);


--
-- PostgreSQL database dump complete
--

