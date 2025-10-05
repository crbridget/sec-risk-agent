import requests
import pandas as pd
import matplotlib.pyplot as plt


url = "	https://www.fema.gov/api/open/v2/HazardMitigationGrantProgramDisasterSummaries"

response = requests.get(url)
data = response.json()

summaries = data["DisasterDeclarationsSummaries"]

df = pd.DataFrame(summaries)
df.to_csv("fema_disasters.csv", index=False)

print(df.info())

df = df[["disasterNumber","state", "incidentType", "declarationDate"]]
print(df.info())

counts = df.groupby("state")["disasterNumber"].count().sort_values(ascending=False)
print(counts.head())

counts.head(10).plot(kind="bar")
plt.title("Top 10 States by Number of Disasters in FEMA Dataset")
plt.xlabel("State")
plt.ylabel("Number of Disasters")
plt.show()