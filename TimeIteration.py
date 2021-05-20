#-----------------------------------------------------------------------------
#-------------------------------------SETUP-----------------------------------
#-----------------------------------------------------------------------------
#Used packages
import random
import Parameters
import Output
import CapitalMarket
import CreditMarket
import LaborMarket
import ConsumptionMarket
import DepositsMarket
import BondsMarket
import CashAdvances
import Output
import Statistics

#-----------------------------------------------------------------------------
#-----------------------------------AUXILIARY---------------------------------
#-----------------------------------------------------------------------------
def expectation(actual, exp=None):
    phi = Parameters.Adaptative_expectations
    if exp==None:
        exp = actual
    return phi*exp + (1-phi)*actual

def calculate_unemployment(households):
    unem = 0
    for household in households:
        if household.employer == None:
            unem += 1
    u_rate = unem/len(households)
    return u_rate

def calculate_avg_wage(households):
    total_wage = 0
    n_employed = 0
    for household in households:
        if household.employer != None:
            total_wage += household.res_wage
            n_employed += 1
    return total_wage/n_employed

def calculate_household_wealth(households):
    total_wealth = 0
    for household in households:
        total_wealth += household.deposits
    return total_wealth

def calculate_household_wealth_pre(households):
    total_wealth_pre = 0
    for household in households:
        total_wealth_pre += household.wealth_pre
    return total_wealth_pre

def calculate_avg_liquidity_ratio(banks):
    avg_liquidity_ratio = 0
    n_banks = 0
    
    for bank in banks:
        if bank.liquidity_ratio != 'no deposits':
            avg_liquidity_ratio += bank.liquidity_ratio
            n_banks += 1
    
    if n_banks > 0:
        avg_liquidity_ratio = avg_liquidity_ratio/n_banks
    else:
        avg_liquidity_ratio = None
        
    return avg_liquidity_ratio

def calculate_avg_capital_ratio(banks):
    avg_capital_ratio = 0
    n_banks = 0
    
    for bank in banks:
        if bank.capital_ratio != 'no loans':
            avg_capital_ratio += bank.capital_ratio
            n_banks += 1
    
    if n_banks > 0:
        avg_capital_ratio = avg_capital_ratio/n_banks
    else:
        avg_capital_ratio = None

def production_planning(Kfirms, Cfirms, data):
    data['aggregates']['c_br_loan'] = 0
    data['aggregates']['c_br_wage'] = 0
    data['aggregates']['k_br_loan'] = 0
    data['aggregates']['k_br_wage'] = 0
    #K firms' planning
    for firm in Kfirms:
        firm.status = None
        firm.plan_output()
    
    #C firms' planning
    for firm in Cfirms:
        firm.plan_output()

def consumption_planning(households):
    for household in households:
        household.plan_consumption()

def labor_demand(Kfirms, Cfirms):
    #K firms' demand
    for firm in Kfirms:
        firm.calculate_labor_demand()
    
    #C firms' demand
    for firm in Cfirms:
        firm.calculate_labor_demand()
    
def prices_interest_wages(Kfirms, Cfirms, banks, households):
    #K firms set prices
    for firm in Kfirms:
        firm.set_price()
    
    #C firms set prices
    for firm in Cfirms:
        firm.set_price()
    
    #Average capital ratio, liquidity ratio and average interest rates on loans
    #and deposits are calculated
    avg_capital_ratio = calculate_avg_capital_ratio(banks)
    avg_liquidity_ratio = calculate_avg_liquidity_ratio(banks)
    avg_r_loans = 0
    avg_r_deposits = 0
    
    for bank in banks:
        avg_r_loans += bank.r_loans
        avg_r_deposits += bank.r_deposits
    
    avg_r_loans = avg_r_loans/len(banks)
    avg_r_deposits = avg_r_deposits/len(banks)

    #Banks set interest rates
    for bank in banks:
        bank.set_r_loans(avg_capital_ratio, avg_r_loans)
        bank.set_r_deposits(avg_liquidity_ratio, avg_r_deposits)
    
    #Households update reservation wages
    u_rate = calculate_unemployment(households)
    for household in households:
        household.update_res_wage(u_rate)

def K_goods_demand(Cfirms, data):
    data['aggregates']['k_goods_demand'] = 0
    for firm in Cfirms:
        firm.calculate_K_goods_demand()
        data['aggregates']['k_goods_demand'] += firm.K_demand
    data['K_demand'].append(data['aggregates']['k_goods_demand'])

def K_market_matching(Kfirms, Cfirms):
    CapitalMarket.matching(Kfirms, Cfirms)

