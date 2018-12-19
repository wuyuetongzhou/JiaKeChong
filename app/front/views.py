from flask import Flask, render_template, request, session, redirect, url_for, current_app
from . import front_bp
from ..models import News, Product, Case, Solution, Category, NewsClass

app = Flask(__name__)


@front_bp.route('/', methods=['GET', 'POST'])
def index():
    # solution_list = []
    # filters = [Solution.status == 1]
    # try:
    #     solution_list = Solution.query.filter(*filters)
    # except Exception as e:
    #     current_app.logger.error(e)
    # solution_list_dict = []
    # for solution in solution_list:
    #     solution_list_dict.append(solution.to_dict())

    product_list = []
    try:
        filters = [Product.status == 1]
        product_list = Product.query.filter(*filters).order_by(Product.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)

    product_list_dict = []
    for product in product_list:
        product_list_dict.append(product.to_dict())

    data = {
        "product_list": product_list_dict
    }

    return render_template('front/index.html', data=data)


@front_bp.route('/solution', methods=['GET'])
def solution():
    solution_id = request.args.get('solution_id')
    if not solution_id:
        return render_template('front/solution_detail.html', data={'errmsg':'未查询到此解决方案'})
    solution = None
    try:
        solution = Solution.query.get(solution_id)
    except Exception as e:
        current_app.logger.error(e)
    if not solution:
        return render_template('front/solution_detail.html', data={'errmsg': '未查询到此解决方案'})

    data = {
        "solution": solution.to_dict() if solution else None
    }
    return render_template('front/solution_detail.html', data=data)


@front_bp.route('/product', methods=['GET'])
def product():
    product_list = []
    category_id = request.args.get('id')
    try:
        filters = [Product.status == 1]
        if category_id:
            filters.append(Product.category_id == category_id)
        product_list = Product.query.filter(*filters).order_by(Product.update_time.desc())
    except Exception as e:
        current_app.logger.error(e)
    pruduct_list_dict = []
    for product in product_list:
        pruduct_list_dict.append(product.to_dict())

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

    data = {
        "product_list": pruduct_list_dict,
        "category_list": category_list_dict,
    }
    return render_template('front/product.html', data=data)


@front_bp.route('/product_detail', methods=['GET'])
def product_detail():
    product_id = request.args.get('product_id')
    if not product_id:
        return render_template('front/product_detail.html', data={"errmsg": "未查询到此产品"})
    product = None
    try:
        product = Product.query.get(product_id)
    except Exception as e:
        current_app.logger.error(e)

    if not product:
        return render_template('front/product_detail.html', data={"errmsg": "未查询到此产品"})

    data = {
        'product': product.to_dict() if product else None
    }
    return render_template('front/product_detail.html', data=data)


@front_bp.route('/case', methods=['GET', 'POST'])
def case():
    case_list = []
    try:
        filters = []
        case_list = Case.query.filter(*filters).order_by(Case.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)
    case_list_dict = []
    for case in case_list:
        case_list_dict.append(case.to_dict())

    data = {
        "case_list": case_list_dict
    }
    return render_template('front/case.html', data=data)


@front_bp.route('/case_detail', methods=['GET'])
def case_detail():
    case_id = request.args.get('case_id')
    if not case_id:
        return render_template('front/case_detail.html', data={"errmsg": "未查询到此案例"})
    case = None
    try:
        case = Case.query.get(case_id)
    except Exception as e:
        current_app.logger.error(e)
    if not case:
        return render_template('front/case_detail.html', data={"errmsg": "未查询到此案例"})

    data = {
        'case': case.to_dict() if case else None
    }
    return render_template('front/case_detail.html', data=data)


@front_bp.route('/news', methods=['GET'])
def news():
    class_list = []
    filters = [NewsClass.status == 1]
    try:
        class_list = NewsClass.query.filter(*filters)
    except Exception as e:
        current_app.logger.error(e)
    news_class_dict = []
    for news_class in class_list:
        news_class_dict.append(news_class.to_dict())

    class_id = request.args.get('id')
    news_list = []
    filters = [News.status ==1]
    try:
        if class_id:
            filters.append(News.class_id == class_id)
        news_list = News.query.filter(*filters).order_by(News.create_time.desc())
    except Exception as e:
        current_app.logger.error(e)
    news_list_dict = []
    for news in news_list:
        news_list_dict.append(news.to_basic_dict())

    data = {
        "news_list": news_list_dict,
        "news_class_list":news_class_dict,
    }
    return render_template('front/news.html', data=data)


@front_bp.route('/news_detail', methods=['GET', 'POST'])
def news_detail():
    if request.method == 'GET':
        news_id = request.args.get('news_id')
        if not news_id:
            return render_template('front/news_detail.html', data={"errmsg": "未查询到此新闻"})
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)

        if not news:
            return render_template('front/news_detail.html', data={"errmsg": "新闻不存在"})

        data = {
            'news': news.to_dict() if news else None
        }

        return render_template('front/news_detail.html', data=data)


@front_bp.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('front/about.html')


@front_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    return render_template('front/contact.html')



