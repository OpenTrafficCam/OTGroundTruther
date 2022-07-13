# %%
import pandas as pd


class current_count:
    counter = 0

    def __init__(self):
        type(self).counter += 1

        # Attributes
        self.ID = type(self).counter
        self.Vhc_class = None
        self.Entry_Gate = None
        self.Entry_Frame = None
        self.Exit_Gate = None
        self.Exit_Frame = None
        print("Anzahl der Instanzen: " + str(current_count.counter))

    def get_vehicle_information(self):

        return {
            "ID": self.ID,
            "Class": self.Vhc_class,
            "Entry_Gate": self.Entry_Gate,
            "Entry_Frame": self.Entry_Frame,
            "Exit_Gate": self.Exit_Gate,
            "Exit_Frame": self.Exit_Frame,
        }


# %%
vehicle1 = current_count()
vehicle2 = current_count()

# %%
print(vehicle1.ID)
# %%
# information = vehicle1.vehicle_information
print(vehicle1.get_vehicle_information())

# %%
df = pd.DataFrame()
print(df)
print(type(df))
df = df.append(vehicle1.get_vehicle_information(), ignore_index=True)


print(df)
# %%
