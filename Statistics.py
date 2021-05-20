import Parameters

def calculate_household_wealth(households):
    total_wealth = 0
    for household in households:
        total_wealth += household.deposits
    return total_wealth

def calculate_unemployment(households):
    total_unem = 0
    for household in households:
        if household.employer == None:
            total_unem += 1
    return total_unem/len(households)

def calculate_C_price(Cfirms):
    total = 0
    for firm in Cfirms:
        total += firm.price
    return total/len(Cfirms)

def C_nominal_output(data):
    # The nominal consumption output is added to the list.
    data['Y_cons_nominal'].append(data['aggregates']['Y_cons'])

def consumer_price_index(data):
    # The average price for consumption goods is calculated.
    if data['aggregates']['Y_cons_r'] > 0:
        average_price_cons = data['aggregates']['Y_cons']/data['aggregates']['Y_cons_r']
    else:
        average_price_cons = None
    
    if average_price_cons != None:
        # The CPI is calculated.
        cpi = (average_price_cons/Parameters.Initial_C_goods_price)*100
    else:
        cpi = None
    # The CPI is added to the list.
    data['CPI'].append(cpi)

def C_real_output(data):
    # The real consumption output is calculated.
    y_cons_real =  data['aggregates']['Y_cons_r']*Parameters.Initial_C_goods_price
    # The real consumption output is added to the list.
    data['Y_cons_real'].append(y_cons_real)
    
def K_nominal_output(data):
    # The nominal consumption output is added to the list.
    data['Y_cap_nominal'].append(data['aggregates']['Y_cap'])

def producer_price_index(data):
    # The average price for consumption goods is calculated.
    if data['aggregates']['Y_cap_r'] > 0:
        average_price_cap = data['aggregates']['Y_cap']/data['aggregates']['Y_cap_r']
    else:
        average_price_cap = None
    
    if average_price_cap != None:
        # The CPI is calculated.
        ppi = (average_price_cap/Parameters.Initial_K_goods_price)*100
    else:
        ppi = None
    # The CPI is added to the list.
    data['PPI'].append(ppi)

def K_real_output(data):
    # The real consumption output is calculated.
    y_cap_real =  data['aggregates']['Y_cap_r']*Parameters.Initial_K_goods_price
    # The real consumption output is added to the list.
    data['Y_cap_real'].append(y_cap_real)

def unemployment(data, households):
    # The unemployment rate is added to the list.
    data['unemployment'].append(calculate_unemployment(households))

def GINI_income_pre(data, households):
    # GINI coefficients:
    # For income before taxes and subsidies:
    agg_income_pre = 0
    hh_list = []
    nhhs = Parameters.Total_households
    for household in households:
        agg_income_pre += household.income
        hh_list.append(household.income)
    hh_list.sort()
    average = agg_income_pre/nhhs
    sum_1 = 0
    SUM_1 = 0
    SUM_2 = 0
    k = 0
    for amount in hh_list:
        k += 1
        sum_1 += amount
        SUM_1 += (k*average - sum_1)
        SUM_2 += (k*average)
    # The GINI coefficient is calculated.
    if SUM_2 > 0 and agg_income_pre > 0:
        GINI = SUM_1/SUM_2
    else:
        GINI = None
    # The GINI coefficient is added to the list.
    data['GINI_income_pre'].append(GINI)

def GINI_income_post(data, households):
    # For income after taxes and subsidies:
    agg_income_post = 0
    hh_list = []
    nhhs = Parameters.Total_households
    for household in households:
        agg_income_post += household.net_disposable_income
        hh_list.append(household.net_disposable_income)
    hh_list.sort()
    average = agg_income_post/nhhs
    sum_1 = 0
    SUM_1 = 0
    SUM_2 = 0
    k = 0
    for amount in hh_list:
        k += 1
        sum_1 += amount
        SUM_1 += (k*average - sum_1)
        SUM_2 += (k*average)
    # The GINI coefficient is calculated.
    if SUM_2 > 0 and agg_income_post > 0:
        GINI = SUM_1/SUM_2
    else:
        GINI = None
    # The GINI coefficient is added to the list.
    data['GINI_income_post'].append(GINI)
    
def GINI_wealth_pre(data, households):
    # For wealth before taxes and subsidies:
    agg_wealth_pre = 0
    hh_list = []
    nhhs = Parameters.Total_households
    for household in households:
        agg_wealth_pre += household.wealth_pre
        hh_list.append(household.wealth_pre)
    hh_list.sort()
    average = agg_wealth_pre/nhhs
    sum_1 = 0
    SUM_1 = 0
    SUM_2 = 0
    k = 0
    for amount in hh_list:
        k += 1
        sum_1 += amount
        SUM_1 += (k*average - sum_1)
        SUM_2 += (k*average)
    # The GINI coefficient is calculated.
    if SUM_2 > 0 and agg_wealth_pre > 0:
        GINI = SUM_1/SUM_2
    else:
        GINI = None
    # The GINI coefficient is added to the list.
    data['GINI_wealth_pre'].append(GINI)

def GINI_wealth_post(data, households):
    # For wealth after taxes and subsidies:
    agg_wealth_post = 0
    hh_list = []
    nhhs = Parameters.Total_households
    for household in households:
        agg_wealth_post += household.deposits
        hh_list.append(household.deposits)
    hh_list.sort()
    average = agg_wealth_post/nhhs
    sum_1 = 0
    SUM_1 = 0
    SUM_2 = 0
    k = 0
    for amount in hh_list:
        k += 1
        sum_1 += amount
        SUM_1 += (k*average - sum_1)
        SUM_2 += (k*average)
    # The GINI coefficient is calculated.
    if SUM_2 > 0 and agg_wealth_post > 0:
        GINI = SUM_1/SUM_2
    else:
        GINI = None
    # The GINI coefficient is added to the list.
    data['GINI_wealth_post'].append(GINI)  