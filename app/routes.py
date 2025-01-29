from flask import render_template, request, redirect, url_for, flash, session
from sqlalchemy import func
from functools import wraps
from datetime import date, datetime
from . import db
from .models import Medicine, Supplier, Employee, Customer, Purchase, Return, Sale, User, Financial, Inventory
from .forms import MedicineForm, EmployeeForm, CustomerForm, SupplierForm, PurchaseForm, ReturnForm, SaleForm, UserForm, LoginForm

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请登录以访问此页面。')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def update_financials(date):
    total_sales = db.session.query(func.sum(Sale.total_price)).filter(func.date(Sale.sale_date) == date).scalar() or 0
    total_returns = db.session.query(func.sum(Return.quantity * (Sale.total_price / Sale.quantity))) \
        .select_from(Return).join(Sale).filter(func.date(Return.return_date) == date).scalar() or 0
    net_profit = total_sales - total_returns

    financial_record = db.session.query(Financial).filter_by(date=date).first()
    if financial_record:
        financial_record.total_sales = total_sales
        financial_record.net_profit = net_profit
    else:
        new_financial_record = Financial(
            date=date,
            total_sales=total_sales,
            net_profit=net_profit
        )
        db.session.add(new_financial_record)

    db.session.commit()

def update_inventory(medicine_id, quantity_change):
    inventory_record = db.session.query(Inventory).filter_by(medicine_id=medicine_id).first()
    if inventory_record:
        inventory_record.quantity += quantity_change
        inventory_record.last_updated = date.today()
    else:
        new_inventory_record = Inventory(
            medicine_id=medicine_id,
            quantity=quantity_change,
            last_updated=date.today()
        )
        db.session.add(new_inventory_record)

    db.session.commit()

