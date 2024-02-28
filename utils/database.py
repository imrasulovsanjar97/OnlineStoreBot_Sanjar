import sqlite3


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    # WORK WITH CATEGORIES
    def get_categories(self):       # get all categories
        categories = self.cursor.execute(
            "SELECT id, category_name FROM categories;"
        )
        return categories.fetchall()

    def add_category(self, new_category):
        try:
            self.cursor.execute(
                "INSERT INTO categories (category_name) VALUES(?);",
                (new_category,)
            )
            self.conn.commit()
            return True
        except:
            return False

    def rename_category(self, old_name, new_name):
        try:
            self.cursor.execute(
                "UPDATE categories SET category_name=? WHERE category_name=?;",
                (new_name, old_name)
            )
            self.conn.commit()
            return True
        except:
            return False

    def delete_category(self, name):
        try:
            self.cursor.execute(
                "DELETE FROM categories WHERE category_name=?;",
                (name,)
            )
            self.conn.commit()
            return True
        except:
            return False

    def check_category_exists(self, name):
        lst = self.cursor.execute(
            f"SELECT * FROM categories WHERE category_name=?",
            (name,)
        ).fetchall()
        if not lst:
            return True
        else:
            return False

    # WORK WITH PRODUCTS
    def add_product(self, title, text, image, price, phone, cat_id, u_id):
        try:
            self.cursor.execute(
                f"INSERT INTO products"
                f"(product_title, product_text, product_image, product_price, product_phone, product_category, product_owner)"
                f"VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, text, image, price, phone, cat_id, u_id)
            )
            self.conn.commit()
            return True
        except:
            return False

    def get_my_last_product(self, u_id):
        product = self.cursor.execute(
            f"SELECT id, product_title, product_text, product_image, product_price, product_phone FROM products WHERE product_owner=? ORDER BY id DESC LIMIT 1",
            (u_id,)
        )
        return product.fetchone()

    def get_all_products(self, cat_id=None):
        if cat_id is None:
            products = self.cursor.execute(
                "SELECT id, product_title, product_text, product_image, product_price, product_phone FROM products;"
            )
        else:
            products = self.cursor.execute(
                "SELECT id, product_title, product_text, product_image, product_price, product_phone FROM products WHERE product_category=?;",
                (cat_id,)
            )
        return products.fetchall()
    
    def get_search_products(self, title):
        products = self.cursor.execute(
            "SELECT id, product_title, product_text, product_image, product_price, product_phone FROM products WHERE product_title=?;",
            (title,)
        )
        return products.fetchall()
    
    def get_title_product(self):       # get title product
        products = self.cursor.execute(
            f"SELECT id, product_title FROM products;"
        )
        return products.fetchall()
    
    def delete_product(self, name):
        try:
            self.cursor.execute(
                "DELETE FROM products WHERE product_title=?;",
                (name,)
            )
            self.conn.commit()
            return True
        except:
            return False

    

