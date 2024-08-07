#!python3
import matplotlib.pyplot as plt
import matplotlib.dates as md
from datetime import date, timedelta

# Exchange names (replace with desired names)
exchanges = ['Coinbase', 'Kraken', 'Gemini', 'Bitstamp']

# Estimated relative volumes (replace with actual data or ratios)

volumes = [13308,13150,7952,6072]  # Sample data (adjust based on your estimates)

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



# Sample data (replace with your actual sequences)
portfolio_value_sequence = [66185.33, 69139.70, 71665.83, 73452.17, 74308.95, 73458.86, 73409.40, 72135.90, 71679.54, 69855.50,
                            69703.63, 70150.18, 72300.46, 70912.60, 73691.11, 73793.13, 73984.54, 73937.18, 73836.00, 74282.30,
                            74493.28, 74693.19, 73417.11, 73561.85, 74164.44]

one_bitcoin_sequence = [57273.48, 59139.29, 61787.18, 63412.84, 64280.10, 63583.90, 63799.00, 62549.90, 62144.40, 60839.90,
                        60701.90, 61102.60, 63100.00, 61895.90, 64834.00, 65718.00, 67183.00, 66956.90, 66894.90, 67599.80,
                        69871.97, 70427.45, 68060.84, 68172.88, 68969.10]
f = one_bitcoin_sequence[0] / portfolio_value_sequence[0]
greedy_bot_sequence = [num * f for num in portfolio_value_sequence]

half_cash = one_bitcoin_sequence[0] / 2
combined_sequence = [(num / 2) + half_cash for num in one_bitcoin_sequence]
#[a / 2 + b / 2 for a, b in zip(greedy_bot_sequence, one_bitcoin_sequence)]

# Define labels for the sequences and plot title
one_bitcoin = "One Bitcoin"
greedy_bot_portfolio = "Greedy Bot Portfolio (scaled)"
plot_title = "May 2024"

# Set starting date and create a list of dates for the x-axis
start_date = date(2024, 5, 1)
num_days = len(greedy_bot_sequence)
dates = [start_date + timedelta(days=i) for i in range(num_days)]

# Create the plot
fig, ax = plt.subplots(figsize=(8, 5))  # Set the figure size (optional)

# Plot the sequences with dates on the x-axis
plt.plot(dates, greedy_bot_sequence, label=greedy_bot_portfolio)
plt.plot(dates, one_bitcoin_sequence, label=one_bitcoin)
plt.plot(dates, combined_sequence, label='Half Cash / Half Bitcoin')

# Format the x-axis labels as dates (optional)
ax.xaxis.set_major_formatter(md.DateFormatter('%b %d'))
ax.xaxis.set_major_locator(md.DayLocator())

plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

# Add labels and title
plt.xlabel("Date")
plt.ylabel("Estimated Value (USD)")
plt.title(plot_title)

# Add legend
plt.legend()

# Save the plot as an image file
image_filename = "daily_plot.png"  # Replace with your desired filename
plt.savefig(image_filename)

print(f"Image saved to: {image_filename}")
