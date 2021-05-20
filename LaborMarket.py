import Parameters
import random

#Households interact with firms and the government
def interaction(households, Kfirms, Cfirms, gov):
    demand_firms = []
    N_partners = Parameters.N_partners_labor_market
    
    #Firms' labor demand
    for cfirm in Cfirms:
        if cfirm.status != 'BRII':
            demand_firms.append(cfirm)
    
    for kfirm in Kfirms:
        demand_firms.append(kfirm)
    
    unem = []
    for household in households:
        if household.employer == None:
            unem.append(household)
    
    random.shuffle(demand_firms)
    
    for firm in demand_firms:
        n_turnover = round(Parameters.L_turnover_ratio*len(firm.employees))
        random.shuffle(firm.employees)
        for i in range(n_turnover):
            household = firm.employees.pop()
            household.employer = None
            unem.append(household)        
        if len(firm.employees) > firm.desired_n_employees:
            while len(firm.employees) > firm.desired_n_employees:
                household = firm.employees.pop()
                household.employer = None
                unem.append(household)
            firm.extra_L_needed = 0
            assert len(firm.employees) == firm.desired_n_employees
        elif len(firm.employees) == firm.desired_n_employees:
            firm.extra_L_needed = 0
        else:
            firm.extra_L_needed = firm.desired_n_employees - len(firm.employees)
    
    for firm in demand_firms:
        a = min(len(unem), firm.extra_L_needed)
        for i in range(min(len(unem), firm.extra_L_needed)):
            options = []
            random.shuffle(unem)
            for j in range(min(len(unem), N_partners)):
                options.append([unem[j].res_wage, unem[j]])
            if len(options) > 0:
                options.sort(key=lambda x: int(x[0]),reverse = True)
                household = options.pop()[1]
                firm.employees.append(household)
                household.employer = firm
                unem.remove(household)
        if a == firm.extra_L_needed:
            assert len(firm.employees) == firm.desired_n_employees
    
    #Government's labor demand
    gov_turnover = round(Parameters.L_turnover_ratio*Parameters.Total_public_servants)
    random.shuffle(gov.employees)
    for i in range(gov_turnover):
        household = gov.employees.pop()
        household.employer = None
        unem.append(household)
        
    while len(gov.employees) > Parameters.Total_public_servants:
        household = gov.employees.pop()
        household.employer = None
        unem.append(household)
        
    if len(gov.employees) < Parameters.Total_public_servants:
        labor_demand = Parameters.Total_public_servants - len(gov.employees)
        for i in range(labor_demand):
            options = []
            random.shuffle(unem)
            for j in range(min(len(unem), N_partners)):
                options.append([unem[j].res_wage, unem[j]])
            if len(options) > 0:
                options.sort(key=lambda x: int(x[0]),reverse = True)
                household = options.pop()[1]
                gov.employees.append(household)
                household.employer = gov
                unem.remove(household)
    
    #Households update their status
    for household in households:
        del household.unem_hist[0]
        if household.employer == None:
            household.unem_hist.append(1)
        else:
            household.unem_hist.append(0)
        household.periods_unem = sum(household.unem_hist)






















        