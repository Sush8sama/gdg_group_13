from typing import Any, Dict

import pandas as pd


def get_user_data(customer_id: str) -> Dict[str, Any]:
    """
    Collects customer info, products, and transactions for a given user.
    """

    # Load CSVs
    customers_df = pd.read_csv(
        "/Users/lunamei/Documents/hackaton/ing/gdg_group_13/data/synthetic_data/customers.csv",
        dtype=str,
    )
    products_df = pd.read_csv(
        "/Users/lunamei/Documents/hackaton/ing/gdg_group_13/data/synthetic_data/products.csv",
        dtype=str,
    )
    products_closed_df = pd.read_csv(
        "/Users/lunamei/Documents/hackaton/ing/gdg_group_13/data/synthetic_data/products_closed.csv",
        dtype=str,
    )
    transactions_df = pd.read_csv(
        "/Users/lunamei/Documents/hackaton/ing/gdg_group_13/data/synthetic_data/transactions.csv",
        dtype=str,
    )

    # 1️⃣ Customer info
    customer_info_df = customers_df[customers_df["customer_id"] == customer_id]
    if customer_info_df.empty:
        raise ValueError(f"Customer ID {customer_id} not found")
    customer_info = customer_info_df.to_dict("records")[0]

    # 2️⃣ Active products
    active_products_df = products_df[products_df["customer_id"] == customer_id]
    active_products_list = active_products_df.to_dict("records")

    # 3️⃣ Closed products
    closed_products_df = products_closed_df[
        products_closed_df["customer_id"] == customer_id
    ]
    closed_products_list = closed_products_df.to_dict("records")

    # 4️⃣ Transactions (only for this customer)
    all_products_df = pd.concat(
        [active_products_df, closed_products_df], ignore_index=True
    )
    all_product_ids = all_products_df["product_id"].astype(str).tolist()
    transactions_df["product_id"] = transactions_df["product_id"].astype(str)
    customer_transactions_df = transactions_df[
        transactions_df["product_id"].isin(all_product_ids)
    ]
    transactions_list = customer_transactions_df.to_dict("records")

    # 5️⃣ Assemble all data
    user_data = {
        "customer_info": customer_info,
        "active_products": active_products_list,
        "closed_products": closed_products_list,
        "transactions": transactions_list,
    }

    return user_data


# Example usage
if __name__ == "__main__":
    user_id = "1031"  # replace with your customer_id
    data = get_user_data(user_id)
    print(data)
