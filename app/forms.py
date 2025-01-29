from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, DateField, SubmitField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Length, NumberRange, EqualTo

class MedicineForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(), Length(max=255)])
    description = StringField('描述')
    price = DecimalField('价格', validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField('库存', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('添加药品')

class EmployeeForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired()])
    position = StringField('职位')
    salary = DecimalField('薪水', places=2)
    hire_date = DateField('入职日期', format='%Y-%m-%d')
    submit = SubmitField('提交')

class CustomerForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired()])
    contact_info = StringField('联系方式')
    address = StringField('地址')
    submit = SubmitField('提交')

class SupplierForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(), Length(max=255)])
    contact_info = StringField('联系方式', validators=[Length(max=255)])
    address = StringField('地址')
    submit = SubmitField('添加供应商')

class PurchaseForm(FlaskForm):
    medicine_id = SelectField('药品', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('数量', validators=[DataRequired(), NumberRange(min=1)])
    purchase_date = DateField('采购日期', format='%Y-%m-%d', validators=[DataRequired()])
    supplier_id = SelectField('供应商', coerce=int, validators=[DataRequired()])
    submit = SubmitField('添加采购')

class ReturnForm(FlaskForm):
    sale_id = SelectField('销售', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('数量', validators=[DataRequired(), NumberRange(min=1)])
    return_date = DateField('退货日期', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('处理退货')

class SaleForm(FlaskForm):
    medicine_id = SelectField('药品', coerce=int, validators=[DataRequired()])
    customer_id = SelectField('客户', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('数量', validators=[DataRequired(), NumberRange(min=1)])
    sale_date = DateField('销售日期', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('添加销售')

class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('管理员')
    submit = SubmitField('提交')

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')