import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام الوسيطة المطور", layout="wide")

# --- دالة التحقق من كلمة السر ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if not st.session_state.password_correct:
        st.sidebar.title("🔐 قفل النظام")
        pwd = st.sidebar.text_input("أدخل كلمة السر للدخول:", type="password")
        if st.sidebar.button("دخول"):
            if pwd == "1414":  # كلمة السر التي طلبتها
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.sidebar.error("كلمة السر خاطئة!")
        return False
    return True

# --- التحقق قبل تشغيل الكود ---
if not check_password():
    st.stop() 

# --- تهيئة البيانات ---
if "invoices" not in st.session_state: st.session_state.invoices = []
if "inventory" not in st.session_state: st.session_state.inventory = pd.DataFrame(columns=["الصنف", "الكمية"])
if "expenses" not in st.session_state: st.session_state.expenses = []

# --- القائمة الجانبية ---
st.sidebar.title("القائمة الرئيسية")
page = st.sidebar.radio("انتقل إلى:", ["1️⃣ إنشاء فواتير", "2️⃣ مخزن الفواتير", "3️⃣ مخزن البضائع", "4️⃣ الحسابات والتقارير"])

# --- الصفحة الأولى: إنشاء فواتير ---
if page == "1️⃣ إنشاء فواتير":
    st.title("📄 إنشاء فاتورة جديدة")
    col1, col2, col3 = st.columns(3)
    with col1:
        customer_name = st.text_input("الاسم")
        customer_phone = st.text_input("رقم الزبون")
        invoice_date = st.date_input("التاريخ", datetime.now())
    with col2:
        payment_method = st.selectbox("طريقة الدفع", ["نقداً", "بطاقة"])
        delivery_cost = st.number_input("تكلفة التوصيل", value=0.0)
    with col3:
        discount = st.number_input("الخصم", value=0.0)

    available_items = st.session_state.inventory["الصنف"].tolist()
    invoice_items = []
    total_invoice_subtotal = 0.0
    
    for i in range(1, 6):
        selected_item = st.selectbox(f"اختر الصنف {i}", ["-- لا يوجد --"] + available_items, key=f"item_{i}")
        if selected_item != "-- لا يوجد --":
            qty = st.number_input(f"الكمية {i}", min_value=1, key=f"qty_{i}")
            price = st.number_input(f"السعر {i}", key=f"price_{i}")
            total_invoice_subtotal += (qty * price)
            invoice_items.append({"الصنف": selected_item, "الكمية": qty, "السعر": price})

    if st.button("حفظ واعتماد الفاتورة"):
        inv_id = len(st.session_state.invoices) + 1001
        st.session_state.invoices.append({"رقم الفاتورة": inv_id, "الاسم": customer_name, "المجموع": total_invoice_subtotal + delivery_cost - discount, "المنتجات": invoice_items})
        st.success(f"تم حفظ الفاتورة {inv_id}")

# --- باقي الصفحات (أضف الكود الخاص بك هنا بنفس الطريقة) ---
elif page == "2️⃣ مخزن الفواتير":
    st.title("🗄️ مخزن الفواتير")
    st.write(st.session_state.invoices)

elif page == "3️⃣ مخزن البضائع":
    st.title("📦 مخزن البضائع")
    add_name = st.text_input("اسم الصنف")
    add_qty = st.number_input("الكمية")
    if st.button("إضافة"):
        new_row = pd.DataFrame([{"الصنف": add_name, "الكمية": add_qty}])
        st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
        st.success("تمت الإضافة")
    st.dataframe(st.session_state.inventory)

elif page == "4️⃣ الحسابات والتقارير":
    st.title("💰 الحسابات")
    st.write("الصافي المالي:", sum(inv["المجموع"] for inv in st.session_state.invoices))
