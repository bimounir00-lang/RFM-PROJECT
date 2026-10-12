from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
data = pd.read_csv(Path(__file__).parent/'train.csv')

print(data.head())
print(data.info())
print(data.isnull().sum())

data['Order Date'] = pd.to_datetime(data['Order Date'].str.strip(), dayfirst=True)
data['Ship Date'] = pd.to_datetime(data['Ship Date'].str.strip(), dayfirst=True)
data = data.drop(columns=['Postal Code'])
print(data['Sales'].sum())

top_products = data.groupby('Product Name')['Sales'].sum().sort_values(ascending=False)
print(top_products.head(5))
top_cities = data.groupby('City')['Sales'].sum().sort_values(ascending=False)
print(top_cities.head(5))

top_months = data.groupby(data['Order Date'].dt.strftime('%Y-%m'))['Sales'].sum().sort_values(ascending=False)
print(top_months.head(5))
order_total = data.groupby('Order ID')['Sales'].sum()
print(order_total.mean())

snapshot  = data['Order Date'].max() + pd.Timedelta(days=1)
rfm = data.groupby('Customer ID').agg(
    recency = ('Order Date', lambda x : (snapshot - x.max()).days),
    frequency = ('Order ID', 'nunique'),
    monetary = ('Sales', 'sum')
)
rfm['R'] = pd.qcut(rfm['recency'], 4, labels=[4,3,2,1])
rfm['F'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1,2,3,4])
rfm['M'] = pd.qcut(rfm['monetary'], 4, labels=[1,2,3,4])

rfm['score'] = rfm[['R','F','M']].astype(int).sum(axis=1)
rfm['segments'] = pd.cut(rfm['score'], bins=[0,4,7,9,12], labels=['AT RISK','REGULAR','LOYAL','VIP'])

print(rfm['segments'].value_counts())
most_valuable_customers = rfm.groupby('segments')['monetary'].sum()
print(most_valuable_customers.sort_values(ascending=False))

rfm['segments'].value_counts().plot(kind = "bar", title = "Customer Segmentation (RFM Analysis)", xlabel = "Customer Segment",ylabel = "Number of Customers")
plt.savefig("Segments.png")
plt.show()
monthly_sales = data.groupby(data['Order Date'].dt.to_period('M'))['Sales'].sum().sort_index()
monthly_sales.plot(kind = 'line', title = "Monthly Sales Trend",marker = "o", xlabel = "Month", ylabel = "Total Sales" )
plt.savefig("Monthly_Sales.png")
plt.show()
data["order_month"] = data["Order Date"].dt.to_period("M")
data['cohort_Month'] = data.groupby('Customer ID')["order_month"].transform('min')
data['cohort_Index'] = (data["order_month"].dt.year - data['cohort_Month'].dt.year) * 12 + data["order_month"].dt.month - data['cohort_Month'].dt.month
cohort_data = data.groupby(['cohort_Month','cohort_Index'])['Customer ID'].nunique()
cohort_table = cohort_data.unstack()
print(cohort_table)
cohort_sizes = cohort_table.iloc[:,0]
retention = cohort_table.divide(cohort_sizes,axis = 0)*100
print(retention.round(1))

plt.figure(figsize = (12, 8))
sns.heatmap(
    retention.iloc[:, :12],
    annot = True,
    fmt = ".0f",
    cmap ="Blues",
    vmin = 0,
    vmax = 30,
)
plt.title("Customer Retention by Cohort(%)")
plt.xlabel("Months Since First Purchase")
plt.ylabel("Cohort Month")
plt.tight_layout()
plt.savefig("retention_heatmap.png")
plt.show()

monthly_retention  = retention.mean()
monthly_retention.plot(
    kind = "line",
    marker = "o",
    title = "Average Customer Retention",
)
plt.xlabel("Months Since First Purchase")
plt.ylabel("Average Retention (%)")
plt.grid(True)
plt.tight_layout()
plt.savefig("average_retention.png")
plt.show()