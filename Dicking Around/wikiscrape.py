import re
import pandas as pd
import csv

tables = pd.read_html("https://en.wikipedia.org/wiki/List_of_Solar_System_objects_by_size")

massFromPandas = tables[1].iloc[:, 6].to_list()
namesFromPandas = tables[1].iloc[:, 0].to_list()
print(namesFromPandas)
mass=[]
names=[]

for massEntry, nameEntry in zip([str(x) for x in massFromPandas], namesFromPandas):
    if re.search(r'\d', massEntry):
        massEntry = massEntry.split("[")[0].split("±")[0]
        massEntry = re.sub("[^\d\.]", "", massEntry)
    else:
        massEntry = 0
    massEntry = float(massEntry)
    if massEntry != 0:
        mass.append(float(massEntry))
        names.append(nameEntry)

output = tuple(zip(names, mass))
print(*output, sep="\n" )

cols = ["Moon", "Mass (10^21 kg)"]
with open("moonMass.csv", "w") as file:
    write = csv.writer(file)
    write.writerow(cols)
    write.writerows(output)
