from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.categories import Category as CategoryModel
from app.schemas import Category as CategorySchema, CategoryCreate
from app.db_depends import get_db

from sqlalchemy.ext.asyncio import AsyncSession
from app.db_depends import get_async_db

# Создаём маршрутизатор с префиксом и тегом
router = APIRouter(
    prefix="/categories",
    tags=["category"],
)


@router.get("/", response_model=list[CategorySchema])
async def get_all_categories(db: AsyncSession = Depends(get_async_db)):
    """
    Возвращает список всех активных категорий.
    """
    result = await db.scalars(select(CategoryModel).where(CategoryModel.is_active == True))
    categories = result.all()
    return categories


@router.post("/", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_async_db)):
    """
    Создаёт новую категорию.
    """
    # Проверка существования parent_id, если указан
    if category.parent_id is not None:
        stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id)
        result = await db.scalars(stmt)
        parent = result.first()
        if parent is None:
            raise HTTPException(status_code=400, detail="Parent category not found")

    # Создание новой категории
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    return db_category


@router.put("/{category_id}", response_model=CategorySchema)
async def update_category(category_id: int, category: CategoryCreate,
                          db: AsyncSession = Depends(get_async_db)):
    """
    Обновляет категорию по её ID.
    """
    # Проверяем существование категории
    stmt = select(CategoryModel).where(CategoryModel.id == category_id)
    result = await db.scalars(stmt)
    db_category = result.first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Проверяем parent_id, если указан
    if category.parent_id is not None:
        parent_stmt = select(CategoryModel).where(CategoryModel.id == category.parent_id)
        parent_result = await db.scalars(parent_stmt)
        parent = parent_result.first()
        if not parent:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Parent category not found")
        if parent.id == category_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Category cannot be its own parent")

    # Обновляем категорию
    update_data = category.model_dump(exclude_unset=True)
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**update_data)
    )
    await db.commit()
    return db_category


@router.delete("/{category_id}", response_model=CategorySchema)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)):
    """
    Выполняет мягкое удаление категории по её ID, устанавливая is_active = False.
    """
    stmt = select(CategoryModel).where(CategoryModel.id == category_id)
    result = await db.scalars(stmt)
    db_category = result.first()
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(is_active=False)
    )
    await db.commit()
    return db_category
