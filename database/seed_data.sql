INSERT OR IGNORE INTO roles (code, name, description) VALUES
('ADMIN', 'Quản trị viên', 'Toàn quyền hệ thống'),
('MANAGER', 'Quản lý', 'Quản lý vận hành siêu thị'),
('CASHIER', 'Thu ngân', 'Bán hàng tại quầy'),
('WAREHOUSE', 'Nhân viên kho', 'Nhập hàng, kiểm kê và điều chỉnh kho');

INSERT OR IGNORE INTO permissions (code, name, description) VALUES
('USER_MANAGE', 'Quản lý người dùng', 'Tạo, sửa, khóa và phân quyền người dùng'),
('PRODUCT_MANAGE', 'Quản lý sản phẩm', 'Quản lý danh mục, sản phẩm, mã vạch và tồn đầu kỳ'),
('SALE_MANAGE', 'Bán hàng', 'Tạo hóa đơn và thanh toán'),
('WAREHOUSE_MANAGE', 'Quản lý kho', 'Nhập hàng, kiểm kê và điều chỉnh tồn'),
('REPORT_VIEW', 'Xem báo cáo', 'Xem báo cáo doanh thu và tồn kho'),
('AUDIT_VIEW', 'Xem nhật ký', 'Tra cứu nhật ký thao tác');

INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p
WHERE r.code = 'ADMIN';

INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.code IN ('PRODUCT_MANAGE', 'SALE_MANAGE', 'WAREHOUSE_MANAGE', 'REPORT_VIEW', 'AUDIT_VIEW')
WHERE r.code = 'MANAGER';

INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.code IN ('SALE_MANAGE')
WHERE r.code = 'CASHIER';

INSERT OR IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM roles r
JOIN permissions p ON p.code IN ('PRODUCT_MANAGE', 'WAREHOUSE_MANAGE', 'REPORT_VIEW')
WHERE r.code = 'WAREHOUSE';

INSERT OR IGNORE INTO users (
    username, password_hash, full_name, email, phone, role_id, is_active
)
SELECT
    'admin',
    'pbkdf2_sha256$260000$c2lldS10aGktbWluaS1kZW1vLXNhbHQ=$abJeWRz2u8EtEqzukbSs2nm9RipLcBj0iFdKf01+cl8=',
    'System Administrator',
    'admin@sieuthimini.local',
    '',
    roles.id,
    1
FROM roles
WHERE roles.code = 'ADMIN';

INSERT OR IGNORE INTO categories (code, name, description) VALUES
('BEVERAGE', 'Đồ uống', 'Nước uống, sữa, đồ giải khát'),
('FOOD', 'Thực phẩm', 'Thực phẩm khô và hàng tiêu dùng nhanh'),
('HOUSEHOLD', 'Gia dụng', 'Vật dụng gia đình phổ biến');

INSERT OR IGNORE INTO products (sku, barcode, name, category_id, unit, cost_price, sale_price, min_stock)
SELECT 'WATER-001', '8930000000011', 'Nước suối 500ml', c.id, 'chai', 3500, 5000, 20
FROM categories c
WHERE c.code = 'BEVERAGE';

INSERT OR IGNORE INTO products (sku, barcode, name, category_id, unit, cost_price, sale_price, min_stock)
SELECT 'MILK-001', '8930000000028', 'Sữa tươi 1L', c.id, 'hop', 26000, 34000, 10
FROM categories c
WHERE c.code = 'BEVERAGE';

INSERT OR IGNORE INTO products (sku, barcode, name, category_id, unit, cost_price, sale_price, min_stock)
SELECT 'RICE-001', '8930000000035', 'Gạo thơm 5kg', c.id, 'tui', 95000, 125000, 8
FROM categories c
WHERE c.code = 'FOOD';

INSERT OR IGNORE INTO inventory (product_id, quantity)
SELECT id, 100 FROM products WHERE sku = 'WATER-001';

INSERT OR IGNORE INTO inventory (product_id, quantity)
SELECT id, 40 FROM products WHERE sku = 'MILK-001';

INSERT OR IGNORE INTO inventory (product_id, quantity)
SELECT id, 25 FROM products WHERE sku = 'RICE-001';

