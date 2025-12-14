"""
Seed Data Script
데이터베이스에 200+개의 테스트 데이터를 생성하는 스크립트
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from decimal import Decimal
import random

from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole, Gender, RefreshToken
from app.models.book import Book, BookView
from app.models.review import Review, ReviewLike, ReviewLikeCount
from app.models.comment import Comment, CommentLike
from app.models.favorite import Favorite
from app.models.cart import Cart
from app.models.order import Order, OrderItem, OrderStatus
from app.models.coupon import Coupon, UserCoupon, CouponIssuance, CouponUsageHistory, CouponType
from app.core.security import hash_password


def clear_all_data(db: Session):
    """기존 데이터 모두 삭제"""
    print("🗑️  Clearing existing data...")

    # 순서 중요 (외래키 제약조건 고려)
    db.query(CommentLike).delete()
    db.query(ReviewLike).delete()
    db.query(ReviewLikeCount).delete()
    db.query(Comment).delete()
    db.query(Review).delete()
    db.query(BookView).delete()
    db.query(Favorite).delete()
    db.query(Cart).delete()
    db.query(OrderItem).delete()
    db.query(Order).delete()
    db.query(CouponUsageHistory).delete()
    db.query(UserCoupon).delete()
    db.query(CouponIssuance).delete()
    db.query(Coupon).delete()
    db.query(Book).delete()
    db.query(RefreshToken).delete()
    db.query(User).delete()

    db.commit()
    print("✅ All data cleared")


def create_users(db: Session):
    """사용자 데이터 생성 (50명)"""
    print("\n👥 Creating users...")

    users = []

    # Admin 1명
    admin = User(
        email="admin@bookstore.com",
        password=hash_password("admin123!"),
        name="관리자",
        birth_date=datetime(1980, 1, 1).date(),
        gender=Gender.MALE,
        role=UserRole.ADMIN,
        address="서울특별시 강남구"
    )
    users.append(admin)

    # Seller 9명
    seller_names = ["김서점", "이도서", "박책방", "최북스", "정문고", "강출판", "조서적", "윤라이브", "장페이퍼"]
    for i, name in enumerate(seller_names, 1):
        seller = User(
            email=f"seller{i}@bookstore.com",
            password=hash_password(f"seller{i}123!"),
            name=name,
            birth_date=datetime(1985 + i, (i % 12) + 1, (i % 28) + 1).date(),
            gender=Gender.MALE if i % 2 == 0 else Gender.FEMALE,
            role=UserRole.SELLER,
            address=f"서울특별시 {['강남구', '서초구', '송파구', '마포구', '용산구'][i % 5]}"
        )
        users.append(seller)

    # Customer 40명
    first_names = ["민준", "서연", "지후", "하은", "도윤", "서준", "예은", "시우", "지아", "주원",
                   "수아", "하준", "다은", "건우", "지민", "우진", "채원", "현우", "소율", "준서"]
    last_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]

    for i in range(40):
        first = random.choice(first_names)
        last = random.choice(last_names)
        customer = User(
            email=f"customer{i+1}@example.com",
            password=hash_password(f"customer{i+1}123!"),
            name=f"{last}{first}",
            birth_date=datetime(1990 + (i % 20), ((i % 12) + 1), ((i % 28) + 1)).date(),
            gender=Gender.MALE if i % 2 == 0 else Gender.FEMALE,
            role=UserRole.CUSTOMER,
            address=f"서울특별시 {['강남구', '서초구', '송파구', '마포구', '용산구', '종로구', '중구', '성동구'][i % 8]}"
        )
        users.append(customer)

    db.add_all(users)
    db.commit()

    print(f"✅ Created {len(users)} users (1 Admin, 9 Sellers, 40 Customers)")
    return users


def create_books(db: Session, sellers: list[User]):
    """도서 데이터 생성 (100권)"""
    print("\n📚 Creating books...")

    books = []

    book_data = [
        # 한국 소설
        ("채식주의자", "한강", "창비", "채식을 시작한 여자의 이야기", "9788936434120", 10800),
        ("82년생 김지영", "조남주", "민음사", "대한민국 평범한 여성의 삶", "9788937473722", 13800),
        ("완득이", "김려령", "창비", "다문화 가정 소년의 성장기", "9788936456610", 11000),
        ("아몬드", "손원평", "창비", "감정을 느끼지 못하는 소년", "9788936434267", 12800),
        ("7년의 밤", "정유정", "은행나무", "댐 붕괴 사건과 복수", "9788956605814", 14000),

        # 외국 소설
        ("1984", "조지 오웰", "민음사", "디스토피아 소설의 고전", "9788937460777", 13800),
        ("위대한 개츠비", "F. 스콧 피츠제럴드", "문학동네", "미국 드림의 환상", "9788954622356", 11000),
        ("노르웨이의 숲", "무라카미 하루키", "민음사", "상실과 사랑의 이야기", "9788937461132", 14000),
        ("호밀밭의 파수꾼", "J.D. 샐린저", "민음사", "10대의 방황과 성장", "9788937460750", 12000),
        ("데미안", "헤르만 헤세", "민음사", "성장 소설의 걸작", "9788937460449", 9800),

        # 자기계발
        ("데일 카네기 인간관계론", "데일 카네기", "현대지성", "인간관계의 기술", "9791187142096", 15000),
        ("미움받을 용기", "기시미 이치로", "인플루엔셜", "아들러 심리학 입문", "9788970127248", 14900),
        ("아주 작은 습관의 힘", "제임스 클리어", "비즈니스북스", "습관 형성의 과학", "9791162540640", 16800),
        ("어떻게 살 것인가", "유시민", "생각의길", "삶에 대한 통찰", "9788965137016", 15000),
        ("멈추면 비로소 보이는 것들", "혜민", "쌤앤파커스", "마음을 치유하는 이야기", "9788965705109", 13800),

        # 역사/인문
        ("사피엔스", "유발 하라리", "김영사", "인류의 역사", "9788934972464", 22000),
        ("총 균 쇠", "재레드 다이아몬드", "문학사상", "문명의 발전사", "9788970127248", 25000),
        ("코스모스", "칼 세이건", "사이언스북스", "우주와 과학의 세계", "9788983711892", 19800),
        ("국가란 무엇인가", "유시민", "돌베개", "국가와 권력", "9788971994498", 16000),
        ("총균쇠", "재레드 다이아몬드", "문학사상", "문명 발전의 비밀", "9788970127248", 25000),
    ]

    # 기본 도서 데이터 추가
    for i, (title, author, publisher, summary, isbn, price) in enumerate(book_data):
        seller = random.choice(sellers)
        book = Book(
            seller_id=seller.id,
            title=title,
            author=author,
            publisher=publisher,
            summary=summary,
            isbn=f"{isbn}{i:02d}",
            price=Decimal(str(price)),
            publication_date=datetime(2020 + (i % 5), ((i % 12) + 1), 1).date()
        )
        books.append(book)

    # 추가 도서 80권 생성 (다양한 장르)
    genres = ["소설", "시", "수필", "경영", "경제", "IT", "과학", "역사", "철학", "예술"]
    publishers = ["민음사", "창비", "문학동네", "김영사", "위즈덤하우스", "한빛미디어", "길벗", "이지스퍼블리싱"]

    for i in range(80):
        genre = random.choice(genres)
        publisher = random.choice(publishers)
        seller = random.choice(sellers)

        book = Book(
            seller_id=seller.id,
            title=f"{genre} 도서 {i+1}: {random.choice(['이야기', '탐구', '분석', '입문', '실전', '마스터'])}",
            author=f"{random.choice(['김', '이', '박', '최'])}{random.choice(['철수', '영희', '민수', '지영'])}",
            publisher=publisher,
            summary=f"{genre} 분야의 {random.choice(['기초', '심화', '실용', '전문'])} 서적",
            isbn=f"978895{i:07d}",
            price=Decimal(str(random.randint(10000, 35000))),
            publication_date=datetime(2018 + (i % 7), ((i % 12) + 1), ((i % 28) + 1)).date()
        )
        books.append(book)

    db.add_all(books)
    db.commit()

    print(f"✅ Created {len(books)} books")
    return books


def create_coupons(db: Session):
    """쿠폰 데이터 생성 (10개 - UNIVERSAL 4개, PERSONAL 6개)"""
    print("\n🎫 Creating coupons...")

    coupons = []
    now = datetime.utcnow()

    # (이름, 할인율, 시작일, 종료일, 타입)
    coupon_data = [
        ("신규회원10", 10.0, now, now + timedelta(days=365), CouponType.UNIVERSAL),
        ("봄맞이15", 15.0, now - timedelta(days=30), now + timedelta(days=60), CouponType.UNIVERSAL),
        ("여름특가20", 20.0, now, now + timedelta(days=90), CouponType.UNIVERSAL),
        ("가을독서", 12.0, now - timedelta(days=10), now + timedelta(days=80), CouponType.PERSONAL),
        ("겨울할인", 18.0, now, now + timedelta(days=120), CouponType.UNIVERSAL),
        ("주말특가", 10.0, now - timedelta(days=5), now + timedelta(days=30), CouponType.PERSONAL),
        ("VIP25", 25.0, now, now + timedelta(days=180), CouponType.PERSONAL),
        ("월말정산", 15.0, now - timedelta(days=15), now + timedelta(days=45), CouponType.PERSONAL),
        ("책사랑", 13.0, now, now + timedelta(days=150), CouponType.PERSONAL),
        ("첫구매", 20.0, now, now + timedelta(days=365), CouponType.PERSONAL),
    ]

    for name, rate, start, end, coupon_type in coupon_data:
        coupon = Coupon(
            name=name,
            description=f"{name} 쿠폰 - {int(rate)}% 할인",
            discount_rate=Decimal(str(rate)),
            coupon_type=coupon_type,
            start_at=start,
            end_at=end,
            is_active=True
        )
        coupons.append(coupon)

    db.add_all(coupons)
    db.commit()

    print(f"✅ Created {len(coupons)} coupons (UNIVERSAL: 4, PERSONAL: 6)")
    return coupons


def create_user_coupons(db: Session, customers: list[User], coupons: list[Coupon]):
    """사용자 쿠폰 발급 데이터 생성 (PERSONAL 쿠폰만, 30개)"""
    print("\n🎁 Creating user coupon issuances...")

    issuances = []
    personal_coupons = [c for c in coupons if c.coupon_type == CouponType.PERSONAL]

    # 각 고객에게 랜덤으로 PERSONAL 쿠폰 발급
    for customer in random.sample(customers, min(30, len(customers))):
        coupon = random.choice(personal_coupons)

        # 중복 발급 방지
        existing = db.query(CouponIssuance).filter(
            CouponIssuance.user_id == customer.id,
            CouponIssuance.coupon_id == coupon.id
        ).first()

        if not existing:
            issuance = CouponIssuance(
                user_id=customer.id,
                coupon_id=coupon.id
            )
            issuances.append(issuance)

    db.add_all(issuances)
    db.commit()

    print(f"✅ Created {len(issuances)} coupon issuances (PERSONAL only)")
    return issuances


def create_orders(db: Session, customers: list[User], books: list[Book]):
    """주문 데이터 생성 (50개)"""
    print("\n🛒 Creating orders...")

    orders = []
    order_items = []

    for i in range(50):
        customer = random.choice(customers)
        status = random.choice(list(OrderStatus))

        # 주문 아이템 먼저 계산
        num_items = random.randint(1, 4)
        selected_books = random.sample(books, num_items)
        total = 0

        for book in selected_books:
            quantity = random.randint(1, 3)
            total += int(book.price * quantity)

        # 주문 생성
        order = Order(
            user_id=customer.id,
            status=status,
            total_price=Decimal(str(total)),
            discount_amount=Decimal('0'),
            final_price=Decimal(str(total)),
            shipping_address=f"서울시 {random.choice(['강남구', '서초구', '송파구', '마포구', '용산구'])} {random.randint(1, 500)}",
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 90))
        )
        db.add(order)
        db.flush()  # order.id 얻기

        # 주문 아이템 추가
        for book in selected_books:
            quantity = random.randint(1, 3)
            order_item = OrderItem(
                order_id=order.id,
                book_id=book.id,
                quantity=quantity,
                price_at_purchase=book.price
            )
            order_items.append(order_item)

        orders.append(order)

    db.add_all(order_items)
    db.commit()

    print(f"✅ Created {len(orders)} orders with {len(order_items)} items")
    return orders


def create_admin_order(db: Session, admin: User, books: list[Book]):
    """Admin 테스트용 DELIVERED 주문 생성"""
    print("\n📦 Creating admin test order (DELIVERED)...")

    # 1번, 2번 책을 각 1권씩 추가
    book_quantities = [
        (books[0], 1),  # 1번 책 1권
        (books[1], 1),  # 2번 책 1권
    ]

    # Total 계산
    total = sum(int(book.price * qty) for book, qty in book_quantities)

    # DELIVERED 주문 생성
    order = Order(
        user_id=admin.id,
        status=OrderStatus.DELIVERED,
        total_price=Decimal(str(total)),
        discount_amount=Decimal('0'),
        final_price=Decimal(str(total)),
        shipping_address="서울시 강남구 테헤란로 123 (Admin 테스트 주소)",
        created_at=datetime.utcnow() - timedelta(days=7)  # 7일 전 주문
    )
    db.add(order)
    db.flush()  # order.id 얻기

    # 주문 아이템 추가
    order_items = []
    for book, quantity in book_quantities:
        order_item = OrderItem(
            order_id=order.id,
            book_id=book.id,
            quantity=quantity,
            price_at_purchase=book.price
        )
        order_items.append(order_item)

    db.add_all(order_items)
    db.commit()

    print(f"✅ Created admin test order (ID: {order.id}, Status: DELIVERED, Items: {len(order_items)})")
    return order


def create_reviews(db: Session, customers: list[User], books: list[Book], orders: list[Order]):
    """리뷰 데이터 생성 (80개)"""
    print("\n⭐ Creating reviews...")

    reviews = []
    review_counts = []

    # 배송 완료된 주문에서 랜덤하게 리뷰 작성
    delivered_orders = [o for o in orders if o.status == OrderStatus.DELIVERED]

    if not delivered_orders:
        print("⚠️  No delivered orders found, skipping reviews")
        return reviews

    for order in delivered_orders[:min(80, len(delivered_orders))]:
        # 주문의 첫 번째 아이템에 대해 리뷰 작성
        if not order.items:
            continue

        first_item = order.items[0]
        rating = random.choice([3, 4, 4, 5, 5, 5])  # 높은 평점 비율 높게

        review_texts = [
            "정말 재미있게 읽었습니다. 추천합니다!",
            "기대 이상이었어요. 좋은 책입니다.",
            "내용이 알차고 유익했습니다.",
            "배송도 빠르고 책 상태도 좋았어요.",
            "다시 읽어보고 싶은 책입니다.",
            "생각보다 별로였어요.",
            "가격 대비 좋은 것 같아요.",
            "시간 가는 줄 모르고 읽었습니다.",
        ]

        review = Review(
            user_id=order.user_id,
            book_id=first_item.book_id,
            order_id=order.id,
            rating=rating,
            comment=random.choice(review_texts),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60))
        )
        db.add(review)
        db.flush()

        # 리뷰 좋아요 카운트 초기화
        count = ReviewLikeCount(
            review_id=review.id,
            like_count=0
        )
        review_counts.append(count)
        reviews.append(review)

    db.add_all(review_counts)
    db.commit()

    print(f"✅ Created {len(reviews)} reviews")
    return reviews


def create_review_likes(db: Session, customers: list[User], reviews: list[Review]):
    """리뷰 좋아요 데이터 생성 (100개)"""
    print("\n👍 Creating review likes...")

    likes = []
    like_counts = {}
    attempted = 0
    max_attempts = 200

    while len(likes) < 100 and attempted < max_attempts:
        customer = random.choice(customers)
        review = random.choice(reviews)
        attempted += 1

        # 중복 방지 (메모리에서 확인)
        like_key = (customer.id, review.id)
        if like_key in {(l.user_id, l.review_id) for l in likes}:
            continue

        like = ReviewLike(
            user_id=customer.id,
            review_id=review.id
        )
        likes.append(like)

        # 카운트 업데이트
        like_counts[review.id] = like_counts.get(review.id, 0) + 1

    db.add_all(likes)

    # 좋아요 카운트 업데이트
    for review_id, count in like_counts.items():
        db.query(ReviewLikeCount).filter(
            ReviewLikeCount.review_id == review_id
        ).update({"like_count": count})

    db.commit()

    print(f"✅ Created {len(likes)} review likes")
    return likes


def create_comments(db: Session, customers: list[User], reviews: list[Review]):
    """댓글 데이터 생성 (60개)"""
    print("\n💬 Creating comments...")

    comments = []

    comment_texts = [
        "저도 이 책 읽어봤는데 정말 좋더라구요!",
        "좋은 리뷰 감사합니다.",
        "다음에 한번 읽어봐야겠네요.",
        "공감합니다!",
        "추천 감사합니다.",
        "이 부분이 특히 인상 깊었어요.",
        "좋은 정보 감사합니다.",
    ]

    for _ in range(60):
        customer = random.choice(customers)
        review = random.choice(reviews)

        comment = Comment(
            review_id=review.id,
            user_id=customer.id,
            content=random.choice(comment_texts),
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 50))
        )
        comments.append(comment)

    db.add_all(comments)
    db.commit()

    print(f"✅ Created {len(comments)} comments")
    return comments


def create_favorites(db: Session, customers: list[User], books: list[Book]):
    """위시리스트 데이터 생성 (40개)"""
    print("\n❤️  Creating favorites...")

    favorites = []

    for _ in range(40):
        customer = random.choice(customers)
        book = random.choice(books)

        # 중복 방지
        if db.query(Favorite).filter(
            Favorite.user_id == customer.id,
            Favorite.book_id == book.id,
            Favorite.deleted_at.is_(None)
        ).first():
            continue

        favorite = Favorite(
            user_id=customer.id,
            book_id=book.id
        )
        favorites.append(favorite)

    db.add_all(favorites)
    db.commit()

    print(f"✅ Created {len(favorites)} favorites")
    return favorites


def create_carts(db: Session, customers: list[User], books: list[Book]):
    """장바구니 데이터 생성 (30개)"""
    print("\n🛍️  Creating cart items...")

    carts = []

    for _ in range(30):
        customer = random.choice(customers)
        book = random.choice(books)

        # 중복 방지
        if db.query(Cart).filter(
            Cart.user_id == customer.id,
            Cart.book_id == book.id,
            Cart.deleted_at.is_(None)
        ).first():
            continue

        cart = Cart(
            user_id=customer.id,
            book_id=book.id,
            quantity=random.randint(1, 5)
        )
        carts.append(cart)

    db.add_all(carts)
    db.commit()

    print(f"✅ Created {len(carts)} cart items")
    return carts


def main():
    """메인 실행 함수"""
    print("=" * 60)
    print("📊 Bookstore Database Seed Script")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 기존 데이터 삭제
        clear_all_data(db)

        # 데이터 생성
        users = create_users(db)
        admin = [u for u in users if u.role == UserRole.ADMIN][0]
        sellers = [u for u in users if u.role == UserRole.SELLER]
        customers = [u for u in users if u.role == UserRole.CUSTOMER]

        books = create_books(db, sellers)
        coupons = create_coupons(db)
        user_coupons = create_user_coupons(db, customers, coupons)
        orders = create_orders(db, customers, books)

        # Admin 테스트용 DELIVERED 주문 추가
        admin_order = create_admin_order(db, admin, books)
        if admin_order:
            orders.append(admin_order)
        reviews = create_reviews(db, customers, books, orders)
        review_likes = create_review_likes(db, customers, reviews)
        comments = create_comments(db, customers, reviews)
        favorites = create_favorites(db, customers, books)
        carts = create_carts(db, customers, books)

        # 총 개수 계산
        total = (
            len(users) + len(books) + len(coupons) + len(user_coupons) +
            len(orders) + len(reviews) + len(review_likes) +
            len(comments) + len(favorites) + len(carts)
        )

        print("\n" + "=" * 60)
        print("✨ Seed Data Creation Summary")
        print("=" * 60)
        print(f"Users: {len(users)}")
        print(f"Books: {len(books)}")
        print(f"Coupons: {len(coupons)}")
        print(f"User Coupons: {len(user_coupons)}")
        print(f"Orders: {len(orders)}")
        print(f"Reviews: {len(reviews)}")
        print(f"Review Likes: {len(review_likes)}")
        print(f"Comments: {len(comments)}")
        print(f"Favorites: {len(favorites)}")
        print(f"Cart Items: {len(carts)}")
        print("-" * 60)
        print(f"📊 Total Records: {total}")
        print("=" * 60)
        print("✅ Seed data created successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
