import streamlit as st
import random

# --- GAME SETUP & MEMORY ---
st.set_page_config(page_title="The Budget Sim", layout="centered")
st.title("First Year Survival: The Budget Sim")

if "month" not in st.session_state:
    st.session_state.month = 0  
    st.session_state.checking_balance = 200.0  
    st.session_state.savings_balance = 0.0     
    st.session_state.credit_card_balance = 0.0  
    st.session_state.burnout = 0  
    st.session_state.random_event = None
    st.session_state.pending_curveball = None 
    st.session_state.pending_burnout_penalty = False 
    st.session_state.lifestyle_trap = None 

# --- THE LEDGER ---
current_income = 3480.0

rent = 1400.0  
utilities = 160.0
insurance_and_phone = 165.0 
student_loans = 250.0 if st.session_state.month >= 6 else 0.0
total_fixed_expenses = rent + utilities + insurance_and_phone + student_loans

# --- CORE GAME FUNCTIONS ---

def draw_live_sidebar(live_check, live_sav, live_cc, b_change=0):
    st.sidebar.header("🏦 Live Accounts")
    st.sidebar.metric(label="Checking Account", value=f"${live_check:,.2f}")
    st.sidebar.metric(label="Savings Account", value=f"${live_sav:,.2f}")
    if live_cc > 0:
        st.sidebar.error(f"Credit Card Debt: ${live_cc:,.2f}")
    else:
        st.sidebar.metric(label="Credit Card Debt", value="$0.00")
        
    st.sidebar.write("---")
    st.sidebar.subheader("📋 Monthly Fixed Bills")
    st.sidebar.text(f"Rent: ${rent:,.2f}")
    st.sidebar.text(f"Utilities: ${utilities:,.2f}")
    st.sidebar.text(f"Phone/Ins: ${insurance_and_phone:,.2f}")
    if student_loans > 0:
        st.sidebar.text(f"Student Loans: ${student_loans:,.2f}")
    st.sidebar.write(f"**Total Fixed:** ${total_fixed_expenses:,.2f}")

    st.sidebar.write("---")
    st.sidebar.subheader("🧠 Mental Health")
    current_burnout = st.session_state.burnout + b_change
    display_burnout = min(max(current_burnout, 0), 100)
    
    if current_burnout >= 100: st.sidebar.error("🚨 100% BURNOUT REACHED!")
    elif current_burnout >= 75: st.sidebar.warning("⚠️ CRITICAL STRESS!")
        
    st.sidebar.progress(display_burnout, text=f"Burnout: {current_burnout}%")

def resolve_burnout_penalty():
    if st.session_state.pending_burnout_penalty:
        st.error("🚨 **100% BURNOUT REACHED: MANDATORY LEAVE** 🚨")
        st.write("You pushed yourself too hard and had to take involuntary time off to recover. This costs you **$500** in lost wages and medical co-pays.")
        
        pay_col = st.radio("How will you pay for this $500 penalty?", 
                           ["Checking Account", "Savings Account", "Credit Card"], 
                           index=None, key="burnout_pay")
        if pay_col:
            if pay_col == "Checking Account" and st.session_state.checking_balance < 500:
                st.error("🚨 DECLINED: Insufficient funds in Checking.")
                return False
            elif pay_col == "Savings Account" and st.session_state.savings_balance < 500:
                st.error("🚨 DECLINED: Insufficient funds in Savings.")
                return False

            if pay_col == "Checking Account": st.session_state.checking_balance -= 500
            elif pay_col == "Savings Account": st.session_state.savings_balance -= 500
            elif pay_col == "Credit Card": st.session_state.credit_card_balance += 500
            
            st.session_state.burnout = 75 
            st.session_state.pending_burnout_penalty = False
            st.rerun()
        return False 
    return True

def resolve_curveball():
    if st.session_state.pending_curveball:
        event = st.session_state.pending_curveball
        st.warning(f"🌪️ **SURPRISE EVENT:** {event['name']} (Cost: ${abs(event['cost']):,.2f})")
        
        if event['cost'] >= 0:
            st.success(f"Lucky break! +${event['cost']:,.2f} added to your checking.")
            st.session_state.checking_balance += event['cost']
            st.session_state.pending_curveball = None
            st.rerun()
        else:
            pay_col = st.radio("How will you pay for this emergency?", 
                               ["Checking Account", "Savings Account", "Credit Card"], 
                               index=None, key="curveball_pay")
            if pay_col:
                cost_abs = abs(event['cost'])
                if pay_col == "Checking Account" and st.session_state.checking_balance < cost_abs:
                    st.error("🚨 DECLINED: Insufficient funds in Checking.")
                    return False
                elif pay_col == "Savings Account" and st.session_state.savings_balance < cost_abs:
                    st.error("🚨 DECLINED: Insufficient funds in Savings.")
                    return False

                if pay_col == "Checking Account": st.session_state.checking_balance -= cost_abs
                elif pay_col == "Savings Account": st.session_state.savings_balance -= cost_abs
                elif pay_col == "Credit Card": st.session_state.credit_card_balance += cost_abs
                
                st.session_state.pending_curveball = None
                st.rerun()
            return False 
    return True

