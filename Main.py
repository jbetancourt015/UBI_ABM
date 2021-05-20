#-----------------------------------------------------------------------------
#-------------------------------------SETUP-----------------------------------
#-----------------------------------------------------------------------------
#Setting up working directory
import os
import getpass
if(getpass.getuser()=='jpbon'):
     os.chdir('C:\\Users\jpbon\Dropbox\GCC\Proyecto UBI\Simulaciones\Caiani et al. (2016) based model\\New Simulation')

#Used packages and files
import Parameters
import Generator
import Plotting
import glob
import random


#-----------------------------------------------------------------------------
#---------------------------------INITIALIZATION------------------------------
#-----------------------------------------------------------------------------

data = {}
data['Y_cons_nominal'] = []
data['CPI'] = []
data['Y_cons_real'] = []
data['Y_cap_nominal'] = []
data['PPI'] = []
data['Y_cap_real'] = []
data['unemployment'] = []
data['GINI_income_pre'] = []
data['GINI_income_post'] = []
data['GINI_wealth_pre'] = []
data['GINI_wealth_post'] = []
data['C_BR_loan'] = []
data['C_BR_wage'] = []
data['K_BR_loan'] = []
data['K_BR_wage'] = []
data['Total Wealth'] = []
data['Total Wealth Laissez Faire'] = []
data['Available_deposits'] = []
data['K_demand'] = []
data['K_supply'] = []


data['aggregates'] = {}
data['aggregates']['Y_cons'] = 0
data['aggregates']['Y_cons_r'] = 0
data['aggregates']['Y_cap'] = 0
data['aggregates']['Y_cap_r'] = 0
data['aggregates']['c_br_loan'] = 0
data['aggregates']['c_br_wage'] = 0
data['aggregates']['k_br_loan'] = 0
data['aggregates']['k_br_wage'] = 0
data['aggregates']['available_deposits'] = 0
data['aggregates']['k_goods_demand'] = 0
data['aggregates']['k_goods_supply'] = 0

#Initialize agents
households = Generator.create_households()
Kfirms = Generator.create_K_firms()
Cfirms = Generator.create_C_firms()
banks = Generator.create_banks()
CB = Generator.create_central_bank()
gov = Generator.create_government()  

#Network is initialized
Generator.initialize_network(households, Kfirms, Cfirms, banks, CB, gov)

print('')
print('Basic setup complete.')

#-----------------------------------------------------------------------------
#-----------------------------------ITERATION---------------------------------
#-----------------------------------------------------------------------------
#Initializing temporal evolution
Generator.run_simulation(households, Kfirms, Cfirms, banks, CB, gov, 
                         data)

Plotting.plot(data)
