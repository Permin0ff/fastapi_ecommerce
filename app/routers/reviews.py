from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db_depends import get_async_db
from app.models.products import Product
from app.models.reviews import Review
from app.models.users import User
from app.schemas import Review as ReviewSchema, ReviewCreate

router = APIRouter(tags=["reviews"])
review_oauth2 = OAuth2PasswordBearer(
    tokenUrl="users/token", auto_error=False, scheme_name="ReviewBearer"
)


async def get_review_user(
    token: str | None = Depends(review_oauth2),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    if not token:
        raise HTTPException(403, "Authentication required")
    try:
        return await get_current_user(token=token, db=db)
    except HTTPException as exc:
        if exc.status_code != 401:
            raise
        raise HTTPException(403, "Could not validate credentials") from exc


async def get_review_buyer(user: User = Depends(get_review_user)) -> User:
    if user.role != "buyer":
        raise HTTPException(403, "Only buyers can create reviews")
    return user


async def update_product_rating(db: AsyncSession, product: Product) -> None:
    average = await db.scalar(
        select(func.avg(Review.grade)).where(
            Review.product_id == product.id, Review.is_active.is_(True)
        )
    )
    product.rating = float(average) if average is not None else 0.0


@router.get("/reviews", response_model=list[ReviewSchema])
async def get_reviews(db: AsyncSession = Depends(get_async_db)) -> list[Review]:
    result = await db.scalars(select(Review).where(Review.is_active.is_(True)).order_by(Review.id))
    return list(result.all())


@router.get("/products/{product_id}/reviews", response_model=list[ReviewSchema])
async def get_product_reviews(product_id: int, db: AsyncSession = Depends(get_async_db)) -> list[Review]:
    product = await db.scalar(select(Product).where(Product.id == product_id, Product.is_active.is_(True)))
    if product is None:
        raise HTTPException(404, "Product not found or inactive")
    result = await db.scalars(
        select(Review).where(Review.product_id == product_id, Review.is_active.is_(True)).order_by(Review.id)
    )
    return list(result.all())


@router.post("/reviews", response_model=ReviewSchema, status_code=201)
async def create_review(
    review: ReviewCreate,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_review_buyer),
) -> Review:
    product = await db.scalar(
        select(Product).where(Product.id == review.product_id, Product.is_active.is_(True)).with_for_update()
    )
    if product is None:
        raise HTTPException(400, "Product not found or inactive")
    db_review = Review(**review.model_dump(), user_id=user.id)
    db.add(db_review)
    await update_product_rating(db, product)
    await db.commit()
    return db_review


@router.delete("/reviews/{review_id}", response_model=dict[str, str])
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_async_db),
    user: User = Depends(get_review_user),
) -> dict[str, str]:
    product_id = await db.scalar(select(Review.product_id).where(Review.id == review_id))
    if product_id is None:
        raise HTTPException(404, "Review not found or inactive")
    product = await db.scalar(select(Product).where(Product.id == product_id).with_for_update())
    review = await db.scalar(
        select(Review).where(Review.id == review_id, Review.is_active.is_(True)).with_for_update()
    )
    if review is None:
        raise HTTPException(404, "Review not found or inactive")
    if review.user_id != user.id and user.role != "admin":
        raise HTTPException(403, "Only the author or an admin can delete this review")
    review.is_active = False
    await update_product_rating(db, product)
    await db.commit()
    return {"message": "Review deleted"}
