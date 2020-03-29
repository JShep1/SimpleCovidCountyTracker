import csv
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

class Date:
    def __init__(self, day, month, year):
        self.day = day
        self.month = month
        self.year = year

def DaysBetween(first, second):
    days_in_month = np.array([31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    day_mapping = {}
    day_count = 0
    if (days_in_month[second.month-1] == second.day):
        if (second.month == 12):
            second.month = 1
        else:
            second.month += 1
        second.day = 1
    else:
        second.day += 1
    while (not (first.day == second.day and first.month == second.month and first.year == second.year)):
        day_count += 1
        first_day_str = str(first.day)
        first_month_str = str(first.month)
        first_year_str = str(first.year)
        if (first.day < 10):
            first_day_str = '0' + first_day_str
        if (first.month < 10):
            first_month_str = '0' + first_month_str
        date_string = first_year_str + '-' + first_month_str + '-' + first_day_str
        day_mapping[date_string] = int(day_count)
        if (days_in_month[first.month-1] == first.day):
            if (first.month == 12):
                first.month = 1
            else:
                first.month += 1
            first.day = 1
        else:
            first.day += 1
    return day_count, day_mapping

county_names = np.array([])
state_names = np.array([])
while (True):
    county_name = input("Enter county: ")
    county_names = np.append(county_names, county_name)
    state_name = input("Enter state: ")
    state_names = np.append(state_names, state_name)
    another = input("Enter another? (y/n) or delete previous entry (d): ")
    if (another == "D" or another == "d"):
        continue
    elif (another == "n" or another == "N"):
        break

county_name = county_names[0]
state_name = state_names[0]

county_set = np.array([])
deaths = np.array([])

county_cases_dict = {}
county_dates_dict = {}

for i in range(len(county_names)):
    county_cases_dict[county_names[i] + state_names[i]] = []

with open('us-counties.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter='\n', quotechar='|')
    for row in reader:
        row_data = row[0].split(',')
        date = row_data[0]
        county = row_data[1]
        if (len(row_data) > 2):
            state = row_data[2]
        for i in range(len(county_names)):
            if (county == county_names[i] and state == state_names[i]):
                county_dates_dict.setdefault((county + state), []).append(row_data[0])
                county_cases_dict.setdefault((county + state), []).append(int(row_data[4]))

earliest_date = Date(32, 13, 3000)
latest_date = Date(0, 0, 0)

for i in range(len(county_names)):
    county = county_names[i]
    state = state_names[i]
    dates = county_dates_dict[county + state]
    for j in range(len(dates)):
        date = dates[j]
        date = date.split('-')
        year = int(date[0])
        month = int(date[1])
        day = int(date[2])
        if (year < earliest_date.year or
            (year == earliest_date.year and month < earliest_date.month) or
            (year == earliest_date.year and month == earliest_date.month and day < earliest_date.day)):
            earliest_date = Date(day, month, year)
        if (year > latest_date.year or
            (year == latest_date.year and month > latest_date.month) or
            (year == latest_date.year and month == latest_date.month and day > latest_date.day)):
            latest_date = Date(day, month, year)
day_count, day_mapping = DaysBetween(earliest_date, latest_date)
fig, ax = plt.subplots()
for i in range(len(county_names)):
    county = county_names[i]
    state = state_names[i]
    dates = county_dates_dict[county + state]
    cases = county_cases_dict[county + state]
    cases = np.array(cases)
    dates = np.array(dates)
    first_day = int(day_mapping[dates[0]])
    last_day = int(day_mapping[dates[len(dates)-1]])
    x = np.arange(first_day, last_day+1)
    y_pos = x
    new_cases = cases[:, np.newaxis]
    x = x[:, np.newaxis]

    polynomial_features = PolynomialFeatures(degree=4)
    x_poly = polynomial_features.fit_transform(x)
    model = LinearRegression()
    model.fit(x_poly, new_cases)
    y_poly_pred = model.predict(x_poly)

    plt.scatter(y_pos, cases, s=10)
    plt.plot(x, y_poly_pred, label=county)
    plt.ylabel('Cases')
all_dates = list(day_mapping.keys())
plt.xticks(np.arange(day_count), all_dates, rotation='vertical')
nrows = 5
ncols = 2
ax.legend(ncol=ncols, loc='best')
plt.title("Total COVID-19 Cases Per County")
plt.show()
