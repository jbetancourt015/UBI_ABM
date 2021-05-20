#-----------------------------------------------------------------------------
#-------------------------------------SETUP-----------------------------------
#-----------------------------------------------------------------------------
#Used packages and files
import Parameters
import Households
import KFirms
import CFirms
import Banks
import Government
import CentralBank
import TimeIteration
import random

#-----------------------------------------------------------------------------
#-----------------------------------GENERATION--------------------------------
#-----------------------------------------------------------------------------
#Initializing the simulation
my_simulation = TimeIteration.Simulation()

#Generating agents
def create_households():
    population = []
    N = Parameters.Total_households
    for household_id in range(N):
        deposits = Parameters.Initial_household_deposits/N
        interest_on_deposits = deposits*Parameters.Initial_r_deposits
        reservation_wage = Parameters.Initial_wages
        last_price = Parameters.Initial_C_goods_price
        net_disposable_income = Parameters.Initial_net_income/N
        desired_consumption = Parameters.Initial_household_consumption/N
        income = (Parameters.Initial_K_dividends + Parameters.Initial_C_dividends + Parameters.Initial_bank_dividends)/N
        population.append(Households.Household(household_id + 1,deposits,interest_on_deposits,
                                               reservation_wage,last_price,net_disposable_income,
                                               desired_consumption, income = income))
    return population

def create_K_firms():
    K_sector = []
    N = Parameters.Total_K_firms
    for firm_id in range(N):
        mark_up = Parameters.Initial_K_ULC_markup
        deposits = Parameters.Initial_K_deposits/N
        interest_on_deposits = deposits*Parameters.Initial_r_deposits
        sales = Parameters.Initial_K_output/N
        inventories = Parameters.Initial_K_inventories/N
        inventories_past = Parameters.Initial_K_inventories/N
        output = Parameters.Initial_K_output/N
        price = Parameters.Initial_K_goods_price
        unit_cost_present = Parameters.Initial_K_unit_costs
        OCF = Parameters.Initial_K_OCF
        profit_post_tax = (Parameters.Initial_K_profits_pretax-Parameters.Initial_K_taxes)/N
        loan_granted = 0
        
        loan_sheet = [] #[value, age, r, outstanding debt, loan ID, bank]
        for i in range(Parameters.Loans_duration):
            value = Parameters.Initial_K_t0_loan/(N*(1+Parameters.Growth_rate_SS)**i)
            age = i
            r = Parameters.Initial_r_loans
            outstanding_debt = ((Parameters.Initial_K_t0_loan*(Parameters.Loans_duration - i))/
                                (N*Parameters.Loans_duration*(1 + Parameters.Growth_rate_SS)**i))
            loan_ID = None
            bank = None
            loan_sheet.append([value, age, r, outstanding_debt, loan_ID, bank])
        loan_sheet.reverse()
        
        K_sector.append(KFirms.KFirm(firm_id + 1,mark_up,deposits,interest_on_deposits,
                                     sales,inventories,inventories_past,output,
                                     price,unit_cost_present,OCF, profit_post_tax,
                                     loan_granted,loan_sheet))
    return K_sector

