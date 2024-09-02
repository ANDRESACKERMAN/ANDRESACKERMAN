from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import json
import pandas as pd

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Rutas de los archivos JSON
PRODUCTS_FILE = 'productos.json'
ORDERS_FILE = 'pedidos.json'

# Contraseñas
ADMIN_PASSWORD = '8645'
USER_PASSWORD = 'MILOR2024'

# Funciones de utilidad para cargar y guardar JSON
def load_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Ruta para la página de inicio
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user_type = request.form['user_type']
        password = request.form['password']
        
        if user_type == 'admin' and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['user_type'] = 'admin'
            return redirect(url_for('admin'))
        elif user_type == 'user' and password == USER_PASSWORD:
            session['logged_in'] = True
            session['user_type'] = 'user'
            return redirect(url_for('user'))
        else:
            flash('Usuario o contraseña incorrecta.', 'danger')
            
    return render_template('home.html')

# Ruta para el panel de administrador
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'logged_in' not in session or session.get('user_type') != 'admin':
        return redirect(url_for('home'))

    if request.method == 'POST':
        if 'add_product' in request.form:
            product_name = request.form['product_name']
            if product_name:
                products = load_json(PRODUCTS_FILE)
                product_id = len(products) + 1
                products.append({'id': product_id, 'nombre': product_name})
                save_json(products, PRODUCTS_FILE)
                flash('Producto añadido con éxito.', 'success')
            else:
                flash('El nombre del producto no puede estar vacío.', 'danger')
        elif 'clear_products' in request.form:
            save_json([], PRODUCTS_FILE)
            flash('Lista de productos limpiada.', 'success')
        elif 'clear_orders' in request.form:
            save_json([], ORDERS_FILE)
            flash('Lista de pedidos limpiada.', 'success')
        elif 'download_orders' in request.form:
            orders = load_json(ORDERS_FILE)
            if orders:
                df = pd.DataFrame(orders)
                df.to_excel('pedidos.xlsx', index=False)
                return send_file('pedidos.xlsx', as_attachment=True)
            else:
                flash('No hay pedidos para descargar.', 'danger')
        elif 'switch_user' in request.form:
            session.pop('logged_in', None)
            session.pop('user_type', None)
            return redirect(url_for('home'))
    
    products = load_json(PRODUCTS_FILE)
    return render_template('admin.html', products=products)

# Ruta para el panel de usuario
@app.route('/user', methods=['GET', 'POST'])
def user():
    if 'logged_in' not in session or session.get('user_type') != 'user':
        return redirect(url_for('home'))
        
    if request.method == 'POST':
        if 'add_order' in request.form:
            product_number = request.form['product_number']
            quantity = request.form['quantity']
            delivery_date = request.form['delivery_date']
            store_name = request.form['store_name']
            if product_number.isdigit() and quantity.isdigit() and delivery_date and store_name:
                products = load_json(PRODUCTS_FILE)
                if 0 < int(product_number) <= len(products):
                    selected_product = products[int(product_number) - 1]['nombre']
                    orders = load_json(ORDERS_FILE)
                    orders.append({
                        'producto': selected_product,
                        'cantidad': quantity,
                        'fecha_entrega': delivery_date,
                        'nombre_local': store_name
                    })
                    save_json(orders, ORDERS_FILE)
                    flash(f'{quantity} unidades de {selected_product} añadido al pedido para {delivery_date}.', 'success')
                else:
                    flash('Número de producto inválido.', 'danger')
            else:
                flash('Por favor, complete todos los campos correctamente.', 'danger')
        elif 'switch_user' in request.form:
            session.pop('logged_in', None)
            session.pop('user_type', None)
            return redirect(url_for('home'))
    
    products = load_json(PRODUCTS_FILE)
    orders = load_json(ORDERS_FILE)
    return render_template('user.html', products=products, orders=orders)

if __name__ == '__main__':
    app.run(debug=True)
