import cherrypy
import sqlite3
import threading
import os

# Cherrypy configuration
cherrypy.config.update({
    'server.socket_host': '0.0.0.0',
    'server.socket_port': 8080
})

# Thread-local storage for SQLite objects
local = threading.local()


def get_db_connection():
    if not hasattr(local, 'conn'):
        local.conn = sqlite3.connect('inventory.db')
        # Create the new table if it doesn't exist
        cursor = local.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                location TEXT,
                item TEXT,
                category TEXT,
                quantity_in INTEGER,
                supplier TEXT,
                order_placed BOOLEAN,
                minimum_required INTEGER
            )
        ''')
        local.conn.commit()
    return local.conn



def get_db_cursor():
    if not hasattr(local, 'cursor'):
        local.cursor = get_db_connection().cursor()
    return local.cursor



class Root:
    @cherrypy.expose
    
    @cherrypy.expose
    def index(self):
        # Fetch data from the database
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM stock")
        rows = cursor.fetchall()

        # Generate HTML table rows from the fetched data
        table_rows = ""
        for row in rows:
            table_rows += "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"

        # Serve the home.html file with the table rows
        with open(os.path.join(os.path.dirname(__file__), "home.html"), "r") as file:
            content = file.read()
            return content.format(table_rows=table_rows)



class Admin:
    @cherrypy.expose
    def index(self):
        # Retrieve data from the "stock" table
        cursor = get_db_cursor()
        cursor.execute("SELECT * FROM stock WHERE quantity_in < minimum_required")
        data = cursor.fetchall()

        # Render the admin.html template
        with open("admin.html", "r") as file:
            template = file.read()

        # Escape curly braces by doubling them except for the placeholders
        template = template.replace('{', '{{').replace('}', '}}')
        template = template.replace('{{table_rows}}', '{table_rows}')

        # Generate the HTML table rows from the fetched data
        table_rows = ""
        for row in data:
            # order_placed = "Yes" if row[7] else "No"  # Assuming row[7] is the order_placed BOOLEAN column
            table_rows += (f"<tr>"
                        f"<td>{row[0]}</td>"  # ID
                        f"<td>{row[1]}</td>"  # Last updated
                        f"<td>{row[2]}</td>"  # Location
                        f"<td>{row[3]}</td>"  # Item
                        f"<td>{row[4]}</td>"  # Category
                        f"<td>{row[5]}</td>"  # Qty. (in)
                        f"<td>{row[6]}</td>"  # Supplier
                        f"<td>{row[7]}</td>"  # Order placed
                        f"<td>{row[8]}</td>"  # Min. Reqd.
                        f"</tr>")

        # Use the format method to replace the table_rows placeholder
        return template.format(table_rows=table_rows)


    @cherrypy.expose
    def update_stock(self, id, location, item, category, quantity_in, supplier, order_placed, minimum_required):
    # Update an existing entry in the "inventory" table
        cursor = get_db_cursor()
        cursor.execute(
            '''UPDATE stock 
            SET location=?, 
                item=?, 
                category=?, 
                quantity_in=?, 
                supplier=?, 
                order_placed=?, 
                minimum_required=?,
                timestamp=CURRENT_TIMESTAMP
            WHERE id=?''',
            (location, item, category, quantity_in, supplier, order_placed, minimum_required, id))
        get_db_connection().commit()


        # Redirect back to the admin page
        raise cherrypy.HTTPRedirect('/admin')

    @cherrypy.expose
    def add_stock(self, location, item, category, quantity_in, supplier, add_order_placed, minimum_required):
        # Insert a new entry into the "inventory" table
        order_placed = add_order_placed.upper()
        cursor = get_db_cursor()
        cursor.execute(
            '''INSERT INTO stock (location, item, category, quantity_in, supplier, order_placed, minimum_required) 
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (location, item, category, quantity_in, supplier, order_placed, minimum_required))
        get_db_connection().commit()


        # Redirect back to the admin page
        raise cherrypy.HTTPRedirect('/admin')

    @cherrypy.expose
    def default(self, *args, **kwargs):
        raise cherrypy.HTTPError(404)

    @cherrypy.expose
    def error_page_404(self, *args, **kwargs):
        return "404 Error: Page not found."



class User:
    @cherrypy.expose
    def index(self):
        # Render the user.html template
        with open("user.html", "r") as file:
            template = file.read()

        # Retrieve category options from the "inventory" table
        cursor = get_db_cursor()
        cursor.execute("SELECT DISTINCT location FROM stock")
        categories = cursor.fetchall()

        # Generate the HTML category options
        category_options = ""
        for category in categories:
            category_options += f"<option value='{category[0]}'>{category[0]}</option>"

        return template.replace('{{location_options}}', category_options)



    @cherrypy.expose
    def get_items(self, location):
        cursor = get_db_cursor()
        cursor.execute("SELECT DISTINCT item FROM stock WHERE location=?", (location,))
        items = cursor.fetchall()

        item_options = "\n".join(f"<option value='{item[0]}'>{item[0]}</option>" for item in items)
        return item_options

    @cherrypy.expose
    def update_count(self, item, count_change):
        cursor = get_db_cursor()
        cursor.execute("SELECT quantity_in FROM stock WHERE item=?", (item,))
        current_quantity = cursor.fetchone()[0]
        new_quantity = current_quantity + int(count_change)

        cursor.execute("UPDATE stock SET quantity_in=? WHERE item=?", (new_quantity, item))
        get_db_connection().commit()

        return str(new_quantity)

    @cherrypy.expose
    def update_quantity(self, item, quantity_change):
        # Retrieve the current quantity of the selected item from the "inventory" table
        cursor = get_db_cursor()
        cursor.execute("SELECT quantity_in FROM stock WHERE item=?", (item,))
        current_quantity = cursor.fetchone()[0]

        # Calculate the new quantity based on the quantity change
        new_quantity = current_quantity + int(quantity_change)

        # Update the quantity of the selected item in the "inventory" table
        cursor.execute("UPDATE stock SET quantity_in=? WHERE item=?", (new_quantity, item))
        get_db_connection().commit()

        # Return the updated quantity as the response
        return str(new_quantity)

     



if __name__ == '__main__':
    cherrypy.tree.mount(Root(), '/', config={
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath(os.getcwd())
        }
    })
    cherrypy.tree.mount(Admin(), '/admin', config={
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/'
        }
    })
    cherrypy.tree.mount(User(), '/user', config={
        '/': {
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '/'
        }
    })
    cherrypy.engine.start()
    cherrypy.engine.block()
