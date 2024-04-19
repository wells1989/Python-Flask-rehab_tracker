--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2
-- Dumped by pg_dump version 16.2

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: exercises; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.exercises (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    image character varying(255),
    creator_id integer
);


ALTER TABLE public.exercises OWNER TO postgres;

--
-- Name: exercises_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.exercises_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.exercises_id_seq OWNER TO postgres;

--
-- Name: exercises_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.exercises_id_seq OWNED BY public.exercises.id;


--
-- Name: programs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.programs (
    id integer NOT NULL,
    user_id integer,
    start_date date,
    end_date date,
    rating integer,
    description character varying(255),
    CONSTRAINT programs_rating_check CHECK (((rating >= 1) AND (rating <= 3)))
);


ALTER TABLE public.programs OWNER TO postgres;

--
-- Name: programs_exercises; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.programs_exercises (
    program_id integer NOT NULL,
    exercise_id integer NOT NULL,
    user_id integer,
    exercise_name character varying(255),
    notes text,
    sets integer,
    reps integer,
    rating integer,
    CONSTRAINT programs_exercises_rating_check CHECK (((rating >= 1) AND (rating <= 3)))
);


ALTER TABLE public.programs_exercises OWNER TO postgres;

--
-- Name: programs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.programs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.programs_id_seq OWNER TO postgres;

--
-- Name: programs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.programs_id_seq OWNED BY public.programs.id;


--
-- Name: userprofiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.userprofiles (
    id integer NOT NULL,
    user_id integer,
    profile_pic character varying(255),
    bio text
);


ALTER TABLE public.userprofiles OWNER TO postgres;

--
-- Name: userprofile_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.userprofile_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.userprofile_id_seq OWNER TO postgres;

--
-- Name: userprofile_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.userprofile_id_seq OWNED BY public.userprofiles.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    name text NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    is_admin boolean DEFAULT false NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: exercises id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercises ALTER COLUMN id SET DEFAULT nextval('public.exercises_id_seq'::regclass);


--
-- Name: programs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs ALTER COLUMN id SET DEFAULT nextval('public.programs_id_seq'::regclass);


--
-- Name: userprofiles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userprofiles ALTER COLUMN id SET DEFAULT nextval('public.userprofile_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: exercises; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.exercises (id, name, image, creator_id) FROM stdin;
2	deadlifts	sample image	28
8	firemans carries	sample image2	28
10	muay thai		19
5	bench	sample image3	28
4	walking lunges	me walking	28
6	bridges	me walking	28
12	dumbbell laterals	\N	28
14	dumbbell front laterals	test_image	28
16	dumbbell side laterals	test_image	30
18	dumbbell rear and front laterals	test_image	30
\.


--
-- Data for Name: programs; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.programs (id, user_id, start_date, end_date, rating, description) FROM stdin;
2	28	2000-10-20	2000-12-20	3	first program
7	28	2000-10-10	2005-10-12	2	an old program I did
\.


--
-- Data for Name: programs_exercises; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.programs_exercises (program_id, exercise_id, user_id, exercise_name, notes, sets, reps, rating) FROM stdin;
2	4	28	lunges	test stage	3	15	2
2	5	28	dips	leg work	2	20	2
7	4	28	walking lunges	did not go well	3	20	2
7	10	28	muay thai		3	20	2
7	16	28	dumbbell side laterals		5	15	2
\.


--
-- Data for Name: userprofiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.userprofiles (id, user_id, profile_pic, bio) FROM stdin;
8	28		
5	19	text	I am from Manchester init!!!
3	17	text	I am from Rotterdam
12	35		
9	30	my_new_pic_link_hi	I am from Roma, Italy
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, name, email, password, is_admin) FROM stdin;
1	Paul	paul@gmail.com\r\n	paul2	f
28	superuser	wellspaul554@gmail.com	\\x243262243132242e514f49796367417a2e682f48315174777a6b7848656e7a754e33784b744f2e4332706a486b4f616e485458443274686a58625747	t
17	D-man	dennis@gmail.com	\\x243262243132247a6b6779694c417332724c4339463366544d74334b756a57352e43633368397072454857634f59666f3256494976696c594366484b	f
35	adam	adam@gmail.com	\\x2432622431322458646f576b504d56565638754b30633867764d6e2e2e374a564b6b35474d4d31336d49325951436a424a53797a6864374950384c47	f
30	Vasiley-man	vasile@gmail.com	\\x243262243132246168795876396a794f2e7563684e3156433648506b653475437154747775716c702f455836314e725a467744637632794356716579	f
19	frank	frankie@gmail.com	\\x2432622431322445777a7152662f6752715546714171756e764877497532754c304a585776497752785369694b444d46315151394c385167686d6a61	f
\.


--
-- Name: exercises_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.exercises_id_seq', 18, true);


--
-- Name: programs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.programs_id_seq', 8, true);


--
-- Name: userprofile_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.userprofile_id_seq', 13, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 36, true);


--
-- Name: exercises exercises_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercises
    ADD CONSTRAINT exercises_name_key UNIQUE (name);


--
-- Name: exercises exercises_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercises
    ADD CONSTRAINT exercises_pkey PRIMARY KEY (id);


--
-- Name: programs_exercises programs_exercises_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs_exercises
    ADD CONSTRAINT programs_exercises_pkey PRIMARY KEY (exercise_id, program_id);


--
-- Name: programs programs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_pkey PRIMARY KEY (id);


--
-- Name: userprofiles userprofile_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userprofiles
    ADD CONSTRAINT userprofile_pkey PRIMARY KEY (id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: exercises exercises_creator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.exercises
    ADD CONSTRAINT exercises_creator_id_fkey FOREIGN KEY (creator_id) REFERENCES public.users(id);


--
-- Name: programs_exercises programs_exercises_exercise_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs_exercises
    ADD CONSTRAINT programs_exercises_exercise_id_fkey FOREIGN KEY (exercise_id) REFERENCES public.exercises(id);


--
-- Name: programs_exercises programs_exercises_program_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs_exercises
    ADD CONSTRAINT programs_exercises_program_id_fkey FOREIGN KEY (program_id) REFERENCES public.programs(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: programs_exercises programs_exercises_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs_exercises
    ADD CONSTRAINT programs_exercises_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: programs programs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.programs
    ADD CONSTRAINT programs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: userprofiles userprofile_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userprofiles
    ADD CONSTRAINT userprofile_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

