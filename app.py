Import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة الأساسية
st.set_page_config(page_title="نظام إدارة الفواتير والمخازن المطور", layout="wide")

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
# الصفحة الأولى: إنشاء فواتير (محدثة بـ 14 خانة بضائع)
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

    # جلب قائمة الأصناف المتاحة بالمخزن
    available_items = st.session_state.inventory["الصنف"].tolist()
    
    invoice_items = []
    total_invoice_subtotal = 0.0
    total_invoice_tax = 0.0
    
    if not available_items:
        st.warning("⚠️ المخزن فارغ حالياً! الرجاء الذهاب إلى صفحة 'مخزن البضائع' أولاً لإضافة الأصناف وتسميتها لتتمكن من اختيارها هنا.")
    else:
        # إنشاء 14 خانة (أسطر) تحت بعضها لإدخال البضائع المتعددة
        for i in range(1, 15):
            st.markdown(f"**الصنف رقم ({i})**")
            icol1, icol2, icol3, icol4, icol5 = st.columns([2, 1.5, 1.5, 1.5, 1.5])
            
            with icol1:
                # خيار إضافي "لم يتم الاختيار" لكي لا يجبرك النظام على تعبئة الـ 14 خانة كلها إذا كانت البضائع أقل
                selected_item = st.selectbox(f"اختر الصنف {i}", ["-- لم يتم الاختيار --"] + available_items, key=f"item_{i}")
            
            if selected_item != "-- لم يتم الاختيار --":
                # فحص المخزون الفعلي المتاح
                available_qty = st.session_state.inventory[st.session_state.inventory["الصنف"] == selected_item]["الكمية"].values[0]
                is_available = available_qty > 0
                
                with icol2:
                    if is_available:
                        st.markdown(f"<p style='color:white; background-color:#2e7d32; padding:6px; border-radius:5px; text-align:center; font-size:14px;'>متاح (المخزون: {available_qty})</p>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p style='color:white; background-color:#c62828; padding:6px; border-radius:5px; text-align:center; font-size:14px;'>غير متاح (نافد)</p>", unsafe_allow_html=True)
                
                with icol3:
                    qty = st.number_input(f"الكمية المطلوبة {i}", min_value=1, value=1, step=1, key=f"qty_{i}")
                with icol4:
                    price = st.number_input(f"السعر الإفرادي {i}", min_value=0.0, value=0.0, step=0.5, key=f"price_{i}")
                with icol5:
                    tax_pct = st.number_input(f"الضريبة (%) {i}", min_value=0.0, value=15.0, step=1.0, key=f"tax_{i}")
                
                # حسابات الصنف الحالي
                item_subtotal = qty * price
                item_tax = item_subtotal * (tax_pct / 100)
                
                total_invoice_subtotal += item_subtotal
                total_invoice_tax += item_tax
                
                # حفظ الصنف في قائمة مؤقتة لإضافته للفاتورة
                invoice_items.append({
                    "الصنف": selected_item,
                    "الكمية": qty,
                    "السعر": price,
                    "الضريبة": item_tax,
                    "المخزون_المتاح": available_qty
                })
            else:
                with icol2: st.text("-")
                with icol3: st.text("-")
                with icol4: st.text("-")
                with icol5: st.text("-")
            st.markdown("<hr style='margin:0.5em 0px;'>>", unsafe_allow_html=True)

        # المجموع الكلي النهائي للفاتورة
        final_total = total_invoice_subtotal + total_invoice_tax + delivery_cost - discount
        
        st.write(f"### 💰 إجمالي الفاتورة الحالي: {final_total:.2f} (شامل ضريبة: {total_invoice_tax:.2f})")
        
        if st.button("حفظ واعتماد الفاتورة أوتوماتيكياً"):
            if not customer_name:
                st.error("الرجاء إدخال اسم الزبون قبل الحفظ.")
            elif not invoice_items:
                st.error("الرجاء اختيار صنف واحد على الأقل في الفاتورة.")
            else:
                # التحقق من أن الكميات المطلوبة متوفرة في المخزن
                error_found = False
                for item in invoice_items:
                    if item["الكمية"] > item["المخزون_المتاح"]:
                        st.error(f"الكمية المطلوبة من '{item['الصنف']}' أكبر من المتاح في المخزن ({item['المخزون_المتاح']})!")
                        error_found = True
                        break
                
                if not error_found:
                    # خصم الكميات من المخزن تلقائياً وإنشاء الفاتورة
                    inv_id = len(st.session_state.invoices) + 1001
                    
                    for item in invoice_items:
                        st.session_state.inventory.loc[st.session_state.inventory["الصنف"] == item["الصنف"], "الكمية"] -= item["الكمية"]
                    
                    invoice_data = {
                        "رقم الفاتورة": inv_id,
                        "الاسم": customer_name,
                        "رقم الهاتف": customer_phone,
                        "الموقع": customer_loc,
                        "رقم الضريبة": tax_number,
                        "التاريخ": str(invoice_date),
                        "المنتجات": invoice_items,
                        "المجموع الأساسي": total_invoice_subtotal,
                        "قيمة الضريبة": total_invoice_tax,
                        "المجموع النهائي": final_total,
                        "تكلفة التوصيل": delivery_cost,
                        "الخصم": discount,
                        "طريقة الدفع": payment_method
                    }
                    
                    st.session_state.invoices.append(invoice_data)
                    st.success(f"تم حفظ الفاتورة رقم {inv_id} بنجاح وتحديث كميات المخزن!")

