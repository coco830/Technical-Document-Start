from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_users():
    """获取用户列表"""
    return {"message": "获取用户列表接口待实现"}


@router.get("/{user_id}")
async def get_user(user_id: int):
    """获取用户详情"""
    return {"message": f"获取用户{user_id}详情接口待实现"}


@router.put("/{user_id}")
async def update_user(user_id: int):
    """更新用户信息"""
    return {"message": f"更新用户{user_id}信息接口待实现"}


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """删除用户"""
    return {"message": f"删除用户{user_id}接口待实现"}