def run_phase_1(month_num):
    st.write("### 🏠 Step 1: Lifestyle")
    
    if month_num == 4:
        st.error("📈 **BREAKING NEWS: INFLATION SPIKE!**\n\nGlobal supply chain issues have driven up the cost of living. Starting this month, all **Groceries and Gas** prices have increased by 15%!")
    elif month_num > 4:
        st.warning("📈 Reminder: The 15% inflation increase is still in effect for Groceries and Gas.")

    if month_num == 1:
        st.info("Month 1 begins. Your $200 graduation gift is in your account, and your fixed bills have been automatically paid.")
    else:
        st.success(f"💸 **Payday!** +${current_income:,.2f} deposited. Bills (-${total_fixed_expenses:,.2f}) paid.")
    
    inf = 1.15 if month_num >= 4 else 1.0
    g_costs = [int(250 * inf), int(400 * inf), int(600 * inf)]
    t_costs = [int(100 * inf), int(200 * inf), int(350 * inf)]

    if month_num == 1:
        g_desc = [f"Discount (Meal prepping, generic brands, rarely eat out) - ${g_costs[0]}", f"Standard (Good mix of groceries, casual takeout 1-2x a week) - ${g_costs[1]}", f"Premium (High-end grocery stores, frequent dining out/delivery) - ${g_costs[2]}"]
        t_desc = [f"Public Transit (Bus/Train pass, walking, no car maintenance) - ${t_costs[0]}", f"Standard Commuter (Average gas usage, basic parking/tolls) - ${t_costs[1]}", f"Heavy Commuter (Long daily drive, frequent weekend road trips) - ${t_costs[2]}"]
        l_desc = ["Bare Bones (Free hobbies, maybe one basic streaming app) - $50", "Average (Streaming apps, a few movies, casual weekend outings) - $200", "Treat Yourself (Concerts, premium hobbies, frequent nightlife) - $450"]
        h_desc = ["Minimalist (Basic generic toiletries, strictly DIY cleaning) - $30", "Standard (Brand name products, standard gym membership) - $100", "Premium (Luxury care products, boutique fitness classes/salons) - $250"]
    else:
        g_desc = [f"Discount - ${g_costs[0]}", f"Standard - ${g_costs[1]}", f"Premium - ${g_costs[2]}"]
        t_desc = [f"Public - ${t_costs[0]}", f"Standard - ${t_costs[1]}", f"Heavy - ${t_costs[2]}"]
        l_desc = ["Bare Bones - $50", "Average - $200", "Treat Yourself - $450"]
        h_desc = ["Minimalist - $30", "Standard - $100", "Premium - $250"]

    g_choice = st.radio("🛒 Groceries & Food:", g_desc, index=None, key=f"g{month_num}")
    t_choice = st.radio("⛽ Gas & Commuting:", t_desc, index=None, key=f"t{month_num}")
    l_choice = st.radio("🎬 Entertainment:", l_desc, index=None, key=f"l{month_num}")
    h_choice = st.radio("🧼 Hygiene & Household Upkeep:", h_desc, index=None, key=f"h{month_num}")
    
    p1_method = st.selectbox("💳 How will you pay for your lifestyle choices?", 
                             ["Checking Account", "Savings Account", "Credit Card"], index=None, key=f"p1_meth{month_num}")

    trap_choice = None
    trap_method = None
    trap_cost = 0
    if month_num == 1:
        st.write("---")
        st.write("### 🛋️ Step 1.5: Settle In (Mandatory)")
        st.write("You must make ONE major investment to help you survive your first year. Each offers a mental health boost.")
        trap_choice = st.radio("Choose your commitment:", [
            "🚗 The 'Beater' Car (-$1,500): Buy a cheap used car. (-5% Burnout/mo)",
            "🐶 The Companion (-$150): Adopt a rescue pet. (-10% Burnout/mo)",
            "📺 The Tech Setup ($0 today): 65\" TV & Gaming setup on a Buy Now, Pay Later plan. (-5% Burnout/mo)"
        ], index=None)
        
        if trap_choice:
            if "Car" in trap_choice:
                trap_cost = 1500
                trap_method = st.selectbox("How to pay $1,500 for the car?", ["Checking Account", "Savings Account", "Credit Card"], index=None, key="t_meth")
            elif "Companion" in trap_choice:
                trap_cost = 150
                trap_method = st.selectbox("How to pay $150 for the pet?", ["Checking Account", "Savings Account", "Credit Card"], index=None, key="t_meth")
            elif "Tech" in trap_choice:
                trap_cost = 0
                trap_method = "BNPL"
                st.info("You pay $0 today. The $1,000 balance is deferred for 6 months.")

    phase1_complete = all([g_choice, t_choice, l_choice, h_choice, p1_method])
    if month_num == 1:
        if not trap_choice or (trap_cost > 0 and not trap_method):
            phase1_complete = False

    g_cost = g_costs[0] if g_choice and "Discount" in g_choice else (g_costs[1] if g_choice and "Standard" in g_choice else (g_costs[2] if g_choice and "Premium" in g_choice else 0))
    t_cost = t_costs[0] if t_choice and "Public" in t_choice else (t_costs[1] if t_choice and "Standard" in t_choice else (t_costs[2] if t_choice and "Heavy" in t_choice else 0))
    l_cost = 50 if l_choice and "Bare" in l_choice else (200 if l_choice and "Average" in l_choice else (450 if l_choice and "Treat" in l_choice else 0))
    h_cost = 30 if h_choice and "Minimalist" in h_choice else (100 if h_choice and "Standard" in h_choice else (250 if h_choice and "Premium" in h_choice else 0))
    p1_total = g_cost + t_cost + l_cost + h_cost

    b_change = 0
    if g_choice and "Discount" in g_choice: b_change += 7 
    if l_choice and "Bare" in l_choice: b_change += 15
    elif l_choice and "Treat" in l_choice: b_change -= 15
    if h_choice and "Minimalist" in h_choice: b_change += 8
    
    current_trap = st.session_state.get("lifestyle_trap")
    if current_trap == "Car" or (month_num == 1 and trap_choice and "Car" in trap_choice): b_change -= 5
    elif current_trap == "Pet" or (month_num == 1 and trap_choice and "Companion" in trap_choice): b_change -= 10
    elif current_trap == "BNPL" or (month_num == 1 and trap_choice and "Tech" in trap_choice): b_change -= 5
    
    live_check = st.session_state.checking_balance + current_income - total_fixed_expenses
    live_sav = st.session_state.savings_balance
    live_cc = st.session_state.credit_card_balance

    check_deduct = 0
    sav_deduct = 0
    cc_deduct = 0
    
    if p1_method == "Checking Account": check_deduct += p1_total
    elif p1_method == "Savings Account": sav_deduct += p1_total
    elif p1_method == "Credit Card": cc_deduct += p1_total
    
    if month_num == 1 and trap_cost > 0 and trap_method:
        if trap_method == "Checking Account": check_deduct += trap_cost
        elif trap_method == "Savings Account": sav_deduct += trap_cost
        elif trap_method == "Credit Card": cc_deduct += trap_cost

    p1_declined = False
    if live_check < check_deduct:
        st.error(f"🚨 DECLINED: Insufficient funds in Checking to cover ${check_deduct:,.2f}.")
        p1_declined = True
    if live_sav < sav_deduct:
        st.error(f"🚨 DECLINED: Insufficient funds in Savings to cover ${sav_deduct:,.2f}.")
        p1_declined = True

    if not p1_declined:
        live_check -= check_deduct
        live_sav -= sav_deduct
        live_cc += cc_deduct
    else:
        phase1_complete = False 

    st.write("---")
    st.write("### 🏦 Step 2: Management")
    cc_payment = 0.0
    
    if st.session_state.credit_card_balance > 0:
        st.error(f"Previous Statement Balance: ${st.session_state.credit_card_balance:,.2f}")
        max_cc_pay = round(float(min(live_check, st.session_state.credit_card_balance)), 2)
        if max_cc_pay > 0:
            cc_payment = st.number_input("Pay down Credit Card (Enter Exact Amount)", 
                                         min_value=0.0, 
                                         max_value=max_cc_pay, 
                                         value=0.0, 
                                         step=0.01, 
                                         format="%.2f", 
                                         key=f"cc{month_num}")
            live_check -= cc_payment
            live_cc -= cc_payment
            
    max_savings = max(0, int(live_check)) 
    savings_contribution = 0
    if max_savings > 0:
        savings_contribution = st.slider("Transfer to Savings", 0, max_savings, 0, step=25, key=f"s{month_num}")
        live_check -= savings_contribution
        live_sav += savings_contribution
        
    return phase1_complete, live_check, live_sav, live_cc, b_change, trap_choice