def credit_demand(Kfirms, Cfirms, banks, time):
    #K firms' credit demand
    for firm in Kfirms:
        firm.calculate_credit_demand(time)
    
    #C firms' credit demand
    for firm in Cfirms:
        firm.calculate_credit_demand(time)
        
    #Firms choose their lending bank
    CreditMarket.matching(Kfirms, Cfirms, banks)

def credit_supply(Kfirms, Cfirms, banks):
    CreditMarket.transactions(Kfirms, Cfirms, banks)

def labor_market(households, Kfirms, Cfirms, gov):
    #The workers and firms interact in the labor market
    LaborMarket.interaction(households, Kfirms, Cfirms, gov)

def production(Kfirms, Cfirms, data):
    #K firms' production
    data['aggregates']['k_goods_supply'] = 0
    for firm in Kfirms:
        firm.produce()
        data['aggregates']['k_goods_supply'] += firm.inventories
    data['K_supply'].append(data['aggregates']['k_goods_supply'])
        
    #C firm's production
    for firm in Cfirms:
        firm.produce()

def K_purchase(Kfirms, Cfirms, data):
    CapitalMarket.purchase(Kfirms, Cfirms, data)

def C_market(households, Cfirms, data):
    ConsumptionMarket.matching_and_transactions(households, Cfirms, data)

def payments(households, Kfirms, Cfirms, banks, CB, gov, data):
    #Interests on deposits are paid
    DepositsMarket.interest_payment(households, banks)
    
    #Banks' interest payments are reset
    for bank in banks:
        bank.interest_payment = 0
    
    #Interests on loans and loan repayments are paid
    for firm in Cfirms:
        firm.loans_payment(data)
    data['C_BR_loan'].append(data['aggregates']['c_br_loan'])
    
    for firm in Kfirms:
        firm.loans_payment(data)
    data['K_BR_loan'].append(data['aggregates']['k_br_loan'])
    
    #Bonds and interest are paid
    gov.reset_payments()
    BondsMarket.bonds_payment(banks, CB, gov)
    CashAdvances.advances_payment(banks, CB, gov)

def pay_wages_dole(Kfirms, Cfirms, gov, households, data):
    #K firms pay their wages
    for firm in Kfirms:
        firm.pay_wages(data)
    data['K_BR_wage'].append(data['aggregates']['k_br_wage'])
    
    #C firms pay their wages
    for firm in Cfirms:
        firm.pay_wages(data)
    data['C_BR_wage'].append(data['aggregates']['c_br_wage'])
        
    #The government pays its wages
    gov.pay_wages()
    
    #The wealth not taking into account government intervention is set
    for household in households:
        household.wealth_pre = household.deposits
    
    #The government pays dole to unemployed households
    avg_wage = calculate_avg_wage(households)
    for household in households:
        household.tax = Parameters.Income_tax_rate*household.income
        assert household.tax >= 0
        if household.employer == None:
            gov.pay_dole(household, avg_wage)

def pay_taxes(Kfirms, Cfirms, households, banks, gov):
    #K firms pay taxes
    for firm in Kfirms:
        firm.pay_taxes(gov)
    
    #C firms pay taxes
    for firm in Cfirms:
        firm.pay_taxes(gov)
    
    #Households pay taxes
    for household in households:
        household.pay_taxes(gov)
    
    #Banks pay taxes
    for bank in banks:
        bank.pay_taxes(gov)

def pay_dividends(Kfirms, Cfirms, banks, households):
    for household in households:
        household.income = 0
    
    #K firms pay dividends
    for firm in Kfirms:
        total_wealth = calculate_household_wealth(households)
        total_wealth_pre = calculate_household_wealth_pre(households)
        firm.pay_dividends(households, total_wealth, total_wealth_pre)
    
    #C firms pay dividends
    for firm in Cfirms:
        total_wealth = calculate_household_wealth(households)
        total_wealth_pre = calculate_household_wealth_pre(households)
        firm.pay_dividends(households, total_wealth, total_wealth_pre)
        
    #Banks pay dividends
    for bank in banks:
        total_wealth = calculate_household_wealth(households)
        total_wealth_pre = calculate_household_wealth_pre(households)
        bank.pay_dividends(households, total_wealth, total_wealth_pre)

def accounting_1(Kfirms, Cfirms):  
    #K firms perform their accounting
    for firm in Kfirms:
        firm.accounting()
        
    #C firms perform their first accounting
    for firm in Cfirms:
        firm.accounting_1()
    

