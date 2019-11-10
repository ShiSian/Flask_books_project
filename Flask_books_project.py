# _*_ coding:utf-8 _*_
# 使用模板的相关引用
from flask import Flask, render_template, flash, request, redirect, url_for
# 1.1-导入SQLAlchemy扩展
from flask_sqlalchemy import SQLAlchemy
# 使用表单的相关引用
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# 解决编码问题
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
# 1.2-配置数据库对象（db）：数据库地址
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:mysql123@127.0.0.1/flask_books'
# 1.2-配置数据库对象（db）：关闭自动跟踪修改
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 5.3设置密钥
app.secret_key = 'flask_book'
# 1.2-创建数据库对象（db）
db = SQLAlchemy(app)
# 1.3-终端创建数据库（在mysql中）


# 3-定义书和作者类型
# 3.1-作者模型
class Author(db.Model):
    # 定义表名
    __tablename__ = 'authors'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    # 关系引用
    books = db.relationship('Book', backref='author')

    # 打印函数的定义
    def __repr__(self):
        return '作者: %s' % self.name


# 3.2-书籍模型
class Book(db.Model):
    # 定义表名
    __tablename__ = 'books'
    # 定义字段
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(16), unique=True)
    # 定义外键
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))

    # 定义打印函数
    def __repr__(self):
        return 'Book: %s %s' % (self.name, self.author_id)


# 自定义表单类
class AuthorForm(FlaskForm):
    author = StringField('作者', validators=[DataRequired()])
    book = StringField('书籍', validators=[DataRequired()])
    submit = SubmitField('提交')


# 查询数据库是否有该ID的作者
@app.route('/delete_author/<author_id>')
def delete_author(author_id):
    # 1、查询数据库是否有该ID的作者
    author = Author.query.get(author_id)
    # 2、如果有就删除
    if author:
        try:
            # 2.1首先删除该作者的书籍
            Book.query.filter_by(author_id=author.id).delete()

            # 2.2然后删除作者
            db.session.delete(author)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除作者出错')
            db.session.rollback()
    else:
        # 3、没有提示错误
        flash('没有找到该作者')
    # rederict（需要传入的网址/路由地址）
    # url_for('视图函数名'):
    return redirect(url_for('index'))

@app.route('/delete_book/<book_id>')
def delete_book(book_id):
    # 1、查询数据库是否有该ID的书，如果有就删除，没有就提示错误
    book = Book.query.get(book_id)
    # 2、如果有就删除
    if book:
        try:
            db.session.delete(book)
            db.session.commit()
        except Exception as e:
            print(e)
            flash('删除数据出错')
            db.session.rollback()
    else:
        # 3、没有提示错误
        flash('没有找到该书籍')
    # rederict（需要传入的网址/路由地址）
    # url_for('视图函数名'):
    return redirect(url_for('index'))


@app.route('/', methods=['GET', 'POST'])
def index():
    # 创建自定义的表单类
    author_form = AuthorForm()
    # 1、调用wtf的函数实现验证
    if author_form.validate_on_submit():
        # 2、验证通过获取数据
        author_name = author_form.author.data
        book_name = author_form.book.data
        # 3、判断作者是否存在
        author = Author.query.filter_by(name=author_name).first()
        # 4、如果作者存在
        if author:
            # 判断书籍是否存在
            book = Book.query.filter_by(name=book_name).first()
            # 如果重复就提示错误
            if book:
                flash('存在同名书籍')
            # 如果不重复就添加数据
            else:
                try:
                    new_book = Book(name=book_name, author_id=author.id)
                    db.session.add(new_book)
                    db.session.commit()
                except Exception as e:
                    print e
                    flash('增加书籍失败')
                    db.session.rollback()
        else:
            # 5、如果作者不存在，添加作者和书籍
            try:
                new_author = Author(name=author_name)
                db.session.add(new_author)
                db.session.commit()

                new_book = Book(name=book_name, author_id=new_author.id)
                db.session.add(new_book)
                db.session.commit()
            except Exception as e:
                print e
                flash('添加作者和书籍失败')
                db.session.rollback()
    else:
        # 6、验证不过就提示错误
        if request.method == 'POST':
            flash('参数不全')
    # 查询所有的作者信息，让信息传递给模板
    authors = Author.query.all()

    return render_template('books.html', authors=authors, form=author_form)


if __name__ == '__main__':
    # 删除所有表
    db.drop_all()
    # 创建所有表
    db.create_all()
    # 添加数据
    au1 = Author(name='张三')
    au2 = Author(name='李四')
    db.session.add_all([au1, au2])
    db.session.commit()
    bk1 = Book(name='张三自传', author_id=au1.id)
    bk2 = Book(name='张三恩仇录', author_id=au1.id)
    bk3 = Book(name='我和张三不得不说的几件事', author_id=au2.id)
    db.session.add_all([bk1, bk2, bk3])
    db.session.commit()
    app.run(debug=True)
