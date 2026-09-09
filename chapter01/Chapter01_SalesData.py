import pandas as pd
import os
import matplotlib.pyplot as plt


# ============================================================
# 0. 기본 설정
# ============================================================

DATA_DIR = r"C:\llm_data_analysis\chapter01\01_Chapter01_RawData"

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 1. Raw Data 불러오기
# ============================================================

products = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
order_items = pd.read_csv(os.path.join(DATA_DIR, "order_items.csv"))
orders = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))


print("=" * 60)
print("RAW DATA LOAD")
print("=" * 60)

print(f"products     : {products.shape}")
print(f"customers    : {customers.shape}")
print(f"order_items  : {order_items.shape}")
print(f"orders       : {orders.shape}")


# ============================================================
# 2. 데이터 기본 정보 확인
# ============================================================

print("\n" + "=" * 60)
print("DATA INFORMATION")
print("=" * 60)

for name, df in {
    "products": products,
    "customers": customers,
    "order_items": order_items,
    "orders": orders
}.items():

    print(f"\n[{name}]")
    print(df.info())
    print("\n결측치")
    print(df.isnull().sum())

    print("\n중복 데이터:", df.duplicated().sum())


# ============================================================
# 3. 날짜 데이터 타입 변환
# ============================================================

customers["signup_date"] = pd.to_datetime(customers["signup_date"])
orders["order_date"] = pd.to_datetime(orders["order_date"])


# ============================================================
# 4. 주문 데이터 JOIN
# ============================================================

# orders + customers
df = orders.merge(
    customers,
    on="customer_id",
    how="left"
)

# order_items 추가
df = df.merge(
    order_items,
    on="order_id",
    how="left"
)

# products 추가
df = df.merge(
    products,
    on="product_id",
    how="left",
    suffixes=("_order", "_product")
)


print("\n" + "=" * 60)
print("MERGED DATA")
print("=" * 60)

print("최종 데이터 크기:", df.shape)
print("\n컬럼")
print(df.columns.tolist())


# ============================================================
# 5. 매출액 계산
# ============================================================

df["sales"] = df["quantity"] * df["unit_price"]


# ============================================================
# 6. 완료된 주문만 분석
# ============================================================

completed_df = df[
    df["order_status"] == "completed"
].copy()


print("\n" + "=" * 60)
print("COMPLETED ORDER ANALYSIS")
print("=" * 60)

print("전체 주문 건수:", orders.shape[0])
print("완료 주문 건수:", completed_df["order_id"].nunique())

print(
    "총 매출액:",
    f"{completed_df['sales'].sum():,.0f}원"
)

print(
    "평균 주문 금액:",
    f"{completed_df.groupby('order_id')['sales'].sum().mean():,.0f}원"
)


# ============================================================
# 7. 카테고리별 매출 분석
# ============================================================

category_sales = (
    completed_df
    .groupby("category")["sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n" + "=" * 60)
print("CATEGORY SALES")
print("=" * 60)

print(category_sales)


# ============================================================
# 8. 상품별 매출 TOP 10
# ============================================================

product_sales = (
    completed_df
    .groupby(
        ["product_id", "product_name"]
    )["sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n" + "=" * 60)
print("TOP 10 PRODUCTS")
print("=" * 60)

print(product_sales)


# ============================================================
# 9. 고객별 구매금액 TOP 10
# ============================================================

customer_sales = (
    completed_df
    .groupby(
        ["customer_id", "name"]
    )["sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n" + "=" * 60)
print("TOP 10 CUSTOMERS")
print("=" * 60)

print(customer_sales)


# ============================================================
# 10. 성별 매출 분석
# ============================================================

gender_sales = (
    completed_df
    .groupby("gender")["sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n" + "=" * 60)
print("GENDER SALES")
print("=" * 60)

print(gender_sales)


# ============================================================
# 11. 도시별 매출 분석
# ============================================================

city_sales = (
    completed_df
    .groupby("city")["sales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n" + "=" * 60)
print("CITY SALES")
print("=" * 60)

print(city_sales)


# ============================================================
# 12. 월별 매출 분석
# ============================================================

completed_df["order_month"] = (
    completed_df["order_date"]
    .dt.to_period("M")
    .astype(str)
)

monthly_sales = (
    completed_df
    .groupby("order_month")["sales"]
    .sum()
)

print("\n" + "=" * 60)
print("MONTHLY SALES")
print("=" * 60)

print(monthly_sales)


# ============================================================
# 13. 결제수단별 주문 분석
# ============================================================

payment_analysis = (
    completed_df
    .groupby("payment_method")
    .agg(
        order_count=("order_id", "nunique"),
        sales=("sales", "sum")
    )
    .sort_values("sales", ascending=False)
)

print("\n" + "=" * 60)
print("PAYMENT METHOD ANALYSIS")
print("=" * 60)

print(payment_analysis)


# ============================================================
# 14. 데이터 시각화
# ============================================================

# ------------------------------------------------------------
# 14-1. 카테고리별 매출
# ------------------------------------------------------------

plt.figure(figsize=(8, 5))

category_sales.plot(kind="bar")

plt.title("카테고리별 매출")
plt.xlabel("카테고리")
plt.ylabel("매출액")
plt.xticks(rotation=0)

plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 14-2. 월별 매출
# ------------------------------------------------------------

plt.figure(figsize=(12, 5))

monthly_sales.plot(kind="line", marker="o")

plt.title("월별 매출 추이")
plt.xlabel("월")
plt.ylabel("매출액")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 14-3. TOP 10 상품
# ------------------------------------------------------------

plt.figure(figsize=(10, 6))

product_sales.sort_values().plot(kind="barh")

plt.title("매출 TOP 10 상품")
plt.xlabel("매출액")
plt.ylabel("상품")

plt.tight_layout()
plt.show()


# ------------------------------------------------------------
# 14-4. 도시별 매출
# ------------------------------------------------------------

plt.figure(figsize=(10, 5))

city_sales.plot(kind="bar")

plt.title("도시별 매출")
plt.xlabel("도시")
plt.ylabel("매출액")
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()


# ============================================================
# 15. 분석 결과 CSV 저장
# ============================================================

RESULT_DIR = os.path.join(DATA_DIR, "analysis_result")

os.makedirs(RESULT_DIR, exist_ok=True)

category_sales.to_csv(
    os.path.join(RESULT_DIR, "category_sales.csv"),
    encoding="utf-8-sig"
)

product_sales.to_csv(
    os.path.join(RESULT_DIR, "top10_products.csv"),
    encoding="utf-8-sig"
)

customer_sales.to_csv(
    os.path.join(RESULT_DIR, "top10_customers.csv"),
    encoding="utf-8-sig"
)

city_sales.to_csv(
    os.path.join(RESULT_DIR, "city_sales.csv"),
    encoding="utf-8-sig"
)

monthly_sales.to_csv(
    os.path.join(RESULT_DIR, "monthly_sales.csv"),
    encoding="utf-8-sig"
)

payment_analysis.to_csv(
    os.path.join(RESULT_DIR, "payment_analysis.csv"),
    encoding="utf-8-sig"
)

# JOIN된 전체 분석 데이터 저장
completed_df.to_csv(
    os.path.join(RESULT_DIR, "completed_order_analysis.csv"),
    index=False,
    encoding="utf-8-sig"
)


print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)

print("분석 결과 저장 위치:")
print(RESULT_DIR)


from pathlib import Path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

DATA_DIR = Path('C:\llm_data_analysis\chapter01\01_Chapter01_RawData')
sns.set_theme(style='whitegrid')