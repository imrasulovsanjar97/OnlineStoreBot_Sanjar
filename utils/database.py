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
    def get_products(self):       # get all categories
        products = self.cursor.execute(
            "SELECT id, product_name FROM products;"
        )
        return products.fetchall()
    
    def add_product(self, new_product):
        try:
            self.cursor.execute(
                "INSERT INTO products (product_name) VALUES(?);",
                (new_product,)
            )
            self.conn.commit()
            return True
        except:
            return False
        
    def rename_product(self, old_name, new_name):
        try:
            self.cursor.execute(
                "UPDATE products SET product_name=? WHERE product_name=?;",
                (new_name, old_name)
            )
            self.conn.commit()
            return True
        except:
            return False
        
    def delete_product(self, name):
        try:
            self.cursor.execute(
                "DELETE FROM products WHERE product_name=?;",
                (name,)
            )
            self.conn.commit()
            return True
        except:
            return False

    
    def check_product_exists(self, name):
        lst = self.cursor.execute(
            f"SELECT * FROM products WHERE product_name=?",
            (name,)
        ).fetchall()
        if not lst:
            return True
        else:
            return False