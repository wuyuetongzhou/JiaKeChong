from flask import render_template, g, request, jsonify, current_app, session, redirect, url_for
from app import db, constants
from . import admin_bp
from ..models import User, Product, Case, News, Introduction, Solution, Category, NewsClass
from app.utils.image_storage import qiniu_image_store
from app.utils.response_code import RET
from app.utils.common import user_login_data
from app import csrf


@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        if user_id:
            return redirect(url_for('admin.admin_index'))
        return render_template('admin/login.html')

    # -----------post------------------
    username = request.form.get('username')
    print(username)
    password = request.form.get('password')
    if not all([username, password]):
        return render_template('admin/login.html', errmsg='用户名或密码未输入')

    user = None
    try:
        user = User.query.filter_by(username=username).first()
        print(user)
    except Exception as e:
        # current_app.logger.error(e)
        print(e)
        return render_template('admin/login.html', errmsg='用户不存在')

    if user is not None and user.verify_password(password):
        #  记住登陆的状态
        session['user_id'] = user.id
        session['username'] = user.username

        return redirect(url_for('admin.admin_index'))
    else:
        return render_template('admin/login.html', errmsg='用户名或密码错误')


@admin_bp.route('/index')
@user_login_data
def admin_index():
    user = g.user
    if user:
        return render_template('admin/index.html', user=user.to_dict())
    else:
        return redirect(url_for('admin.admin_login'))


@admin_bp.route('/logout')
def admin_logout():
    # 就是把所有记录下来的的东西全部变为没有
    session.pop('user_id', None)
    session.pop('username', None)

    return redirect(url_for('.admin_login'))


@admin_bp.route('/user_count')
def user_count():
    # 查询总新闻数
    news_count = 0
    try:
        filters = []
        news_count = News.query.filter(*filters).count()
    except Exception as e:
        current_app.logger.error(e)

        # 查询产品总数
        product_count = 0
    try:
        filters = []
        product_count = Product.query.filter(*filters).count()
    except Exception as e:
        current_app.logger.error(e)

        # 查询案例总数
        case_count = 0
    try:
        filters = []
        case_count = Case.query.filter(*filters).count()
    except Exception as e:
        current_app.logger.error(e)

    # # 查询月新增数
    # mon_count = 0
    # try:
    #     now = time.localtime()
    #     mon_begin = '%d-%02d-01' % (now.tm_year, now.tm_mon)
    #     mon_begin_date = datetime.strptime(mon_begin, '%Y-%m-%d')
    #     mon_count = User.query.filter(User.is_admin == False, User.create_time >= mon_begin_date).count()
    # except Exception as e:
    #     current_app.logger.error(e)
    #
    # # 查询日新增数
    # day_count = 0
    # try:
    #     now = time.localtime()
    #     day_begin = '%d-%02d-%02d' % (now.tm_year, now.tm_mon, now.tm_mday)
    #     day_begin_date = datetime.strptime(day_begin, '%Y-%m-%d')
    #     day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    # except Exception as e:
    #     current_app.logger.error(e)
    #
    # # 查询图表信息
    # # 获取到当天00:00:00时间
    #
    # now_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d'), '%Y-%m-%d')
    # # 定义空数组，保存数据
    # active_date = []
    # active_count = []
    #
    # # 依次添加数据，再反转
    # for i in range(0, 31):
    #     begin_date = now_date - timedelta(days=i)
    #     end_date = now_date - timedelta(days=(i - 1))
    #     active_date.append(begin_date.strftime('%Y-%m-%d'))
    #     count = 0
    #     try:
    #         count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
    #                                   User.last_login < end_date).count()
    #     except Exception as e:
    #         current_app.logger.error(e)
    #     active_count.append(count)
    #
    # active_date.reverse()
    # active_count.reverse()

    data = {"news_count": news_count, "product_count": product_count, "case_count": case_count}
    return render_template('admin/user_count.html', data=data)