def process_end_of_month(month_num, final_check, final_sav, final_cc, b_change, trap_choice):
    st.session_state.checking_balance = round(final_check, 2)
    st.session_state.savings_balance = round(final_sav, 2)
    st.session_state.credit_card_balance = round(final_cc, 2)
    st.session_state.burnout = max(0, st.session_state.burnout + b_change) 
    
    if month_num == 1 and trap_choice:
        if "Car" in trap_choice: st.session_state.lifestyle_trap = "Car"
        elif "Companion" in trap_choice: st.session_state.lifestyle_trap = "Pet"
        elif "Tech" in trap_choice: st.session_state.lifestyle_trap = "BNPL"
    
    if st.session_state.burnout >= 100: 
        st.session_state.pending_burnout_penalty = True
    
    if st.session_state.credit_card_balance > 0:
        st.session_state.credit_card_balance *= 1.03 
        st.session_state.credit_card_balance = round(st.session_state.credit_card_balance, 2)
        
    trap_event = None
    if month_num == 3 and st.session_state.lifestyle_trap == "Pet":
        trap_event = {"name": "Your pet swallowed a sock! Emergency Vet Surgery.", "cost": -800}
    elif month_num == 4 and st.session_state.lifestyle_trap == "Car":
        trap_event = {"name": "The transmission on your 'beater' car blew.", "cost": -1200}
    elif month_num == 5 and st.session_state.lifestyle_trap == "BNPL":
        trap_event = {"name": "BNPL Promo Ended! The $1000 balance + $250 retroactive interest hit your account.", "cost": -1250}

    if trap_event:
        st.session_state.pending_curveball = trap_event
    else:
        events = [
            {"name": "Speeding Ticket.", "cost": -250},
            {"name": "Emergency Plumbing Leak.", "cost": -300},
            {"name": "Computer Repair.", "cost": -150},
            {"name": "IRS Tax Adjustment.", "cost": -200},
            {"name": "Small inheritance!", "cost": 150},
            {"name": "Sold furniture on FB Marketplace.", "cost": 100}
        ]
        st.session_state.pending_curveball = random.choice(events)
        
    st.session_state.month = month_num + 1
    st.rerun()

