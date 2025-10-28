create database budget_tracking_web;
use budget_tracking_web;

create table User(
    user_id int primary key auto_increment,
    user_name varchar(50) not null,
    email varchar(100) not null unique,
    password varchar(255) not null
);

create table transaction(
    transaction_id int primary key auto_increment,
    user_id int ,
    type enum('Income', 'Expense', 'Payable', 'Receivable') not null,
    amount decimal(10, 2) not null,
    category_name varchar(50) not null,
    description text,
    date timestamp not null default current_timestamp,
    person_involved varchar(100),
    status enum('Pending', 'Paid', 'Completed') not null,
    foreign key (user_id)references User(user_id)
);    

CREATE TABLE password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    token VARCHAR(120) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);