def accounting_2(Cfirms, banks, households, data):
    
    #C firms perform their second accounting
    for firm in Cfirms:
        wealth = calculate_household_wealth(households)
        wealth_pre = calculate_household_wealth_pre(households)
        firm.accounting_2(households, wealth, wealth_pre)
    
    #Banks perform their accounting
    avg_capital_ratio = calculate_avg_capital_ratio(banks)
    for bank in banks:
        bank.accounting(avg_capital_ratio)

def deposits_market_matching(Kfirms, Cfirms, households, banks):
    DepositsMarket.matching(Kfirms, Cfirms, households, banks)

def bond_issuing(gov, CB, banks):
    gov.emit_bonds()
    
    avg_liquidity_ratio = calculate_avg_liquidity_ratio(banks)
    for bank in banks:
        bank.calculate_bonds_and_cash_demand(avg_liquidity_ratio)
        
    BondsMarket.bonds_buying(gov, CB, banks)

def advances_requests(banks, CB):
    CashAdvances.advances_requests(banks, CB)

#-----------------------------------------------------------------------------
#-------------------------------------CLASS-----------------------------------
#-----------------------------------------------------------------------------
class Simulation:
    
    #Initialization
    def __init__(self, time=0):
        self.time = time
    
    #Updating
    def update_time(self):
        self.time += 1
    
    #Iterative dynamics
    def iterate(self, households, Kfirms, Cfirms, banks, CB, gov, 
                         data):
        #1. Firms plan their production.
        production_planning(Kfirms, Cfirms, data)
        
        #1.5 Households calculate their desired consumption
        consumption_planning(households)
        
        #2. Firms evaluate their labor demand.
        labor_demand(Kfirms, Cfirms)
        
        #3. Firms determine prices, banks determine interest rates and workers
        #   workers update their reservation wages.
        prices_interest_wages(Kfirms, Cfirms, banks, households)
        
        #4. C firms determine their demand for capital goods.
        K_goods_demand(Cfirms, data)
        
        #5. C firms choose their K supplier.
        K_market_matching(Kfirms, Cfirms)
        
        #6. Firms evaluate their credit demand and choose their lending bank.
        credit_demand(Kfirms, Cfirms, banks, self.time)
        
        #7. Banks evaluate requested loans
        credit_supply(Kfirms, Cfirms, banks)
        
        #8. Unemployed workers interact with firms and the government on the 
        #   labor market
        labor_market(households, Kfirms, Cfirms, gov)
        
        #9. Firms produce their respective outputs
        production(Kfirms, Cfirms, data)
        
        #10. C firms purchase K from their supplier
        K_purchase(Kfirms, Cfirms, data)
        
        #11. Households purchase C goods and consume
        C_market(households, Cfirms, data)
        
        #11.1. Firms perform their accounting (Consumption firms perform their first accounting).
        accounting_1(Kfirms, Cfirms)
        
        #12. Loans, deposits and cash advances, along with their respecitve
        #    interests, are paid.
        payments(households, Kfirms, Cfirms, banks, CB, gov, data)
        
        #13. Wages and doles are paid
        pay_wages_dole(Kfirms, Cfirms, gov, households, data)
        
        #14. Income and profit taxes are paid to the government.
        pay_taxes(Kfirms, Cfirms, households, banks, gov)
        Statistics.GINI_income_pre(data, households)
        
        #15. Dividends are distributed to households.
        pay_dividends(Kfirms, Cfirms, banks, households)
        
        #15.1. Consumption firms and banks perform their accounting after expenses.
        accounting_2(Cfirms, banks, households, data)
        
        #15.2 Gini indexes are calculated and unemployment registered.
        Statistics.GINI_income_post(data, households)
        Statistics.GINI_wealth_pre(data, households)
        Statistics.GINI_wealth_post(data, households)
        Statistics.unemployment(data, households)
        data['Total Wealth'].append(calculate_household_wealth(households))
        data['Total Wealth Laissez Faire'].append(calculate_household_wealth_pre(households))
        
        #16. Firms and households select their deposit bank.
        deposits_market_matching(Kfirms, Cfirms, households, banks)
        
        #17. Issued bonds are purchased by banks and the Central Bank.
        bond_issuing(gov, CB, banks)
        
        #18. Requests for cash advances are accomodated by the Central Bank.
        advances_requests(banks, CB)
        
        #Statistics are called
        # Output.write_household_wealth(households, self.time)
        # Output.write_unemployment(households, self.time)
        # Output.write_C_price(Cfirms, self.time)
        
        #Time is updated
        self.update_time()
        print('Iterations: ', self.time)





