def create_C_firms():
    C_sector = []
    N = Parameters.Total_C_firms
    for firm_id in range(N):
        mark_up = Parameters.Initial_C_ULC_markup
        deposits = Parameters.Initial_C_deposits/N
        interest_on_deposits = deposits*Parameters.Initial_r_deposits
        sales = Parameters.Initial_C_output/N
        inventories = Parameters.Initial_C_inventories/N
        inventories_past = Parameters.Initial_C_inventories/N
        output = Parameters.Initial_C_output/N
        price = Parameters.Initial_C_goods_price
        unit_cost_present = Parameters.Initial_C_unit_costs
        OCF = Parameters.Initial_C_OCF
        profit_rate = Parameters.Target_profit_rate
        profit_post_tax = (Parameters.Initial_C_profits_pretax-Parameters.Initial_C_taxes)/N
        
        K_sheet = [] #[K amount, age, price, value, supplier]
        for i in range(Parameters.K_goods_duration):
            amount = Parameters.Initial_K_stock/(N*Parameters.K_goods_duration)
            age = i
            price = Parameters.Initial_K_goods_price/(1+Parameters.Growth_rate_SS)**i
            value = (Parameters.Initial_K_stock*Parameters.Initial_K_goods_price*
                    (Parameters.K_goods_duration - i))/(N*(Parameters.K_goods_duration**2)*
                    ((1 + Parameters.Growth_rate_SS)**i))
            supplier = None
            K_sheet.append([amount, age, price, value, supplier])
        K_sheet.reverse()
        
        K_stock = Parameters.Initial_K_stock/N
        loan_granted = 0
        
        loan_sheet = [] #[value, age, r, outstanding debt, loan ID, bank]
        for i in range(Parameters.Loans_duration):
            value = Parameters.Initial_C_t0_loan/(N*(1+Parameters.Growth_rate_SS)**i)
            age = i
            r = Parameters.Initial_r_loans
            outstanding_debt = ((Parameters.Initial_C_t0_loan*(Parameters.Loans_duration - i))/
                                (N*Parameters.Loans_duration*(1 + Parameters.Growth_rate_SS)**i))
            loan_ID = None
            bank = None
            loan_sheet.append([value, age, r, outstanding_debt, loan_ID, bank])
        loan_sheet.reverse()
        
        C_sector.append(CFirms.CFirm(firm_id + 1,mark_up,deposits,interest_on_deposits,
                                     sales,inventories,inventories_past,output,
                                     price,unit_cost_present,OCF,profit_rate,
                                     profit_post_tax,K_sheet,K_stock,
                                     loan_granted,loan_sheet))
    return C_sector

def create_banks():
    financial_sector = []
    N = Parameters.Total_banks
    for bank_id in range(N):
        r_loans = Parameters.Initial_r_loans
        r_deposits = Parameters.Initial_r_deposits
        reserves = 0
        loan_number = 0
        bonds = Parameters.Initial_bank_bonds/(N*Parameters.Bonds_price)
        net_worth = Parameters.Initial_bank_net_wealth/N
        cash_advances = 0
        financial_sector.append(Banks.Bank(bank_id + 1,r_loans,r_deposits,reserves,
                                           loan_number,bonds,net_worth,
                                           cash_advances))
    return financial_sector

def create_central_bank():
    bonds = Parameters.Initial_CB_bonds/Parameters.Bonds_price
    cash_advances = 0
    return CentralBank.Central_Bank(bonds,cash_advances)

def create_government():
    bonds = Parameters.Initial_economy_bonds_stocks/Parameters.Bonds_price
    reserves = 0
    return Government.Gov(bonds, reserves)