@admin_bp.route('/user_list')
def user_list():
    """获取用户列表"""
    pass
    # # 获取参数
    # page = request.args.get("p", 1)
    # try:
    #     page = int(page)
    # except Exception as e:
    #     current_app.logger.error(e)
    #     page = 1
    #
    # # 设置变量默认值
    # users = []
    # current_page = 1
    # total_page = 1
    #
    # # 查询数据
    # try:
    #     paginate = User.query.filter(User.is_admin == False).order_by(User.last_login.desc()).paginate(page,
    #                                                                                                    constants.ADMIN_USER_PAGE_MAX_COUNT,
    #                                                                                                    False)
    #     users = paginate.items
    #     current_page = paginate.page
    #     total_page = paginate.pages
    # except Exception as e:
    #     current_app.logger.error(e)
    #
    # # 将模型列表转成字典列表
    # users_list = []
    # for user in users:
    #     users_list.append(user.to_admin_dict())
    #
    # context = {"total_page": total_page, "current_page": current_page, "users": users_list}
    context = ''
    return render_template('admin/user_list.html', data=context)


@admin_bp.route('/submit-image', methods=['GET', 'POST'])
@csrf.exempt
def submit_image():
    '''富文本图片上传方法'''
    file = request.files['file']
    try:
        img = file.read()
        # print(img)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
    try:
        key = qiniu_image_store(img)
    except Exception as e:
        current_app.logger.error(e)

    img_url = constants.QINIU_DOMIN_PREFIX + key
    return '{"error":false,"path":"' + img_url + '"}'


@admin_bp.route('/news_release', methods=['POST', 'GET'])
def news_release():
    '''编辑发布新闻资讯'''
    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        digest = request.form.get('digest')
        content = request.form.get('content')
        index_image = request.files.get('index_image')

        # print(title, digest)
        # 1.2 尝试读取图片
        try:
            index_image = index_image.read()
            # print(img)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
        if not index_image:
            return jsonify(errno=RET.NODATA, errmsg="没有选择图片")
        # 2. 将标题图片上传到七牛
        try:
            key = qiniu_image_store(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        # 3. 初始化新闻模型，并设置相关数据
        news = News()
        news.title = title
        news.class_id = category_id
        news.digest = digest
        news.content = content
        news.image_url = constants.QINIU_DOMIN_PREFIX + key
        if not all([title, digest, content]):
            return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")
        try:
            db.session.add(news)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
        return jsonify(errno=RET.OK, errmsg="发布成功")

    # ----------------------GET------------------------------------
    else:
        # 查询分类数据
        category_list = []
        filters = [NewsClass.status == 1]
        try:
            category_list = NewsClass.query.filter(*filters)
        except Exception as e:
            current_app.logger.error(e)
        category_list_dict = []
        for category in category_list:
            category_list_dict.append(category.to_dict())
        data = {
            "category_list": category_list_dict
        }
        return render_template('admin/news_release.html', data=data)


@admin_bp.route('/news_list', methods=['GET'])
def news_list():
    '''返回新闻列表'''

    page = request.args.get('p', 1)
    keywords = request.args.get('keywords', '')
    try:
        page = int(page)
    except Exception as e:
        # current_app.logger.error(e)
        page = 1

    news_list = []
    current_page = 1
    total_page = 1
    try:
        filters = [News.status==1]
        if keywords:
            filters.append(News.title.contains(keywords))

        paginate = News.query.filter(*filters).order_by(
            News.create_time.desc()).paginate(page, constants.ADMIN_PER_PAGE_10, False)

        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)

    news_list_dict = []
    for news in news_list:
        news_list_dict.append(news.to_basic_dict())

    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_list": news_list_dict
    }

    return render_template('admin/news_list.html', data=data)