# --- THE GAME LOOP ---

# --- THE HOME SCREEN ---
if st.session_state.month == 0:
    st.write("### 🎓 Welcome to the Real World.")
    st.write("You just graduated and landed your first job. The goal is simple: **Survive this 6-month simulation without going broke or burning out.**")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### 🎮 How to Play")
        st.write("1. **Lifestyle:** Choose how you live (Groceries, Commute, etc.) and pick how to pay for it.")
        st.write("2. **Management:** Use your leftover cash to pay down Credit Card debt (3% monthly interest!) or build Savings.")
        st.write("3. **Dilemma:** Face a monthly scenario and decide how to handle it.")
        st.write("4. **Curveballs:** Emergencies happen. You will have to pay for them before you can start the next month.")
    
    with col2:
        st.write("#### 📊 The Starting Ledger")
        st.write("* Graduation Gift: **$200.00**")
        st.write("* Monthly Paycheck: **$3,480.00**")
        st.write("* Fixed Bills: **-$1,725.00** *(Rent, Utilities, Phone)*")
        st.write("---")
        st.warning("🧠 **The Golden Rule:** Watch your Mental Health meter! If you go too cheap on everything, your Burnout will rise. If it hits **100%**, you will be forced to take unpaid leave and face a **$500 penalty**.")

    st.write("---")
    if st.button("Start 6-Month Simulation", use_container_width=True):
        st.session_state.month = 1
        st.rerun()