#Initial network
def initialize_network(households, Kfirms, Cfirms, banks, CB, gov):
    N_households = Parameters.Total_households
    N_Kfirms = Parameters.Total_K_firms
    N_Cfirms = Parameters.Total_C_firms
    N_banks = Parameters.Total_banks
    
    #Consumption firms hire workers
    random.shuffle(households)
    for i in range(N_Cfirms):
        N_workers = Parameters.C_firms_initial_workers//N_Cfirms
        for j in range(N_workers):
            household = households[i*N_workers + j]
            household.employer = Cfirms[i]
            Cfirms[i].employees.append(household)
        
    #Households are assigned old suppliers
    random.shuffle(households)
    for i in range(N_Cfirms):
        Households_per_firm = N_households//N_Cfirms
        for j in range(Households_per_firm):
            household = households[i*Households_per_firm + j]
            household.old_supplier = Cfirms[i]
    
    #Capital firms hire workers
    random.shuffle(households)
    for i in range(N_Kfirms):
        N_workers = Parameters.K_firms_initial_workers//N_Cfirms
        j = 0
        for household in households:
            if household.employer == None:
                household.employer = Kfirms[i]
                Kfirms[i].employees.append(household)
                j += 1
            if j == N_workers:
                break
    
    #Consumption firms are assigned old capital suppliers
    random.shuffle(Cfirms)
    for i in range(N_Kfirms):
        Cfirms_per_Kfirm = N_Cfirms//N_Kfirms
        for j in range(Cfirms_per_Kfirm):
            Cfirm = Cfirms[i*Cfirms_per_Kfirm + j]
            Cfirm.old_supplier = Kfirms[i]
    
    #Households are assigned a deposits bank
    random.shuffle(households)
    for i in range(N_banks):
        Households_per_bank = N_households//N_banks
        for j in range(Households_per_bank):
            household = households[i*Households_per_bank + j]
            household.deposits_bank = banks[i]
            banks[i].deposits_list.append(household)
    
    #Consumption firms are assigned a deposits bank
    random.shuffle(Cfirms)
    for i in range(N_banks):
        Cfirms_per_bank = N_Cfirms//N_banks
        for j in range(Cfirms_per_bank):
            Cfirm = Cfirms[i*Cfirms_per_bank + j]
            Cfirm.deposits_bank = banks[i]
            banks[i].deposits_list.append(Cfirm)
            
    #Capital firms are assigned a deposits bank
    random.shuffle(Kfirms)
    for i in range(N_banks):
        Kfirms_per_bank = N_Kfirms//N_banks
        for j in range(Kfirms_per_bank):
            Kfirm = Kfirms[i*Kfirms_per_bank + j]
            Kfirm.deposits_bank = banks[i]
            banks[i].deposits_list.append(Kfirm)
    
    #Banks are assigned to elements of loan sheets
    for t in range(Parameters.Loans_duration):
        #Consumption firms
        random.shuffle(Cfirms)
        for i in range(N_banks):
            Cfirms_per_bank = N_Cfirms//N_banks
            for j in range(Cfirms_per_bank):
                Cfirm = Cfirms[i*Cfirms_per_bank + j]
                banks[i].loan_number += 1
                Cfirm.loan_sheet[t][4] = str(banks[i].id) + '_' + str(banks[i].loan_number)
                Cfirm.loan_sheet[t][5] = banks[i]
                if t == Parameters.Loans_duration-1:
                    Cfirm.old_bank = banks[i]
                
                bank_sheet_element = Cfirm.loan_sheet[t]
                banks[i].loan_sheet.append(bank_sheet_element)
        
        #Capital firms
        random.shuffle(Kfirms)
        for i in range(N_banks):
            Kfirms_per_bank = N_Kfirms//N_banks
            for j in range(Kfirms_per_bank):
                Kfirm = Kfirms[i*Kfirms_per_bank + j]
                banks[i].loan_number += 1
                Kfirm.loan_sheet[t][4] = str(banks[i].id) + '_' + str(banks[i].loan_number)
                Kfirm.loan_sheet[t][5] = banks[i]
                if t == Parameters.Loans_duration-1:
                    Kfirm.old_bank = banks[i]
                
                bank_sheet_element = Kfirm.loan_sheet[t]
                banks[i].loan_sheet.append(bank_sheet_element)

    #Bank deposits and loans are calculated
    for bank in banks:
        deposits = 0
        for agent in bank.deposits_list:
            deposits += agent.deposits
        
        total_loans = 0
        for element in bank.loan_sheet:
            total_loans += element[3]
            
        bank.reserves = (bank.net_worth - bank.bonds*Parameters.Bonds_price - 
                         total_loans + deposits + bank.cash_advances)
        
        bank.liquidity_ratio = bank.reserves/deposits
        bank.capital_ratio = bank.net_worth/total_loans
        
    #Government employees are assigned
    random.shuffle(households)
    gov_employees = 0
    for household in households:
        if household.employer == None:
            household.employer = gov
            gov.employees.append(household)
            gov_employees += 1
        if gov_employees == Parameters.Total_public_servants:
            break
    
    #Unemployment history is created
    for household in households:
        if household.employer == None:
            household.unem_hist = [1,1,1,1]
            household.periods_unem = 4
        else:
            household.unem_hist = [0,0,0,0]
            household.periods_unem = 0
            
#-----------------------------------------------------------------------------
#------------------------------------ITERATION--------------------------------
#-----------------------------------------------------------------------------
#Running the simulation
def run_simulation(households, Kfirms, Cfirms, banks, CB, gov, 
                         data):
    while my_simulation.time < Parameters.Total_iterations:
        my_simulation.iterate(households, Kfirms, Cfirms, banks, CB, gov, 
                         data)
    
    print('')
    print('Simulation complete')