@admin_bp.route('/news_modify', methods=['GET', 'POST'])
def news_modify():
    if request.method == 'GET':
        news_id = request.args.get('news_id')
        if not news_id:
            return render_template('admin/news_modify.html', data={"errmsg": "未查询到此新闻"})

        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template('admin/news_modify.html', data={"errmsg": "新闻不存在"})

        category_list = []
        filters = [NewsClass.status == 1]
        try:
            category_list = NewsClass.query.filter(*filters)
        except Exception as e:
            current_app.logger.error(e)
        category_list_dict = []
        for category in category_list:
            category_list_dict.append(category.to_dict())

        data = {
            'news': news.to_dict() if news else None,
            "category_list": category_list_dict
        }
        return render_template('admin/news_modify.html', data=data)

    # ----------------post-------------------
    else:
        news_id = request.form.get('news_id')
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        digest = request.form.get('digest')
        content = request.form.get('content')
        index_image = request.files.get('index_image')
        if not all([title, digest, content]):
            return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")

        try:
            category_id = int(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg='请选择新闻类型')

        news = None
        try:
            news = News.query.get(news_id)
            # print(news)
        except Exception as e:
            current_app.logger.error(e)
        if index_image:
            try:
                index_image = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")

            try:
                key = qiniu_image_store(index_image)
                news.image_url = constants.QINIU_DOMIN_PREFIX + key
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

        news.title = title
        news.digest = digest
        news.content = content
        news.class_id = category_id

        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
        return jsonify(errno=RET.OK, errmsg="修改成功")


@admin_bp.route('/news_delete/<int:id>', methods=['GET', 'POST'])
def news_delete(id):
    product = News.query.get_or_404(id)
    product.status = 0
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="删除成功")


