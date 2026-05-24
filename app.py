import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="نظام إدارة الفواتير والمخازن المطور", layout="wide")

# --- تهيئة البيانات ---
if "invoices" not in st.session_state: st.session_state.invoices = []
if "inventory" not in st.session_state: 
    st.session_state.inventory = pd.DataFrame(columns=["الصنف", "الكمية"])

# ==========================================
# وظائف مساعدة
# ==========================================
def highlight_stock(row):
    color = '#d32f2f' if row['الكمية'] <= 0 else '#2e7d32'
    return [f'background-color: {color}; color: white'] * len(row)

# ==========================================
# القائمة الجانبية (مخزن الفواتير)
# ==========================================
st.sidebar.title("🗄️ مخزن الفواتير")
search_query = st.sidebar.text_input("🔍 بحث برقم الفاتورة أو الاسم")
if st.sidebar.button("عرض الفواتير"):
    st.session_state.show_invoices = True

if st.session_state.get("show_invoices", False):
    with st.sidebar.expander("قائمة الفواتير", expanded=True):
        filtered_invoices = st.session_state.invoices
        if search_query:
            filtered_invoices = [inv for inv in st.session_state.invoices if search_query in str(inv['رقم الفاتورة']) or search_query in inv['الاسم']]
        
        for inv in filtered_invoices:
            if st.button(f"فاتورة {inv['رقم الفاتورة']} - {inv['الاسم']}"):
                st.session_state.selected_invoice = inv

# عرض تفاصيل الفاتورة المختارة
if "selected_invoice" in st.session_state:
    inv = st.session_state.selected_invoice
    st.sidebar.info(f"### تفاصيل الفاتورة {inv['رقم الفاتورة']}\nالزبون: {inv['الاسم']}\nالإجمالي: {inv['المجموع النهائي']}")

# ==========================================
# الصفحات
# ==========================================
page = st.radio("انتقل إلى:", ["📄 إنشاء فاتورة", "📦 مخزن البضائع", "💰 الحسابات"])

if page == "📄 إنشاء فاتورة":
    st.title("📄 إنشاء فاتورة جديدة")
    # ... (بيانات العميل كما هي) ...
    
    invoice_items = []
    for i in range(1, 5):
        col1, col2, col3 = st.columns(3)
        with col1: selected_item = st.selectbox(f"صنف {i}", ["--"] + st.session_state.inventory["الصنف"].tolist(), key=f"item_{i}")
        
        if selected_item != "--":
            avail = st.session_state.inventory.loc[st.session_state.inventory["الصنف"] == selected_item, "الكمية"].values[0]
            with col2:
                qty = st.number_input(f"الكمية ({avail} متاح)", min_value=1, max_value=int(avail), key=f"qty_{i}")
                if qty > avail: st.error("غير متاح!")
            with col3: price = st.number_input(f"السعر", key=f"price_{i}")
            invoice_items.append({"الصنف": selected_item, "الكمية": qty, "السعر": price})

    if st.button("حفظ الفاتورة"):
        st.session_state.invoices.append({"رقم الفاتورة": len(st.session_state.invoices)+1001, "الاسم": "عميل", "المجموع النهائي": 100})
        st.success("تم الحفظ")

elif page == "📦 مخزن البضائع":
    st.title("📦 مخزن البضائع")
    # إضافة بضاعة
    add_name = st.text_input("اسم الصنف")
    add_qty = st.number_input("الكمية")
    if st.button("إضافة"):
        new_row = pd.DataFrame([{"الصنف": add_name, "الكمية": add_qty}])
        st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
    
    # عرض الجدول ملون
    st.dataframe(st.session_state.inventory.style.apply(highlight_stock, axis=1))

elif page == "💰 الحسابات":
    st.title("💰 الحسابات والتقارير")
    # عرض التوتال والضريبة
    total_sales = sum(inv['المجموع النهائي'] for inv in st.session_state.invoices)
    st.metric("إجمالي المبيعات", f"{total_sales} ريال")
    
    reason = st.text_input("📝 سبب الخصم أو تعديل الحساب (اختياري)")
    if st.button("اعتماد التقرير"):
        st.write(f"تم اعتماد البيانات. السبب المسجل: {reason}")
