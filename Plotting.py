import Parameters
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('ggplot')

def plot(data):
    # dat = pd.read_csv(Parameters.wealth_data,sep=' ', header = None)
    # plt.plot(dat.iloc[:,0], dat.iloc[:,1])
    # plt.show()

    # dat = pd.read_csv(Parameters.unem_data,sep=' ', header = None)
    # plt.plot(dat.iloc[:,0], dat.iloc[:,1])
    # plt.show()

    # dat = pd.read_csv(Parameters.C_price_data,sep=' ', header = None)
    # plt.plot(dat.iloc[:,0], dat.iloc[:,1])
    # plt.show()
    
    plt.plot(data['Y_cons_nominal'])
    plt.xlabel('Time')
    plt.ylabel('Nominal Consumption Output')
    plt.title('Evolution of nominal consumption output', )
    plt.show()
    

    plt.plot(data['Y_cons_real'])
    plt.xlabel('Time')
    plt.ylabel('Real Consumption Output')
    plt.title('Evolution of real consumption output', )
    plt.show()
    
    plt.plot(data['CPI'])
    plt.xlabel('Time')
    plt.ylabel('Consumer Price Index (%)')
    plt.title('Evolution of consumer price index', )
    plt.show()
    
    plt.plot(data['Y_cap_nominal'])
    plt.xlabel('Time')
    plt.ylabel('Nominal Capital Output')
    plt.title('Evolution of nominal capital output', )
    plt.show()
    

    plt.plot(data['Y_cap_real'])
    plt.xlabel('Time')
    plt.ylabel('Real Capital Output')
    plt.title('Evolution of real capital output', )
    plt.show()
    
    plt.plot(data['K_demand'], label = r'K demand')
    plt.plot(data['K_supply'], label = r'K_supply')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Units of capital goods')
    plt.title('Evolution of real capital demand and supply', )
    plt.show()
    
    plt.plot(data['PPI'])
    plt.xlabel('Time')
    plt.ylabel('Producer Price Index (%)')
    plt.title('Evolution of producer price index', )
    plt.show()
    

    plt.plot(data['unemployment'])
    plt.xlabel('Time')
    plt.ylabel('Unemployment rate')
    plt.title('Evolution of unemployment rate', )
    plt.show()
    

    plt.plot(data['GINI_income_pre'], color = 'red', label = r'GINI income pre')
    plt.plot(data['GINI_income_post'], color = 'blue', label = r'GINI income post')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Income Gini Coefficient')
    plt.title('Evolution of income gini coefficient', )
    plt.show()
    
    plt.plot(data['GINI_wealth_pre'], color = 'red', label = r'GINI wealth pre')
    plt.plot(data['GINI_wealth_post'], color = 'blue', label = r'GINI wealth post')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Wealth Gini Coefficient')
    plt.title('Evolution of wealth gini coefficient', )
    plt.show()
    
    plt.plot(data['C_BR_loan'], color = 'blue', label = r'Cfirm BR loan')
    plt.plot(data['C_BR_wage'], color = 'green', label = r'Cfirm BR wage')
    plt.plot(data['K_BR_loan'], color = 'red', label = r'Kfirm BR loan')
    plt.plot(data['K_BR_wage'], color = 'purple', label = r'Kfirm BR wage')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Number of bankruptcies')
    plt.title('Evolution of firm bankruptcies', )
    plt.show()
    
    plt.plot(data['Total Wealth'], label = r'Total Wealth')
    plt.plot(data['Total Wealth Laissez Faire'], label = r'Total Wealth Laissez Faire')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Total Wealth')
    plt.title('Evolution of total household wealth', )
    plt.show()
    
    plt.plot(data['Available_deposits'], label = r'Available deposits')
    plt.plot(data['Y_cap_nominal'], label = r'Nominal capital output')
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Monetary unit')
    plt.title('Evolution of available deposits', )
    plt.show()