USE db_proyect;


CREATE TABLE clinics (
	id_clinic INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    telephone VARCHAR(20) NOT NULL UNIQUE,
    active BOOL NOT NULL DEFAULT 1
);


CREATE TABLE boxes (
	id_box INT AUTO_INCREMENT PRIMARY KEY,
    color ENUM('NEGRA','AZUL','ROJA','VERDE', 'AMARILLA', 'GRIS') NOT NULL,
    number INT NOT NULL,
    status ENUM('LIBRE','OCUPADA','PERDIDA','INACTIVA') NOT NULL DEFAULT 'LIBRE'
);

CREATE TABLE doctors (
	id_doctor VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE,
    telephone VARCHAR(20) UNIQUE,
    address VARCHAR(255),
    status BOOL NOT NULL DEFAULT 1,
    
    id_clinic INT,
    FOREIGN KEY (id_clinic) REFERENCES clinics(id_clinic) ON DELETE SET NULL
);

CREATE TABLE patients (
	id_patient VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50),
    
    id_doctor VARCHAR(20) NOT NULL,
    id_clinic INT,
    
    FOREIGN KEY(id_doctor) REFERENCES doctors(id_doctor) ON DELETE RESTRICT,
    FOREIGN KEY(id_clinic) REFERENCES clinics(id_clinic) ON DELETE SET NULL
    
);

CREATE TABLE products (
	id_product INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL,
    production_time INT NOT NULL,
    status BOOL NOT NULL DEFAULT 1
);

CREATE TABLE jobs (
	id_job INT AUTO_INCREMENT PRIMARY KEY,
    job_type ENUM('NUEVO','REPETICION','GARANTIA') NOT NULL DEFAULT 'NUEVO',
    description TEXT, 
    entry_date DATE NOT NULL DEFAULT (CURRENT_DATE()),
    expected_exit_date DATE NOT NULL,
    exit_date DATE,
    status ENUM('REGISTRADO','EN_PROCESO','EN_REVISION','APROBADO','TERMINADO','FACTURADO','DESPACHADO') NOT NULL DEFAULT 'REGISTRADO',
    
    id_doctor VARCHAR(20) NOT NULL,
    id_patient VARCHAR(20) NOT NULL,
    id_box INT,
    id_clinic INT,
    
    FOREIGN KEY(id_doctor) REFERENCES doctors(id_doctor) ON DELETE RESTRICT,
    FOREIGN KEY(id_patient) REFERENCES patients(id_patient) ON DELETE RESTRICT,
    FOREIGN KEY(id_box) REFERENCES boxes(id_box) ON DELETE RESTRICT,
    FOREIGN KEY(id_clinic) REFERENCES clinics(id_clinic) ON DELETE RESTRICT
    
);

CREATE TABLE job_products (
	id_product INT NOT NULL,
    id_job INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    historic_price DECIMAL(10,2) NOT NULL,
    
    PRIMARY KEY (id_job, id_product),
    
   FOREIGN KEY(id_product) REFERENCES products(id_product) ON DELETE RESTRICT,
   FOREIGN KEY(id_job) REFERENCES jobs(id_job) ON DELETE RESTRICT
);

CREATE TABLE job_pictures (
	id_job_picture INT AUTO_INCREMENT PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL,
    
    id_job INT NOT NULL,
    FOREIGN KEY(id_job) REFERENCES jobs(id_job) ON DELETE CASCADE
);

CREATE TABLE invoices (
    id_invoice INT AUTO_INCREMENT PRIMARY KEY,
    id_job INT NOT NULL UNIQUE,
    invoice_date DATE NOT NULL DEFAULT (CURRENT_DATE()),
    amount DECIMAL(10,2) NOT NULL,
    lending_balance DECIMAL(10,2) NOT NULL,
    pay_state ENUM('PAGADO','PARCIAL','PENDIENTE') NOT NULL DEFAULT 'PENDIENTE',

    FOREIGN KEY (id_job) REFERENCES jobs(id_job) ON DELETE RESTRICT
);

CREATE TABLE payments (
    id_payment INT AUTO_INCREMENT PRIMARY KEY,
    id_invoice INT NOT NULL,
    pay_date DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP()),
    payment_amount DECIMAL(10,2) NOT NULL,
    payment_type ENUM('EFECTIVO','TRANSFERENCIA','CHEQUE','OTRO') NOT NULL DEFAULT 'EFECTIVO',
    status BOOL NOT NULL DEFAULT 1,

    FOREIGN KEY (id_invoice) REFERENCES invoices(id_invoice) ON DELETE RESTRICT
);
