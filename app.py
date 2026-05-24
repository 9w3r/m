import streamlit as st
import pandas as pd
from datetime import datetime

# --- نظام تسجيل الدخول (1414) ---
st.set_page_config(page_title="نظام إدارة الفواتير والمخازن المطور", layout="wide")

def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False
    if not st.session_state.password_correct:
        st.sidebar.title("🔐 قفل النظام")
        pwd = st.sidebar.text_input("أدخل كلمة السر للدخول:", type="password")
        if st.sidebar.button("دخول"):
            if pwd == "1414":
                st.session_state.password_correct = True
                st.rerun()
            else:
                st.sidebar.error("كلمة السر خاطئة!")
        return False
    return True

if not check_password():
    st.stop()

# --- الكود الخاص بك الأصلي ---

# تهيئة قاعدة البيانات المؤقتة في الجلسة (Session State)
if "invoices" not in st.session_state:
    st.session_state.invoices = []

# تصفير المخزن تماماً ليكون فارغاً وجاهزاً لإدخال بضائعك وتسميتها
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=["الصنف", "الكمية"])

if "expenses" not in st.session_state:
    st.session_state.expenses = []

# --- القائمة الجانبية للتنقل بين الصفحات ---
st.sidebar.title("القائمة الرئيسية")
page = st.sidebar.radio("انتقل إلى:", ["1️⃣ إنشاء فواتير", "2️⃣ مخزن الفواتير", "3️⃣ مخزن البضائع", "4️⃣ الحسابات والتقارير"])

# ==========================================
# الصفحة الأولى: إنشاء فواتير
# ==========================================
if page == "1️⃣ إنشاء فواتير":
    st.title("📄 إنشاء فاتورة جديدة")
    
    st.subheader("بيانات العميل والفاتورة الأساسية")
    col1, col2, col3 = st.columns(3)
    with col1:
        customer_name = st.text_input("الاسم")
        customer_phone = st.text_input("رقم الزبون / الهاتف")
        customer_loc = st.text_input("الموقع / العنوان")
        tax_number = st.text_input("رقم الضريبة")
        invoice_date = st.date_input("تاريخ الفاتورة", datetime.now())
    with col2:
        payment_method = st.selectbox("طريقة الدفع", ["نقداً", "بطاقة", "تحويل بنكي"])
        order_status = st.selectbox("حالة الطلب", ["تم التوصيل", "قيد الانتظار", "ملغي"])
        notes = st.text_area("ملاحظات الفاتورة", height=100)
    with col3:
        salesman = st.text_input("اسم المندوب")
        delivery_cost = st.number_input("تكلفة التوصيل", min_value=0.0, step=1.0)
        discount = st.number_input("الخصم المباشر", min_value=0.0, step=1.0)

    st.markdown("---")
    st.subheader("🛒 تفاصيل المنتجات والمواد (حتى 14 صنفاً)")

    available_items = st.session_state.inventory["الصنف"].tolist()
    invoice_items = []
    total_invoice_subtotal = 0.0
    total_invoice_tax = 0.0
    
    if not available_items:
        st.warning("⚠️ المخزن فارغ حالياً! الرجاء الذهاب إلى صفحة 'مخزن البضائع' أولاً.")
    else:
        for i in range(1, 15):
            st.markdown(f"**الصنف رقم ({i})**")
            icol1, icol2, icol3, icol4, icol5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
            with icol1:
                selected_item = st.selectbox(f"اختر الصنف {i}", ["-- لم يتم الاختيار --"] + available_items, key=f"item_{i}")
            if selected_item != "-- لم يتم الاختيار --":
                available_qty = st.session_state.inventory[st.session_state.inventory["الصنف"] == selected_item]["الكمية"].values[0]
                with icol2:
                    st.markdown(f"<p style='color:white; background-color:#2e7d32; padding:6px; border-radius:5px; text-align:center;'>متاح ({available_qty})</p>", unsafe_allow_html=True)
                with icol3:
                    qty = st.number_input(f"الكمية المطلوبة {i}", min_value=1, value=1, step=1, key=f"qty_{i}")
                with icol4:
                    price = st.number_input(f"السعر الإفرادي {i}", min_value=0.0, value=0.0, step=0.5, key=f"price_{i}")
                with icol5:
                    tax_pct = st.number_input(f"الضريبة (%) {i}", min_value=0.0, value=15.0, step=1.0, key=f"tax_{i}")
                item_subtotal = qty * price
                item_tax = item_subtotal * (tax_pct / 100)
                total_invoice_subtotal += item_subtotal
                total_invoice_tax += item_tax
                invoice_items.append({"الصنف": selected_item, "الكمية": qty, "السعر": price, "الضريبة": item_tax, "المخزون_المتاح": available_qty})
            st.markdown("<hr style='margin:0.5em 0px;'>", unsafe_allow_html=True)

        final_total = total_invoice_subtotal + total_invoice_tax + delivery_cost - discount
        st.write(f"### 💰 إجمالي الفاتورة: {final_total:.2f}")
        
        if st.button("حفظ واعتماد الفاتورة أوتوماتيكياً"):
            if not customer_name or not invoice_items:
                st.error("الرجاء إدخال اسم الزبون واختيار صنف واحد على الأقل.")
            else:
                inv_id = len(st.session_state.invoices) + 1001
                for item in invoice_items:
                    st.session_state.inventory.loc[st.session_state.inventory["الصنف"] == item["الصنف"], "الكمية"] -= item["الكمية"]
                st.session_state.invoices.append({"رقم الفاتورة": inv_id, "الاسم": customer_name, "المجموع النهائي": final_total, "المنتجات": invoice_items, "قيمة الضريبة": total_invoice_tax})
                st.success(f"تم حفظ الفاتورة {inv_id} بنجاح!")

# ==========================================
# الصفحة الثانية: مخزن الفواتير
# ==========================================
elif page == "2️⃣ مخزن الفواتير":
    st.title("🗄️ مخزن الفواتير المحفوظة")
    if not st.session_state.invoices:
        st.warning("لا توجد فواتير.")
    else:
        st.write(pd.DataFrame(st.session_state.invoices))

# ==========================================
# الصفحة الثالثة: مخزن البضائع
# ==========================================
elif page == "3️⃣ مخزن البضائع":
    st.title("📦 مخزن البضائع والمستودع")
    add_name = st.text_input("اسم الصنف الجديد:")
    add_qty = st.number_input("الكمية:", min_value=0, value=0)
    if st.button("تحديث المخزن"):
        new_row = pd.DataFrame([{"الصنف": add_name, "الكمية": add_qty}])
        st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
        st.success("تم التحديث!")
    st.dataframe(st.session_state.inventory)

# ==========================================
# الصفحة الرابعة: الحسابات
# ==========================================
elif page == "4️⃣ الحسابات والتقارير":
    st.title("💰 الحسابات والتقارير")
    if st.session_state.invoices:
        df_inv = pd.DataFrame(st.session_state.invoices)
        st.subheader("📑 جدول الفواتير والضرائب المدخلة")
        st.dataframe(df_inv[["رقم الفاتورة", "الاسم", "قيمة الضريبة", "المجموع النهائي"]], use_container_width=True)