@admin_bp.route('/product_release', methods=["GET", "POST"])
def product_release():
    '''编辑发布产品'''
    if request.method == 'POST':
        title = request.form.get('title')
        category_id = request.form.get('category_id')
        content = request.form.get('content')
        img = request.files.get('img')

        # print(title, content)

        # 1.2 尝试读取图片
        try:
            img = img.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
        if not img:
            return jsonify(errno=RET.NODATA, errmsg="没有图片")
        # 2. 将标题图片上传到七牛
        try:
            key = qiniu_image_store(img)
            # print('保存图片到七牛云', key)
        except Exception as e:
            # current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        # 3. 初始化新闻模型，并设置相关数据
        try:
            category_id = int(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        if not all([title, content, category_id]):
            return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")
        product = Product()
        product.name = title
        product.content = content
        product.category_id = category_id
        product.image_url = constants.QINIU_DOMIN_PREFIX + key

        try:
            db.session.add(product)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
        return jsonify(errno=RET.OK, errmsg="发布成功")

    # 查询分类数据
    category_list = []
    filters = [Category.status == 1]
    try:
        category_list = Category.query.filter(*filters)
    except Exception as e:
        current_app.logger.error(e)
    category_list_dict = []
    for category in category_list:
        category_list_dict.append(category.to_dict())
    category_data = {
        "category_list": category_list_dict
    }

    return render_template('admin/product_release.html', category_data=category_data)


@admin_bp.route('/product_list', methods=['GET', 'POST'])
def product_list():
    '''返回产品列表'''
    page = request.args.get('p', 1)
    keywords = request.args.get('keywords', '')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    product_list = []
    current_page = 1
    total_page = 1
    try:
        filters = [Product.status == 1]
        if keywords:
            filters.append(Product.name.contains(keywords))
        paginate = Product.query.filter(*filters).order_by(
            Product.create_time.desc()).paginate(page, constants.ADMIN_PER_PAGE_10, False)
        product_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    product_list_dict = []
    for product in product_list:
        product_list_dict.append(product.to_dict())

    data = {
        'product_list': product_list_dict,
        'total_page': total_page,
        'current_page': current_page
    }
    # print(data)
    return render_template('admin/product_list.html', data=data)


@admin_bp.route('/product_modify', methods=['GET', 'POST'])
def product_modify():
    if request.method == 'GET':
        product_id = request.args.get('product_id')
        if not product_id:
            return render_template('admin/product_modify.html', data={"errmsg": "未查询到此产品"})

        product = None
        try:
            product = Product.query.get(product_id)
        except Exception as e:
            current_app.logger.error(e)

        if not product:
            return render_template('admin/product_modify.html', data={"errmsg": "产品不存在"})

        data = {
            'product': product.to_dict() if product else None
        }

        # 查询分类数据
        category_list = []
        filters = [Category.status == 1]
        try:
            category_list = Category.query.filter(*filters)
        except Exception as e:
            current_app.logger.error(e)
        category_list_dict = []
        for category in category_list:
            category_list_dict.append(category.to_dict())
        category_data = {
            "category_list": category_list_dict
        }

        return render_template('admin/product_modify.html', data=data, category_data=category_data)

    # ----------------post-------------------
    product_id = request.form.get('product_id')
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    content = request.form.get('content')
    # content_html = request.form.get('content_html')
    index_image = request.files.get('index_image')
    # print([name, content, content, category])

    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='请选择产品类型')

    if not all([name, content, content, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")
    # 1.2 尝试读取图片

    product = None
    try:
        product = Product.query.get(product_id)
        # print(product)
    except Exception as e:
        current_app.logger.error(e)

    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
        if not index_image:
            return jsonify(errno=RET.NODATA, errmsg="没有选择图片")
        try:
            key = qiniu_image_store(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        product.image_url = constants.QINIU_DOMIN_PREFIX + key

    product.name = name
    product.content = content
    product.category_id = category_id
    print(category_id)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="修改成功")


@admin_bp.route('/product_delete/<int:id>', methods=['GET', 'POST'])
def product_delete(id):
    product = Product.query.get_or_404(id)
    product.status = 0
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="删除成功")


@admin_bp.route('/case_release', methods=['GET', 'POST'])
def case_release():
    '''编辑发布案例'''
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category_id = request.form.get('category_id')
        img = request.files.get('img')

        # print(title, content)
        # 1.2 尝试读取图片
        try:
            category_id = int(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg='参数错误')
        try:
            img = img.read()
            # print(img)
        except Exception as e:
            # current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
        if not img:
            return jsonify(errno=RET.NODATA, errmsg="没有图片")
        # 2. 将标题图片上传到七牛
        try:
            key = qiniu_image_store(img)
            # print('保存图片到七牛云', key)
        except Exception as e:
            # current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        # 3. 初始化新闻模型，并设置相关数据
        case = Case()
        case.name = title
        case.content = content
        case.category_id = category_id
        case.image_url = constants.QINIU_DOMIN_PREFIX + key
        if not all([title, content, category_id]):
            return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")
        try:
            db.session.add(case)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
        return jsonify(errno=RET.OK, errmsg="发布成功")

    # 查询分类数据
    category_list = []
    filters = [Category.status == 1]
    try:
        category_list = Category.query.filter(*filters)
    except Exception as e:
        current_app.logger.error(e)
    category_list_dict = []
    for category in category_list:
        category_list_dict.append(category.to_dict())
    category_data = {
        "category_list": category_list_dict
    }

    return render_template('admin/case_release.html', category_data=category_data)


@admin_bp.route('/case_list', methods=['GET', 'POST'])
def case_list():
    '''返回案例列表'''
    page = request.args.get('p', 1)
    keywords = request.args.get('keywords', '')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    case_list = []
    current_page = 1
    total_page = 1

    filters = [Case.status == 1]

    try:
        if keywords:
            filters.append(Case.name.contains(keywords))

        paginate = Case.query.filter(*filters).order_by(
            Case.create_time.desc()).paginate(page, constants.ADMIN_PER_PAGE_10, False)

        case_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)

    case_list_dict = []
    for case in case_list:
        case_list_dict.append(case.to_dict())

    data = {
        'case_list': case_list_dict,
        'total_page': total_page,
        'current_page': current_page
    }
    return render_template('admin/case_list.html', data=data)


@admin_bp.route('/case_delete/<int:id>', methods=['GET', 'POST'])
def case_delete(id):
    case = Case.query.get_or_404(id)
    case.status = 0
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="删除成功")


