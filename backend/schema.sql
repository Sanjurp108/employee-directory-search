create database if not exists employee_directory character set utf8mb4 collate utf8mb4_unicode_ci; -- utf8mb4_unicode_ci for case-insensitivity

use employee_directory;

create table if not exists employees(
    id int auto_increment primary key,
    name varchar(100) not null,
    email varchar(100) not null unique,
    department varchar(100) not null,
    designation varchar(100) not null,
    date_of_joining date not null,

    index x_emp_name (name),
    index x_emp_department (department), -- for fast searching
    fulltext index ft_emp_name_dept (name,department) -- for matching inside name as well as department
    
) ENGINE=InnoDB;

insert ignore into employees (name, email, department, designation, date_of_joining) values
    ('Rahul Sharma', 'rahul.sharma@company.com', 'Engineering', 'Senior Backend Engineer', '2021-03-15'),
    ('Rahul Verma', 'rahul.verma@company.com', 'Product', 'Product Manager', '2022-07-01'),
    ('Rahim Khan', 'rahim.khan@company.com', 'Engineering', 'Frontend Developer', '2023-01-10'),
    ('Priya Nair', 'priya.nair@company.com', 'Engineering', 'Staff Software Engineer', '2020-06-22'),
    ('Ananya Iyer', 'ananya.iyer@company.com', 'Design', 'Lead Product Designer', '2021-11-08'),
    ('Vikram Patel', 'vikram.patel@company.com', 'Engineering', 'DevOps Engineer', '2022-02-14'),
    ('Sneha Kulkarni', 'sneha.kulkarni@company.com', 'HR', 'HR Business Partner', '2020-09-03'),
    ('Arjun Mehta', 'arjun.mehta@company.com', 'Finance', 'Financial Analyst', '2023-05-19'),
    ('Meera Krishnan', 'meera.krishnan@company.com', 'Sales', 'Account Executive', '2022-08-29'),
    ('Kabir Malhotra', 'kabir.malhotra@company.com', 'Engineering', 'QA Automation Engineer', '2023-03-12'),
    ('Divya Menon', 'divya.menon@company.com', 'Design', 'UX Researcher', '2024-01-15'),
    ('Rohan Joshi', 'rohan.joshi@company.com', 'IT', 'Systems Administrator', '2021-04-20'),
    ('Neha Gupta', 'neha.gupta@company.com', 'Marketing', 'Growth Marketing Lead', '2022-10-11'),
    ('Siddharth Rao', 'siddharth.rao@company.com', 'Engineering', 'Data Engineer', '2021-08-05'),
    ('Kavita Deshmukh', 'kavita.deshmukh@company.com', 'HR', 'Talent Acquisition Lead', '2023-07-24'),
    ('Aditya Bansal', 'aditya.bansal@company.com', 'Product', 'Associate Product Manager', '2024-02-05'),
    ('Pooja Choudhary', 'pooja.choudhary@company.com', 'Finance', 'Senior Accountant', '2020-12-01'),
    ('Nikhil Kapoor', 'nikhil.kapoor@company.com', 'Sales', 'Enterprise Sales Manager', '2021-06-17'),
    ('Ishita Sen', 'ishita.sen@company.com', 'Marketing', 'Content Strategist', '2023-09-18'),
    ('Varun Agarwal', 'varun.agarwal@company.com', 'IT', 'Security Engineer', '2022-04-25');