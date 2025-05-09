-- Создание таблицы водителей
CREATE TABLE drivers (
    driver_id SERIAL PRIMARY KEY,
    telegram_id VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    work_calendar JSONB
);

-- Создание таблицы автомобилей
CREATE TABLE cars (
    car_id SERIAL PRIMARY KEY,
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    fuel_card VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    notes TEXT,
    fuel_type VARCHAR(30),
    mileage INTEGER,
    work_calendar JSONB
);

-- Создание таблицы для связи водителей и автомобилей
CREATE TABLE driver_car_assignments (
    assignment_id SERIAL PRIMARY KEY,
    driver_id INTEGER NOT NULL REFERENCES drivers(driver_id),
    car_id INTEGER NOT NULL REFERENCES cars(car_id),
    assignment_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    notes TEXT,
    CONSTRAINT unique_assignment UNIQUE (driver_id, car_id, assignment_date)
);

-- Вставка тестовых данных водителей
INSERT INTO drivers (telegram_id, full_name, work_calendar) VALUES
('@ivanov_ii', 'Иванов Иван Иванович', '{"work_days": ["mon", "tue", "wed", "thu", "fri"], "vacation": false}'),
('@petrov_ap', 'Петров Алексей Петрович', '{"work_days": ["mon", "tue", "thu", "fri", "sat"], "vacation": false}'),
('@sidorova_ek', 'Сидорова Екатерина Константиновна', '{"work_days": ["tue", "wed", "thu", "fri", "sun"], "vacation": true}');

-- Вставка тестовых данных автомобилей
INSERT INTO cars (license_plate, fuel_card, status, notes, fuel_type, mileage, work_calendar) VALUES
('А123БВ777', 'CARD123456', 'available', 'Новый, 2023 г.в.', 'AI-95', 12500, '{"last_service": "2023-05-15", "next_service": 15000}'),
('О765ТК178', 'CARD789012', 'in_use', 'Требуется замена масла', 'Дизель', 87650, '{"last_service": "2023-04-10", "next_service": 90000}'),
('Е555КХ777', 'CARD345678', 'maintenance', 'В ремонте - замена тормозов', 'AI-92', 43200, '{"last_service": "2023-03-20", "next_service": 45000}'),
('Х246СА98', 'CARD901234', 'available', 'Резервный автомобиль', 'AI-95', 3200, '{"last_service": "2023-06-01", "next_service": 5000}');

-- Вставка тестовых данных назначений
INSERT INTO driver_car_assignments (driver_id, car_id, assignment_date, start_time, end_time, notes) VALUES
(1, 1, '2023-06-15', '08:00', '17:00', 'Развозка по точкам'),
(1, 2, '2023-06-16', '09:00', '18:00', 'Междугородняя поездка'),
(2, 4, '2023-06-15', '10:00', '19:00', 'Доставка груза'),
(2, 1, '2023-06-17', '08:30', '16:30', 'Служебная поездка'),
(1, 4, '2023-06-18', '07:00', '15:00', 'Ранний выезд');

-- Создание индексов
CREATE INDEX idx_drivers_telegram ON drivers(telegram_id);
CREATE INDEX idx_cars_license_plate ON cars(license_plate);
CREATE INDEX idx_assignments_date ON driver_car_assignments(assignment_date);
CREATE INDEX idx_assignments_driver ON driver_car_assignments(driver_id);
CREATE INDEX idx_assignments_car ON driver_car_assignments(car_id);

CREATE ROLE pank WITH LOGIN PASSWORD 'securepassword123';
ALTER ROLE pank CREATEDB;
CREATE DATABASE postgres_DB WITH OWNER = pank;