# ==========================================
# الصفحة الثانية: مخزن الفواتير
# ==========================================
elif page == "2️⃣ مخزن الفواتير":
    st.title("🗄️ مخزن الفواتير المحفوظة")
    
    if not st.session_state.invoices:
        st.warning("لا توجد فواتير مسجلة حتى الآن.")
    else:
        df_invoices = pd.DataFrame(st.session_state.invoices)
        
        search_query = st.text_input("🔍 ابحث عن فاتورة (باسم الزبون أو رقم الهاتف):")
        
        if search_query:
            filtered_df = df_invoices[
                df_invoices["الاسم"].str.contains(search_query, case=False, na=False) | 
                df_invoices["رقم الهاتف"].str.contains(search_query, na=False)
            ]
        else:
            filtered_df = df_invoices
            
        st.write("اضغط على أي فاتورة بالأسفل لرؤية التفاصيل الكاملة:")
        
        for index, row in filtered_df.iterrows():
            if st.button(f"📄 فاتورة رقم: {row['رقم الفاتورة']} | العميل: {row['الاسم']} | الإجمالي: {row['المجموع النهائي']:.2f}"):
                st.markdown("---")
                st.subheader(f"🔍 تفاصيل الفاتورة الكاملة رقم: {row['رقم الفاتورة']}")
                
                col_i1, col_i2 = st.columns(2)
                with col_i1:
                    st.write(f"**الاسم:** {row['الاسم']}")
                    st.write(f"**رقم الهاتف:** {row['رقم الهاتف']}")
                    st.write(f"**الموقع:** {row['الموقع']}")
                    st.write(f"**الرقم الضريبي:** {row['رقم الضريبة']}")
                    st.write(f"**التاريخ:** {row['التاريخ']}")
                with col_i2:
                    st.write(f"**تكلفة التوصيل:** {row['تكلفة التوصيل']}")
                    st.write(f"**الخصم:** {row['الخصم']}")
                    st.write(f"**طريقة الدفع:** {row['طريقة الدفع']}")
                    st.write(f"**إجمالي الضريبة:** {row['قيمة الضريبة']:.2f}")
                    st.write(f"🟥 **المجموع النهائي الشامل:** {row['المجموع النهائي']:.2f}")
                
                st.write("**📦 البضائع المشمولة في هذه الفاتورة:**")
                st.table(pd.DataFrame(row['المنتجات'])[["الصنف", "الكمية", "السعر", "الضريبة"]])
                st.markdown("---")