# --- MONTHS 1 TO 6 ---
elif st.session_state.month <= 6:
    st.header(f"Month {st.session_state.month} of 6")
    
    if st.session_state.burnout >= 100:
        st.error(f"🚨 BURNOUT CRITICAL ({st.session_state.burnout}%): You pushed yourself too hard!")
    elif st.session_state.burnout >= 75:
        st.error(f"🛑 WARNING: Your burnout is at {st.session_state.burnout}%. You are close to total exhaustion. Consider spending more to recover!")
    elif st.session_state.burnout >= 50:
        st.warning(f"⚠️ NOTICE: Burnout is rising ({st.session_state.burnout}%). Your mental health is slipping.")

    if not resolve_burnout_penalty():
        st.stop()
        
    if not resolve_curveball():
        st.stop() 

    p1_done, l_check, l_sav, l_cc, b_change, trap_choice = run_phase_1(st.session_state.month)
    
    st.write("---")
    st.write("### 🎲 Step 3: Dilemma")
    
    if st.session_state.month == 1:
        st.write("👔 **Wardrobe:** You need professional clothes.")
        d_choice = st.radio("Buy?", ["Thrifted (-$150)", "Department Store (-$300)", "Designer (-$600)"], index=None)
        d_cost = 150 if d_choice and "Thrifted" in d_choice else (300 if d_choice and "Department" in d_choice else 600 if d_choice else 0)
    elif st.session_state.month == 2:
        st.write("🍻 **Networking:** Pricey happy hour.")
        d_choice = st.radio("Go?", ["Yes (-$60)", "No (-$0)"], index=None)
        d_cost = 60 if d_choice and "Yes" in d_choice else 0
    elif st.session_state.month == 3:
        st.write("✈️ **Friend's Trip:** Weekend getaway.")
        d_choice = st.radio("Choice?", ["Go (-$400)", "Gift (-$100)", "Skip (-$0)"], index=None)
        d_cost = 400 if d_choice and "Go" in d_choice else (100 if d_choice and "Gift" in d_choice else 0)
    elif st.session_state.month == 4:
        st.write("🦷 **Dental:** Cracked tooth.")
        d_choice = st.radio("Action?", ["Dentist (-$200)", "Numbing Gel (-$20)"], index=None)
        d_cost = 200 if d_choice and "Dentist" in d_choice else 20
        if d_choice and "Gel" in d_choice: b_change += 20
    elif st.session_state.month == 5:
        st.write("🏠 **Family:** Parents visit.")
        d_choice = st.radio("Host?", ["Dinners Out (-$300)", "Home Cooking (-$100)"], index=None)
        d_cost = 300 if d_choice and "Out" in d_choice else 100
    elif st.session_state.month == 6:
        st.write("💻 **Laptop:** Tech death.")
        d_choice = st.radio("Buy?", ["New MacBook (-$1400)", "Refurbished (-$600)", "Chromebook (-$200)"], index=None)
        d_cost = 1400 if d_choice and "MacBook" in d_choice else (600 if d_choice and "Refurbished" in d_choice else 200 if d_choice else 0)

    p2_method = st.selectbox("How will you pay for the Dilemma?", ["Checking Account", "Savings Account", "Credit Card"], index=None)
    
    p2_declined = False
    if p2_method == "Checking Account" and l_check < d_cost:
        st.error(f"🚨 DECLINED: Insufficient funds in Checking to cover ${d_cost:,.2f}.")
        p2_declined = True
    elif p2_method == "Savings Account" and l_sav < d_cost:
        st.error(f"🚨 DECLINED: Insufficient funds in Savings to cover ${d_cost:,.2f}.")
        p2_declined = True

    f_check, f_sav, f_cc = l_check, l_sav, l_cc
    if not p2_declined:
        if p2_method == "Checking Account": f_check -= d_cost
        elif p2_method == "Savings Account": f_sav -= d_cost
        elif p2_method == "Credit Card": f_cc += d_cost

    draw_live_sidebar(f_check, f_sav, f_cc, b_change)
    
    st.warning("⬆️ **REMINDER:** Don't forget to complete all options in Step 1 above!")

    if p1_done and d_choice and p2_method and not p2_declined:
        if st.button(f"Finalize Month {st.session_state.month}"):
            process_end_of_month(st.session_state.month, f_check, f_sav, f_cc, b_change, trap_choice)
    else:
        st.button(f"Finalize Month {st.session_state.month}", disabled=True)

# --- END GAME ---
else:
    st.balloons()
    st.title("Simulation Over.")
    st.metric("Savings", f"${st.session_state.savings_balance:,.2f}")
    st.metric("Debt", f"${st.session_state.credit_card_balance:,.2f}")
    st.metric("Burnout", f"{st.session_state.burnout}%")
    if st.button("Restart"):
        st.session_state.clear()
        st.rerun()