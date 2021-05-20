#Used packages
import os
import pandas
import sys
import glob
import random
import getpass

#Setting up working directory
# if(getpass.getuser()=='USER'):
#     os.chdir('C:\\Users\\USER\Dropbox\GCC\Proyecto UBI\Simulaciones\Test simulation')
#     Output_path = 'C:\\Users\\USER\Dropbox\GCC\Proyecto UBI\Simulaciones\Test simulation\OutputData'

#--------------------------------Run parameters-------------------------------
Total_iterations = 400
Total_households = 8000
Total_C_firms = 100
Total_K_firms = 20
Total_banks = 10
Total_public_servants = 1360

#--------------------------------Initial state--------------------------------
#Firms
C_firms_initial_workers = 5000
K_firms_initial_workers = 1000
Initial_K_stock = 40000
Initial_K_output = 2000
Initial_C_output = 32000
Initial_K_unit_costs = 2.5
Initial_C_unit_variable_costs = 0.78125
Initial_C_unit_costs = 0.936688446646308
Initial_C_nominal_K_stock = 53863.5973497354
Initial_K_goods_price = 2.6875
Initial_C_goods_price = 1.03035703125
Initial_K_deposits = 5000
Initial_C_deposits = 25000
Initial_K_inventories = 200
Initial_C_inventories = 3200
Initial_K_loan = 1298.02106027597
Initial_C_loan = 52194.5297373919
Initial_K_t0_loan = 129.52835574057
Initial_C_t0_loan = 5208.44524209744
Initial_K_profits_pretax = 381.466344464447
Initial_C_profits_pretax = 2693.19773430481
Initial_K_taxes = 68.6639420036004
Initial_C_taxes = 484.775592174865
Initial_K_dividends = 281.522162214762
Initial_C_dividends = 1987.57992791695
Initial_K_OCF = 189.214650146649
Initial_C_OCF = 2340.2389051818
Initial_K_ULC_markup = 0.075
Initial_C_ULC_markup = 0.318857
Initial_capacity_of_utilization_rate = 0.8

#Households
Initial_net_income = 33554.5129776643
Initial_net_wealth = 80704.7456861706
Initial_household_deposits = 80704.7456861706
Initial_household_taxes = 7084.64919021899
Initial_household_consumption = 32000
Initial_household_expenditure = 32971.425

#Labor market
Initial_unemployment = 0.08
Initial_total_employment = 7360
Initial_wages = 5

#Banks
Initial_r_loans = 0.0075
Initial_r_deposits = 0.0025
Initial_bank_profits_pretax = 218.479532103603
Initial_bank_bonds = 38274.3447309599
Initial_bank_taxes = 39.3263157786486
Initial_bank_dividends = 107.491929794973
Initial_bank_net_wealth = 9626.49962488258
Initial_bank_reserves = 28564.3497824065
Initial_bank_target_K_ratio = 0.179959629543452
Initial_bank_target_liquidity_ratio = 0.258022811988401

#Central Bank
Initial_CB_bonds = 28564.3497823941
Initial_CB_profits = 70.8792798570574
Initial_economy_bonds_stocks = 66838.6945133299

#-----------------------------Economic parameters-----------------------------
#General
Growth_rate_SS = 0.0075
Folded_normal_mean = 0
Folded_normal_variance = 0.0094
Precision = 1e-5

#Firms
K_productivity = 1
L_productivity_K = 2
Inventories_target_share = 0.1
Adaptative_expectations = 0.25
K_goods_duration = 20
Firms_dividends_share = 0.9
K_L_ratio = 6.4
L_turnover_ratio = 0.05
Precautionary_deposits_share = 1
Target_profit_rate = 0.0434475048145534
Target_capacity_utilization = 0.8
Profit_rate_weight = 0.01
Capacity_utilization_rate_weight = 0.02
Min_K_units = 20
Haircut_deafaulted_K_value = 0.5
Bankruptcy_buffer = 0.2
minWageDiscount = 1

#Households
Propensity_to_consume_wealth = 0.25
Propensity_to_consume_income = 0.385803036806576

#Banks
Loans_duration = 20
Banks_dividends_share = 0.6
Banks_K_risk_aversion = 20.8100476049258
Banks_C_risk_aversion = 3.21907520325338
Min_capital_ratio = 0.06
Min_liquidity_ratio = 0.08

#Central Bank
CB_i_advances = 0.005
Cash_advance_duration = 1

#Markets
N_partners_K_market = 5
N_partners_C_market = 5
N_partners_credit_market = 3
N_partners_deposit_market = 3
N_partners_labor_market = 10
Choice_intensity_K_market = 3.46574
Choice_intensity_C_market = 3.46574
Choice_intensity_credit_market = 4.62098    
Choice_intensity_deposits_market = 4.62098

#Government
Dole_proportion = 0.4
Profit_tax_rate = 0.18
Income_tax_rate = 0.18
Gov_r_bonds = 0.0025
Bonds_price = 1


# 'Unemployment threshold in wage revision function':0.08,
# 'Share of banking assets as net worth of banking sector':0.08,

# wealth_data = os.path.join(Output_path, 'wealth.txt')
# unem_data = os.path.join(Output_path, 'unem.txt')
# C_price_data = os.path.join(Output_path, 'C_price.txt')