# ==========================================
# الصفحة الثالثة: مخزن البضائع (المصفر والجاهز للتسمية)
# ==========================================
elif page == "3️⃣ مخزن البضائع":
    st.title("📦 مخزن البضائع والمستودع")
    
    st.subheader("➕ إضافة أو تحديث بضاعة وتسميتها")
    new_col1, new_col2 = st.columns(2)
    with new_col1:
        add_item_name = st.text_input("اكتب اسم الصنف الجديد:")
    with new_col2:
        add_item_qty = st.number_input("الكمية المتوفرة حالياً:", min_value=0, value=0, step=1)
        
    if st.button("🔄 تحديث وإضافة إلى المخزن"):
        if add_item_name:
            if add_item_name in st.session_state.inventory["الصنف"].values:
                st.session_state.inventory.loc[st.session_state.inventory["الصنف"] == add_item_name, "الكمية"] += add_item_qty
                st.success(f"تم زيادة كمية الصنف '{add_item_name}' بنجاح!")
            else:
                new_row = pd.DataFrame([{"الصنف": add_item_name, "الكمية": add_item_qty}])
                st.session_state.inventory = pd.concat([st.session_state.inventory, new_row], ignore_index=True)
                st.success(f"تم تسجيل وتسمية الصنف الجديد '{add_item_name}' في المخزن!")
        else:
            st.error("الرجاء كتابة اسم الصنف أولاً.")

    st.markdown("---")
    st.subheader("📊 جدول البضائع الحالي بالمستودع")
    
    if st.session_state.inventory.empty:
        st.info("المخزن فارغ تماماً حالياً. اكتب اسم البضاعة فوق لتعبئته.")
    else:
        def color_availability(row):
            return ['background-color: #2e7d32; color: white' if row['الكمية'] > 0 else 'background-color: #c62828; color: white'] * len(row)

        styled_inventory = st.session_state.inventory.style.apply(color_availability, axis=1)
        st.dataframe(styled_inventory, use_container_width=True)

# ==========================================
# الصفحة الرابعة: الحسابات والتقارير
# ==========================================
elif page == "4️⃣ الحسابات والتقارير":
    st.title("💰 الحسابات والتقارير المالية التلقائية")
    
    if st.session_state.invoices:
        df_inv = pd.DataFrame(st.session_state.invoices)
        total_sales = df_inv["المجموع النهائي"].sum()
        total_tax = df_inv["قيمة الضريبة"].sum()
    else:
        total_sales = 0.0
        total_tax = 0.0
        
    st.subheader("💸 تسجيل مصروفات جديدة (صرف)")
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        exp_reason = st.text_input("سبب الصرف:")
    with exp_col2:
        exp_amount = st.number_input("المبلغ المصروف:", min_value=0.0, step=1.0)
        
    if st.button("➕ تسجيل الصرف"):
        if exp_reason and exp_amount > 0:
            st.session_state.expenses.append({
                "التاريخ": str(datetime.now().date()),
                "سبب الصرف": exp_reason,
                "المبلغ المصروف": exp_amount
            })
            st.success("تم تسجيل المصروف بنجاح!")
        else:
            st.error("الرجاء كتابة السبب والمبلغ.")

    if st.session_state.expenses:
        df_exp = pd.DataFrame(st.session_state.expenses)
        total_expenses = df_exp["المبلغ المصروف"].sum()
    else:
        total_expenses = 0.0
        df_exp = pd.DataFrame(columns=["التاريخ", "سبب الصرف", "المبلغ المصروف"])
        
    net_profit = total_sales - total_expenses
    
    st.markdown("---")
    st.subheader("📈 الخلاصة المالية التلقائية")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="إجمالي المبيعات (الفواتير)", value=f"{total_sales:.2f}")
    m2.metric(label="إجمالي الضرائب المحصلة", value=f"{total_tax:.2f}")
    m3.metric(label="إجمالي مصاريف الصرف", value=f"{total_expenses:.2f}")
    m4.metric(label="الصافي (المجموع النهائي)", value=f"{net_profit:.2f}")
    
    st.markdown("---")
    st.subheader("📑 جدول مراجعة المصروفات")
    st.dataframe(df_exp, use_container_width=True)
    
    st.subheader("📑 جدول مراجعة الفواتير والضرائب المدخلة")
    if st.session_state.invoices:
        st.dataframe(df_inv[["رقم الفاتورة", "الاسم", "قيمة الضريبة", "المجموع النهائي"]], use_container_width=True)
