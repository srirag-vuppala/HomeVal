import pandas as pd
import numpy as np
import numpy_financial as npf #DOWNLOAD: pip3 install numpy-financial
import matplotlib.pyplot as plt
import seaborn as sns
import math
import requests
import json

def amortize(rate, amount, years, num_payments_per_year):
    """[Used to amortize loan into a table]

    Args:
        rate ([float])
        amount ([integer])
        years ([integer])
        num_payments_per_year ([integer])
    """
    # converted to -ve to symbolize the outflow 
    mortgage_amount = -amount 
    interest_rate = (rate / 100) / num_payments_per_year 
    periods = years*num_payments_per_year

    # create a range of timesteps 
    n_periods = np.arange(years * num_payments_per_year) + 1
    
    # Start building the actual columns for the table
    interest_monthly = npf.ipmt(interest_rate, n_periods, periods, mortgage_amount)
    principal_monthly = npf.ppmt(interest_rate, n_periods, periods, mortgage_amount)
    
    # merge data 
    df_initialize = list(zip(n_periods, interest_monthly, principal_monthly))
    df = pd.DataFrame(df_initialize, columns=['period','interest','principal'])
    
    # monthly mortgage_amount based payment 
    df['monthly_payment'] = df['interest'] + df['principal']
    
    # cumulative sum  
    df['balance'] = df['monthly_payment'].cumsum()
    
    # reverse values 
    df.balance = df.balance.values[::-1]
    return(df)

def home_value_calc(initial_home_value, growth_rate_per_year, years):
    """ Function assumes a linear growth model for each year and calculates the valuation
    of the home for each of those months """
    per_month = growth_rate_per_year/12
    per_month = per_month/100
    n_periods = np.arange(years * 12) + 1
    final_values = np.zeros(years * 12) 

    for month in range(years*12):
        if month == 0:
            final_values[month] = round(initial_home_value*(per_month+1), 2) 
        else:
            final_values[month] = round(final_values[month-1]*(per_month+1), 2)  
    df_init = list(zip(n_periods, final_values))
    df = pd.DataFrame(df_init, columns=['period', 'home value'])
    return df 

def main():
    # default value is 63000
    home_value = int(input("Enter in your home value(in $): ") or "630000")
    # default percent is 10
    down_payment = int(input("Enter in your percent of home value you've put towards your down payment: ") or "10") 
    down_payment = int((down_payment/100)*home_value)
    loan_amount = home_value - down_payment 
    years = 30
    num_payments_per_year = 12

    # Will need to find a way to get daily updates for interest rate
    interest_rate = 4.00

    scen1 = amortize(interest_rate, loan_amount, years, num_payments_per_year)
    hv1 = home_value_calc(home_value, 3, years)

    #Graph the scenario
    plt.figure(figsize=(15, 10))
    sns.lineplot(x='period', y='balance', data=scen1, color='red')
    sns.lineplot(x='period', y='home value', data=hv1, color='blue')

    plt.axhline(y=loan_amount, linestyle=":")

    plt.xlabel("Period")
    plt.ylabel("Outstanding Balance ($)")
    plt.subplots_adjust(top = 0.95)
    title = "$"+str(loan_amount)+" mortgage over "+str(years)+" years"
    plt.suptitle(title , x=0.12, horizontalalignment="left", fontsize=15)
    plt.figtext(0.92, 0.01, "by: srirag", horizontalalignment="right")
    label1 = str(interest_rate)+' Interest Rate'
    label2 = str(home_value)+' Home Value'
    plt.legend(labels=[label1, label2])
    plt.ticklabel_format(useOffset=False, style="plain")

    plt.show()

    # Requires a partnerId with zillow
    # r = requests.get('https://mortgageapi.zillow.com/getCurrentRates?partnerId=a&queries.1.propertyBucket.location.stateAbbreviation=WA&queries.1.propertyBucket.propertyValue=500000&queries.1.propertyBucket.loanAmount=400000')
    # print(r.json())
if __name__ == '__main__':
    main()