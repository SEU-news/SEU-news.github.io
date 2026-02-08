# utils.py
import uuid
from flask import session, request

# utils.py
import uuid
import logging
from flask import session, request

# Session中存储上下文的键名
CONTEXT_KEY = 'main_page_context'
# 与你现有代码一致的合法page_size值
LEGAL_PAGE_SIZES = [10, 20, 50, 100]
# 合法的排序字段（与你现有代码一致）
ALLOWED_SORT_FIELDS = ['created_at', 'updated_at']
# 合法的排序顺序
ALLOWED_SORT_ORDERS = ['asc', 'desc']

def save_main_page_context():
    """
    保存主页面的所有分页、筛选、排序参数到加密Session，返回唯一上下文ID
    完全适配现有MainView的参数验证逻辑
    """
    # 1. 获取所有前端参数（与MainView一致）
    # 排序参数
    sort_field = request.args.get('sort_field', 'created_at')
    sort_order = request.args.get('sort_order', 'desc')
    # 搜索参数
    query = request.args.get('q', '').strip()
    # 分页参数
    page = request.args.get('page', 1, type=int)  # Flask原生支持type参数，无需额外int转换
    page_size = request.args.get('page_size', 10)

    # 2. 严格遵循你的参数验证逻辑（核心修正点）
    # 排序参数验证（与MainView一致）
    sort_field = sort_field if sort_field in ALLOWED_SORT_FIELDS else 'created_at'
    sort_order = sort_order if sort_order in ALLOWED_SORT_ORDERS else 'desc'

    # Page参数验证：确保是正整数，默认1
    try:
        page = int(page)
        page = page if page >= 1 else 1
    except (ValueError, TypeError):
        page = 1
        logging.warning(f"非法page参数，使用默认值1")

    # Page_size参数验证：必须是LEGAL_PAGE_SIZES中的值，否则默认10（与MainView完全一致）
    try:
        page_size = int(page_size)
        if page_size not in LEGAL_PAGE_SIZES:
            raise ValueError(f"非法page_size: {page_size}")
    except (ValueError, TypeError) as e:
        page_size = 10
        logging.warning(f"用户请求了非法page_size，使用默认值10。错误信息: {e}")

    # 3. 生成唯一上下文ID（避免多页面参数冲突）
    context_id = str(uuid.uuid4())

    # 4. 存储到加密Session中（包含所有需要的参数）
    if CONTEXT_KEY not in session:
        session[CONTEXT_KEY] = {}
    session[CONTEXT_KEY][context_id] = {
        'page': page,
        'page_size': page_size,
        'q': query,
        'sort_field': sort_field,
        'sort_order': sort_order
    }

    return context_id

def get_main_page_context(context_id):
    """
    根据上下文ID获取参数，获取后立即删除（用完即删，提升安全性）
    返回的参数完全匹配MainView的需求
    """
    # 默认参数（与MainView的默认值一致）
    default_params = {
        'page': 1,
        'page_size': 10,
        'q': '',
        'sort_field': 'created_at',
        'sort_order': 'desc'
    }

    # 校验上下文ID是否有效
    if not context_id or CONTEXT_KEY not in session or context_id not in session[CONTEXT_KEY]:
        return default_params

    # 取出参数并删除（防止重复使用）
    page_params = session[CONTEXT_KEY].pop(context_id)
    # 如果上下文为空，删除键，减少Session体积
    if not session[CONTEXT_KEY]:
        session.pop(CONTEXT_KEY)

    # 二次验证：确保从Session中取出的参数依然合法（防止极端情况的篡改，双重保障）
    page_params['sort_field'] = page_params['sort_field'] if page_params['sort_field'] in ALLOWED_SORT_FIELDS else 'created_at'
    page_params['sort_order'] = page_params['sort_order'] if page_params['sort_order'] in ALLOWED_SORT_ORDERS else 'desc'
    page_params['page_size'] = page_params['page_size'] if page_params['page_size'] in LEGAL_PAGE_SIZES else 10
    page_params['page'] = page_params['page'] if page_params['page'] >= 1 else 1

    return page_params