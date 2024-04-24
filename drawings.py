#!python3
import matplotlib.pyplot as plt

# Exchange names (replace with desired names)
exchanges = ['Coinbase', 'Kraken', 'Gemini', 'Bitstamp']

# Estimated relative volumes (replace with actual data or ratios)
volumes = [60, 40, 30, 20]  # Sample data (adjust based on your estimates)

# Create the pie chart
plt.figure(figsize=(8, 8))  # Adjust figure size as desired
plt.pie(volumes, labels=exchanges, autopct="%1.1f%%", startangle=140)
plt.title("Estimated Daily BTC Trading Volume Comparison")

# Equal aspect ratio ensures a circular pie chart
plt.axis('equal')

# Save the pie chart as a PNG image
plt.savefig("BTC_Exchange_Volumes.png")


# Initial investment amount
investment = 1000

# Interest rates
apr_1 = 0.01
apr_10 = 0.1

# Number of weeks (one year)
num_weeks = 52

# Calculate weekly growth factors
growth_factor_1 = 1 + apr_1 / 52
growth_factor_10 = 1 + apr_10 / 52

# Initialize lists to store weekly balances
balance_1 = [investment]  # List for 1% APR asset
balance_10 = [investment]  # List for 10% APR asset

# Calculate weekly balances for each asset
for _ in range(1, num_weeks):
    balance_1.append(balance_1[-1] * growth_factor_1)
    balance_10.append(balance_10[-1] * growth_factor_10)

# Create the line chart
plt.figure(figsize=(10, 6))
plt.plot(range(num_weeks), balance_1, label='1% APR')
plt.plot(range(num_weeks), balance_10, label='10% APR')

# Customize the chart
plt.xlabel('Weeks')
plt.ylabel('Balance')
plt.title('Asset Growth Comparison (Weekly)')
plt.legend()
plt.grid(True)

# Save the chart as a PNG image
plt.savefig("Asset_Growth_Comparison.png")