@admin_bp.route('/case_modify', methods=['GET', 'POST'])
def case_modify():
    '''修改应用案例'''
    if request.method == 'GET':
        case_id = request.args.get('case_id')
        if not case_id:
            return render_template('admin/case_modify.html', data={"errmsg": "未查询到此案例"})

        case = None
        try:
            case = Case.query.get(case_id)
        except Exception as e:
            current_app.logger.error(e)

        if not case:
            return render_template('admin/case_modify.html', data={"errmsg": "案例不存在"})

        data = {
            'case': case.to_dict() if case else None
        }

        # 查询分类数据
        category_list = []
        filters = [Category.status == 1]
        try:
            category_list = Category.query.filter(*filters)
        except Exception as e:
            current_app.logger.error(e)
        category_list_dict = []
        for category in category_list:
            category_list_dict.append(category.to_dict())
        category_data = {
            "category_list": category_list_dict
        }
        return render_template('admin/case_modify.html', data=data, category_data=category_data)

    # ----------------post-------------------
    case_id = request.form.get('case_id')
    name = request.form.get('name')
    category_id = request.form.get('category_id')
    content = request.form.get('content')
    # content_html = request.form.get('content_html')
    index_image = request.files.get('index_image')

    try:
        category_id = int(category_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='请选择案例类型')

    if not all([name, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")

    case = None
    try:
        case = Case.query.get(case_id)
    except Exception as e:
        current_app.logger.error(e)

    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
        try:
            key = qiniu_image_store(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        case.image_url = constants.QINIU_DOMIN_PREFIX + key

    case.name = name
    case.content = content
    # product.content_html = content_html

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="修改成功")


@admin_bp.route('/about_release', methods=['GET', 'POST'])
def about_release():
    '''编辑发布企业文化'''
    if request.method == 'POST':
        name = request.form.get('name')
        content = request.form.get('content')
        index_image = request.files.get('index_image')

        if not all([name, content]):
            return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")

        about_us = Introduction()
        if index_image:
            try:
                index_image = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
            try:
                key = qiniu_image_store(index_image)
                about_us.image_url = constants.QINIU_DOMIN_PREFIX + key
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

        about_us.name = name
        about_us.content = content

        try:
            db.session.add(about_us)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
        return jsonify(errno=RET.OK, errmsg="发布成功")
    return render_template('admin/about_release.html')


@admin_bp.route('/about_list', methods=['GET', 'POST'])
def about_list():
    '''返回文化列表'''
    keywords = request.args.get('keywords', '')
    about_list = []
    filters = [Product.status == 1]
    if keywords:
        filters.append(Product.name.contains(keywords))
    try:
        about_list = Introduction.query.filter(*filters)
    except Exception as e:
        current_app.logger.error(e)

    about_list_dict = []
    for about_us in about_list:
        about_list_dict.append(about_us.to_dict())
    data = {
        'about_list': about_list_dict,
    }
    return render_template('admin/about_list.html', data=data)


@admin_bp.route('/about_modify', methods=['GET', 'POST'])
def about_modify():
    '''修改企业文化'''
    if request.method == 'GET':
        about_id = request.args.get('about_id')
        if not about_id:
            return render_template('admin/about_modify.html', data={"errmsg": "未查询到此案例"})

        about_us = None
        try:
            about_us = Introduction.query.get(about_id)
        except Exception as e:
            current_app.logger.error(e)

        if not about_us:
            return render_template('admin/about_modify.html', data={"errmsg": "案例不存在"})

        data = {
            'about': about_us.to_dict() if about_us else None
        }
        return render_template('admin/about_modify.html', data=data)

    # ----------------post-------------------
    about_id = request.form.get('about_id')
    name = request.form.get('name')
    content = request.form.get('content')
    # content_html = request.form.get('content_html')
    index_image = request.files.get('index_image')

    if not all([name, content]):
        return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")

    about_us = None
    try:
        about_us = Introduction.query.get(about_id)
    except Exception as e:
        current_app.logger.error(e)

    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")

        try:
            key = qiniu_image_store(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        about_us.image_url = constants.QINIU_DOMIN_PREFIX + key

    about_us.name = name
    about_us.content = content
    # product.content_html = content_html

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="修改成功")


@admin_bp.route('/about_delete/<int:id>', methods=['GET', 'POST'])
def about_delete(id):
    about = Introduction.query.get_or_404(id)
    about.status = 0
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="删除成功")


@admin_bp.route('/solution_release', methods=['GET', 'POST'])
def solution_release():
    '''编辑发布解决方案'''
    if request.method == 'POST':
        name = request.form.get('name')
        digest = request.form.get('digest')
        index_image = request.files.get('index_image')
        content = request.form.get('content')

        if not all([name, content, digest]):
            return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")

        solution = Solution()
        if index_image:
            try:
                index_image = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")
            try:
                key = qiniu_image_store(index_image)
                solution.image_url = constants.QINIU_DOMIN_PREFIX + key
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

        solution.name = name
        solution.digest = digest
        solution.content = content

        try:
            db.session.add(solution)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
        return jsonify(errno=RET.OK, errmsg="发布成功")
    return render_template('admin/solution_release.html')


@admin_bp.route('/solution_list', methods=['GET', 'POST'])
def solution_list():
    '''返回解决方案列表'''
    keywords = request.args.get('keywords', '')
    solution_list = []
    filters = [Solution.status == 1]
    if keywords:
        filters.append(Product.name.contains(keywords))
    try:
        solution_list = Solution.query.filter(*filters).order_by(Solution.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)

    solution_list_dict = []
    for solution in solution_list:
        solution_list_dict.append(solution.to_dict())
    data = {
        'solution_list': solution_list_dict,
    }
    return render_template('admin/solution_list.html', data=data)


@admin_bp.route('/solution_modify', methods=['GET', 'POST'])
def solution_modify():
    '''修改解决方案'''
    if request.method == 'GET':
        solution_id = request.args.get('solution_id')
        if not solution_id:
            return render_template('admin/solution_modify.html', data={"errmsg": "未查询到此方案"})

        solution = None
        try:
            solution = Solution.query.get(solution_id)
        except Exception as e:
            current_app.logger.error(e)

        if not solution:
            return render_template('admin/solution_modify.html', data={"errmsg": "未查询到此方案"})

        data = {
            'solution': solution.to_dict() if solution else None
        }
        return render_template('admin/solution_modify.html', data=data)

    # ----------------post-------------------
    solution_id = request.form.get('solution_id')
    name = request.form.get('name')
    digest = request.form.get('digest')
    content = request.form.get('content')
    index_image = request.files.get('index_image')

    if not all([name, content, digest]):
        return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")

    solution = None
    try:
        solution = Solution.query.get(solution_id)
    except Exception as e:
        current_app.logger.error(e)

    if index_image:
        try:
            index_image = index_image.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="图片读取失败")

        try:
            key = qiniu_image_store(index_image)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
        solution.image_url = constants.QINIU_DOMIN_PREFIX + key

    solution.name = name
    solution.digest = digest
    solution.content = content

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="修改成功")


