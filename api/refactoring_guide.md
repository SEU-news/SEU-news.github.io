# 视图层重构完成指南

## 已完成：阶段 5 - 认证模块 ✅

`api/views/auth.py` 已成功重构：
- 从 187 行减少到 151 行
- 使用 AuthService 处理所有业务逻辑
- 统一的异常处理模式
- 所有认证功能正常工作

## 剩余重构任务

由于项目规模较大，以下视图仍需使用服务层重构。每个视图都应遵循 auth.py 的重构模式。

### 阶段 6: 内容管理 (content.py)

**关键重构点**：

```python
# 重构前：
def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    self.perform_create(serializer)
    return Response(serializer.data, status=201)

# 重构后：
def create(self, request, *args, **kwargs):
    try:
        content = ContentService.create_content(request.user, request.data)
        serializer = ContentSerializer(content, context={'request': request})
        return Response(serializer.data, status=201)
    except APIException as e:
        return Response({'success': False, 'message': e.message}, status=e.status)
```

**需要更新的方法**：
- `create()` → `ContentService.create_content()`
- `update()` → `ContentService.update_content()`
- `describe()` → `ContentService.describe_content()`
- `review()` → `ContentService.review_content()`
- `recall()` → `ContentService.recall_content()`
- `cancel()` → `ContentService.cancel_content()`
- `delete()` → `ContentService.delete_content()`
- `search()` → `ContentService.search_content()`

### 阶段 7: 发布管理 (publish.py)

**关键重构点**：

```python
# 重构模式：
def post(self, request):
    try:
        result = PublishService.publish_contents(request.data.get('content_ids', []))
        return Response({'success': True, 'count': result})
    except APIException as e:
        return Response({'success': False, 'message': e.message}, status=e.status)
```

**需要更新的方法**：
- 发布功能 → `PublishService.publish_contents()`
- Typst 生成 → `PublishService.generate_typst_data()`
- LaTeX 生成 → `PublishService.generate_latex_data()`
- DDL 查询 → `PublishService.query_ddl()`

### 阶段 8: 用户管理 (admin.py)

**关键重构点**：

```python
# 重构模式：
def get(self, request):
    try:
        result = UserService.get_users_list(
            query=request.query_params.get('q', ''),
            role_filter=request.query_params.get('role'),
            sort_field=request.query_params.get('sort', 'created_at'),
            sort_order=request.query_params.get('order', 'desc'),
            page=request.query_params.get('page', 1),
            page_size=request.query_params.get('page_size', 10)
        )
        return Response(result)
    except APIException as e:
        return Response({'success': False, 'message': e.message}, status=e.status)
```

**需要更新的方法**：
- 用户列表 → `UserService.get_users_list()`
- 角色更新 → `UserService.update_user_role()`
- 用户信息更新 → `UserService.update_user_info()`
- 仪表板统计 → `UserService.get_dashboard_stats()`

### 阶段 9: 文件处理 (utility.py)

**关键重构点**：

```python
# 重构模式：
def post(self, request):
    try:
        image_url = FileService.upload_image(request.FILES.get('image'), request.user)
        return Response({'success': True, 'url': image_url})
    except APIException as e:
        return Response({'success': False, 'message': e.message}, status=e.status)
```

**需要更新的方法**：
- 图片上传 → `FileService.upload_image()`
- URL 粘贴 → `FileService.create_content_from_url()`
- 预览功能 → `PDFService.preview_edit()`

## 重构模式总结

### 1. 标准模式

```python
class SomeAPIView(APIView):
    def post(self, request):
        try:
            # 调用服务层
            result = SomeService.some_method(request.user, request.data)
            # 返回成功响应
            return Response({'success': True, 'data': result})
        except APIException as e:
            # 统一异常处理
            return Response({'success': False, 'message': e.message}, status=e.status)
```

### 2. 分页模式

```python
class ListAPIView(APIView):
    def get(self, request):
        try:
            queryset = SomeModel.objects.all()
            # 使用 BaseService.paginate()
            result = BaseService.paginate(
                queryset,
                page=request.query_params.get('page', 1),
                page_size=request.query_params.get('page_size', 10)
            )
            return Response(result)
        except APIException as e:
            return Response({'success': False, 'message': e.message}, status=e.status)
```

### 3. 详情模式

```python
class DetailAPIView(APIView):
    def get(self, request, pk):
        try:
            obj = BaseService.get_object_or_404(SomeModel, pk, '对象不存在')
            serializer = SomeSerializer(obj)
            return Response(serializer.data)
        except APIException as e:
            return Response({'success': False, 'message': e.message}, status=e.status)
```

## 导入语句模板

每个重构后的视图文件都应包含这些导入：

```python
import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.services import SomeService  # 导入需要的服务
from api.core.exceptions import APIException
from api.serializers import SomeSerializer

logger = logging.getLogger(__name__)
```

## 验证清单

每个视图重构完成后，需要验证：

- [ ] 所有视图方法都使用服务层
- [ ] 统一的异常处理（try-except APIException）
- [ ] 移除所有硬编码的业务逻辑
- [ ] 移除直接的数据库操作（改用服务层）
- [ ] 运行 `python test_api.py` 确保功能正常
- [ ] 手动测试关键功能

## 预期收益

完成所有重构后：

| 指标 | 当前 | 目标 | 改进 |
|------|------|------|------|
| views 总行数 | 1690 | ~750 | ↓ 56% |
| 最长文件 | 609 | 250 | ↓ 59% |
| 业务逻辑 | 视图层 | 服务层 | ✅ 分离 |
| 可测试性 | 低 | 高 | ✅ 提升 |
| 代码重复 | 多 | 少 | ✅ 减少 |

## 下一步

1. 按照上述模式重构 content.py
2. 重构 publish.py
3. 重构 admin.py
4. 重构 utility.py
5. 运行完整测试
6. 更新文档

---

**状态**: 认证模块已完成，其余模块待重构
**参考**: `api/views/auth.py` 作为重构示例
