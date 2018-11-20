# imports
from codecademySQL import sql_query
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency

# examination of visits
print(sql_query('''
SELECT *
FROM visits
LIMIT 5
'''))

# examination of fitness_tests
print(sql_query('''
SELECT *
FROM fitness_tests
LIMIT 5
'''))

# examination of applications
print(sql_query('''
SELECT *
FROM applications
LIMIT 5
'''))

# examination of purchases
print(sql_query('''
SELECT *
FROM purchases
LIMIT 5
'''))

# Creation of a dataframe with all the necessary information

df = sql_query('''
SELECT visits.first_name,
    visits.last_name,
    visits.gender,
    visits.email,
    visits.visit_date,
    fitness_tests.fitness_test_date,
    applications.application_date,
    purchases.purchase_date
FROM visits
LEFT JOIN purchases
    ON visits.first_name = purchases.first_name
    AND visits.last_name = purchases.last_name
    AND visits.email = purchases.email
LEFT JOIN applications
    ON visits.first_name = applications.first_name
    AND visits.last_name = applications.last_name
    AND visits.email = applications.email
LEFT JOIN fitness_tests
    ON visits.first_name = fitness_tests.first_name
    AND visits.last_name = fitness_tests.last_name
    AND visits.email = fitness_tests.email
WHERE visits.visit_date >= '7-1-17'
''')

# Add a new column for test group

df['ab_test_group'] = df.fitness_test_date.apply\
    (lambda x: 'A' if pd.notnull(x) else 'B')

# Grouping the values by test group

ab_counts = df.groupby('ab_test_group').first_name.count().reset_index()
print(ab_counts)

# Creating a pie chart for the test groups + saving of the pie chart

plt.pie(ab_counts.first_name.values, labels = ['A', 'B'], autopct = '%0.2f%%')
plt.axis('equal')
plt.show()
plt.savefig('ab_test_pie_chart.png')

# Add a new column for application

df['is_application'] = df.application_date.apply(lambda x: 'Application' if pd.notnull(x) else 'No Application')

# Count the number of people with an application per group

app_counts = df.groupby(['is_application', 'ab_test_group']).first_name.count().reset_index()
print(app_counts)

# Create a pivot table containing whether someone signs up per test group

app_pivot = app_counts.pivot(
    columns = 'is_application',
    index = 'ab_test_group',
    values = 'first_name'
).reset_index()

# Add new columns to the pivot table (total and percentage applications per group)

app_pivot['Total'] = app_pivot['No Application'] + app_pivot['Application']
app_pivot['Percent with Application'] = app_pivot['Application']/app_pivot['Total']
print(app_pivot)

# Test if the difference in signup is significant

adjusted_pivot = [[250, 2254],[325, 2175]]
chi2, pval, dof, expected = chi2_contingency(adjusted_pivot)
print(pval)

# Adding a column if someone is a member

df['is_member'] = df.purchase_date.apply(lambda x: 'Member' if pd.notnull(x) else 'Not Member')

# Create a DataFrame that contains only people who picked up an application.

just_apps = df[df.is_application == 'Application']

# Amount of people in just_apps and no members from each group.

member_count = just_apps.groupby(['ab_test_group', 'is_member']).first_name.count().reset_index()
member_pivot = member_count.pivot(columns='is_member', index='ab_test_group', values='first_name').reset_index()

member_pivot['Total'] = member_pivot.Member + member_pivot['Not Member']
member_pivot['Percent Purchase'] = member_pivot.Member / member_pivot.Total
print(member_pivot)

# Test if the difference is significant

member_pivot_test = [[200, 50], [250, 75]]
chi2, pval, dof, expected = chi2_contingency(member_pivot_test)
print(pval)

# percentage of all visitors who purchased memberships pivot table

final_member_count = df.groupby(['ab_test_group', 'is_member']).first_name.count().reset_index()
final_member_pivot = final_member_count.pivot(columns='is_member', index='ab_test_group', values='first_name').reset_index()

final_member_pivot['Total'] = final_member_pivot.Member + final_member_pivot['Not Member']
final_member_pivot['Percent Purchase'] = final_member_pivot.Member / final_member_pivot.Total
print(final_member_pivot)

# check if the difference is significant

final_difference = [[200, 2304], [250, 2250]]
chi2, pval, dof, expected = chi2_contingency(final_difference)
print(pval)

# visualize
    # percent applications
ax = plt.subplot()
plt.bar(range(len(app_pivot)), app_pivot['Percent with Application'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'])
plt.show()
plt.savefig('percent_visitors_apply.png')

    # percent purchase
ax = plt.subplot()
plt.bar(range(len(member_pivot)), member_pivot['Percent Purchase'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
ax.set_yticklabels(['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'])
plt.show()
plt.savefig('percent_apply_purchase.png')

    # visitors who purchase percentage
ax = plt.subplot()
plt.bar(range(len(final_member_pivot)), final_member_pivot['Percent Purchase'].values)
ax.set_xticks(range(len(app_pivot)))
ax.set_xticklabels(['Fitness Test', 'No Fitness Test'])
ax.set_yticks([0, 0.05, 0.10, 0.15, 0.20])
ax.set_yticklabels(['0%', '5%', '10%', '15%', '20%'])
plt.show()
plt.savefig('percent_visitors_purchase.png')
