import Parameters
import Statistics

def write_household_wealth(households, time):
    wealth = Statistics.calculate_household_wealth(households)
    wealth_txt = open(Parameters.wealth_data, 'a')
    wealth_txt.write('%s %s \n' % (time, wealth))
    wealth_txt.close()
    
def write_unemployment(households, time):
    unem = Statistics.calculate_unemployment(households)
    unem_txt = open(Parameters.unem_data, 'a')
    unem_txt.write('%s %s \n' % (time, unem))
    unem_txt.close()
    
def write_C_price(Cfirms, time):
    C_price = Statistics.calculate_C_price(Cfirms)
    C_price_txt = open(Parameters.C_price_data, 'a')
    C_price_txt.write('%s %s \n' % (time, C_price))
    C_price_txt.close()