def register_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/medicines')
    @login_required
    def list_medicines():
        medicines = Medicine.query.all()
        return render_template('medicines.html', medicines=medicines)

    @app.route('/add_medicine', methods=['GET', 'POST'])
    @login_required
    def add_medicine():
        form = MedicineForm()
        if form.validate_on_submit():
            new_medicine = Medicine(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                stock=form.stock.data
            )
            db.session.add(new_medicine)
            db.session.commit()
            update_inventory(new_medicine.id, new_medicine.stock)
            return redirect(url_for('list_medicines'))
        return render_template('add_medicine.html', form=form)

    @app.route('/employees')
    @login_required
    def list_employees():
        employees = Employee.query.all()
        return render_template('employees.html', employees=employees)

    @app.route('/add_employee', methods=['GET', 'POST'])
    @login_required
    def add_employee():
        form = EmployeeForm()
        if form.validate_on_submit():
            new_employee = Employee(
                name=form.name.data,
                position=form.position.data,
                salary=form.salary.data,
                hire_date=form.hire_date.data
            )
            db.session.add(new_employee)
            db.session.commit()
            return redirect(url_for('list_employees'))
        return render_template('add_employee.html', form=form)

    @app.route('/customers')
    @login_required
    def list_customers():
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)

    @app.route('/add_customer', methods=['GET', 'POST'])
    @login_required
    def add_customer():
        form = CustomerForm()
        if form.validate_on_submit():
            new_customer = Customer(
                name=form.name.data,
                contact_info=form.contact_info.data,
                address=form.address.data
            )
            db.session.add(new_customer)
            db.session.commit()
            return redirect(url_for('list_customers'))
        return render_template('add_customer.html', form=form)

    @app.route('/suppliers')
    @login_required
    def list_suppliers():
        suppliers = Supplier.query.all()
        return render_template('suppliers.html', suppliers=suppliers)

    @app.route('/add_supplier', methods=['GET', 'POST'])
    @login_required
    def add_supplier():
        form = SupplierForm()
        if form.validate_on_submit():
            new_supplier = Supplier(
                name=form.name.data,
                contact_info=form.contact_info.data,
                address=form.address.data
            )
            db.session.add(new_supplier)
            db.session.commit()
            return redirect(url_for('list_suppliers'))
        return render_template('add_supplier.html', form=form)

    @app.route('/purchases')
    @login_required
    def list_purchases():
        purchases = Purchase.query.all()
        return render_template('purchases.html', purchases=purchases)

    @app.route('/add_purchase', methods=['GET', 'POST'])
    @login_required
    def add_purchase():
        form = PurchaseForm()
        form.medicine_id.choices = [(m.id, m.name) for m in Medicine.query.all()]
        form.supplier_id.choices = [(s.id, s.name) for s in Supplier.query.all()]

        if form.validate_on_submit():
            new_purchase = Purchase(
                medicine_id=form.medicine_id.data,
                quantity=form.quantity.data,
                purchase_date=form.purchase_date.data,
                supplier_id=form.supplier_id.data
            )
            db.session.add(new_purchase)

            medicine = Medicine.query.get(form.medicine_id.data)
            if medicine:
                medicine.stock += form.quantity.data

            db.session.commit()
            update_inventory(form.medicine_id.data, form.quantity.data)
            return redirect(url_for('list_purchases'))
        return render_template('add_purchase.html', form=form)

    @app.route('/returns', methods=['GET', 'POST'])
    @login_required
    def process_return():
        form = ReturnForm()
        form.sale_id.choices = [(s.id, f"{s.medicine.name} - {s.sale_date} - {s.quantity} sold") for s in
                                Sale.query.all()]

        if form.validate_on_submit():
            sale = Sale.query.get(form.sale_id.data)
            if sale and sale.quantity >= form.quantity.data:
                # Get the unit price from the Medicine table
                medicine = sale.medicine
                if medicine:
                    unit_price = medicine.price
                    refund_amount = unit_price * form.quantity.data

                    # Create a new return record
                    new_return = Return(
                        sale_id=form.sale_id.data,
                        quantity=form.quantity.data,
                        return_date=form.return_date.data
                    )
                    db.session.add(new_return)

                    # Update the medicine stock
                    medicine.stock += form.quantity.data

                    # Update the sale record
                    sale.quantity -= form.quantity.data

                    db.session.commit()
                    update_inventory(sale.medicine_id, form.quantity.data)
                    update_financials(form.return_date.data)

                    print(f"Refund amount: {refund_amount}")

                    return redirect(url_for('inventory_report'))
                else:
                    flash('未找到药品。')
            else:
                flash('退货数量超过销售数量。')
        return render_template('process_return.html', form=form)

    @app.route('/inventory_report')
    @login_required
    def inventory_report():
        medicines = Medicine.query.all()
        return render_template('inventory_report.html', medicines=medicines)

    @app.route('/sales')
    @login_required
    def list_sales():
        sales = Sale.query.all()
        return render_template('sales.html', sales=sales)

    @app.route('/add_sale', methods=['GET', 'POST'])
    @login_required
    def add_sale():
        form = SaleForm()
        form.medicine_id.choices = [(m.id, m.name) for m in Medicine.query.all()]
        form.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]

        if form.validate_on_submit():
            medicine = Medicine.query.get(form.medicine_id.data)
            if medicine and medicine.stock >= form.quantity.data:
                total_price = medicine.price * form.quantity.data

                new_sale = Sale(
                    medicine_id=form.medicine_id.data,
                    customer_id=form.customer_id.data,
                    quantity=form.quantity.data,
                    sale_date=form.sale_date.data,
                    total_price=total_price
                )
                db.session.add(new_sale)

                medicine.stock -= form.quantity.data

                db.session.commit()
                update_inventory(form.medicine_id.data, -form.quantity.data)
                update_financials(form.sale_date.data)
                return redirect(url_for('list_sales'))
            else:
                flash('库存不足。')
        return render_template('add_sale.html', form=form)

    @app.route('/sales_report')
    @login_required
    def sales_report():
        sales = Sale.query.all()
        return render_template('sales_report.html', sales=sales)

    @app.route('/returns_report')
    @login_required
    def returns_report():
        returns = Return.query.all()
        return render_template('returns_report.html', returns=returns)

    @app.route('/financial_report')
    @login_required
    def financial_report():
        today = date.today()

        # Calculate today's sales
        today_sales = db.session.query(func.sum(Sale.total_price)).filter(
            func.date(Sale.sale_date) == today).scalar() or 0

        # Calculate today's returns
        today_returns = db.session.query(func.sum(Return.quantity * Medicine.price)) \
                            .select_from(Return).join(Sale).join(Medicine).filter(
            func.date(Return.return_date) == today).scalar() or 0

        today_net = today_sales - today_returns

        # Calculate this month's sales
        first_day_of_month = today.replace(day=1)
        month_sales = db.session.query(func.sum(Sale.total_price)).filter(
            Sale.sale_date >= first_day_of_month).scalar() or 0

        # Calculate this month's returns
        month_returns = db.session.query(func.sum(Return.quantity * Medicine.price)) \
                            .select_from(Return).join(Sale).join(Medicine).filter(
            Return.return_date >= first_day_of_month).scalar() or 0

        month_net = month_sales - month_returns

        return render_template('financial_report.html', today_sales=today_sales, today_returns=today_returns,
                               today_net=today_net, month_sales=month_sales, month_returns=month_returns,
                               month_net=month_net)

    @app.route('/users')
    @login_required
    def list_users():
        users = User.query.all()
        return render_template('users.html', users=users)

    @app.route('/add_user', methods=['GET', 'POST'])
    @login_required
    def add_user():
        form = UserForm()
        if form.validate_on_submit():
            new_user = User(
                username=form.username.data,
                is_admin=form.is_admin.data
            )
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash('用户添加成功。')
            return redirect(url_for('list_users'))
        return render_template('add_user.html', form=form)

    @app.route('/view_logs')
    @login_required
    def view_logs():
        with open('logs/app.log', 'r') as f:
            log_content = f.read()
        return render_template('view_logs.html', log_content=log_content)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # 只有登录用户才能访问此页面
        return render_template('dashboard.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                session['user_id'] = user.id
                session['username'] = user.username  # 保存用户名以便显示
                flash('登录成功。', 'success')
                return redirect(url_for('index'))
            else:
                flash('用户名或密码错误。', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)  # 从会话中移除用户 ID
        flash('您已成功登出。')
        return redirect(url_for('login'))