@admin_bp.route('/solution_delete/<int:id>', methods=['GET', 'POST'])
def solution_delete(id):
    solution = Solution.query.get_or_404(id)
    solution.status = 0
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="删除成功")


@admin_bp.route('/category_release', methods=['GET', 'POST'])
def category_release():
    '''编辑发布分类'''
    if request.method == 'POST':
        name = request.form.get('name')
        print(name)
        if not all([name,]):
            return jsonify(errno=RET.PARAMERR, errmsg="内容填写不完整")

        category = Category()
        category.name = name
        try:
            db.session.add(category)
            db.session.commit()
        except Exception as e:
            current_app.logger.error(e)
            db.session.rollback()
            return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
        return jsonify(errno=RET.OK, errmsg="发布成功")
    return render_template('admin/category_release.html')


@admin_bp.route('/category_list', methods=['GET', 'POST'])
def category_list():
    '''返回文化列表'''
    keywords = request.args.get('keywords', '')
    category_list = []
    filters = [Category.status == 1]
    if keywords:
        filters.append(Category.name.contains(keywords))
    try:
        category_list = Category.query.filter(*filters)
    except Exception as e:
        current_app.logger.error(e)

    category_list_dict = []
    for category in category_list:
        category_list_dict.append(category.to_dict())
    data = {
        'category_list': category_list_dict,
    }
    return render_template('admin/category_list.html', data=data)


@admin_bp.route('/category_delete/<int:id>', methods=['GET', 'POST'])
def category_delete(id):
    category = Category.query.get_or_404(id)
    category.status = 0
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK, errmsg="删除成功")