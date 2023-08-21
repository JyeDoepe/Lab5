import pandas as pd
import numpy as np
import warnings

pd.options.mode.chained_assignment = None

class Part1:
    def __init__(self):
        # Read in Property Tables
        corrected_resistance = pd.read_csv('data/CorrectedResistence.csv')
        corrected_resistance = self.values2Float(corrected_resistance)
        
        temperature = pd.read_csv('data/Temperature.csv')
        temperature = self.values2Float(temperature)


        saturation_properties = pd.read_csv('data/SaturationPoints.csv')
        saturation_properties = saturation_properties.dropna()
        enthalpy = pd.read_csv('data/Enthalpy.csv')
        enthalpy = enthalpy[enthalpy['T ( C )'].notna()]
        saturation_water = pd.read_csv('data/SaturationWater.csv')
        saturation_water = saturation_water[saturation_water['T'].notna()]
        saturation_water = saturation_water[['T', 'P', 'v_f', 'v_g']]
        super_heated = pd.read_csv('data/SuperHeated.csv')
        super_heated = super_heated[super_heated['T'].notna()]
        super_heated = super_heated[['T', 'Volume']]

        cols = list(enthalpy.columns)
        coln = 0
        for col in enthalpy.columns:
            if col != 'T ( C )':
                cols[coln] = enthalpy[col][28]
            coln += 1
        enthalpy.columns = cols
        enthalpy = enthalpy.drop(28)
        enthalpy = self.values2Float(enthalpy)
        
        # Read in data
        data = pd.read_csv('data/data.csv')
        data['P1'] = data['P1'] 
        data = data.drop(columns=['Unnamed: 4'])
        data['hgf'] = np.nan
        for index, row in data.iterrows():
            # calculate R1C
            R1 = row['R1']
            data['R1c'][index] = self.getMidPoint(corrected_resistance, R1, 'Res', 'Cor Res')
            # calculate T1
            data['T1'][index] = self.getMidPoint(temperature, data['R1c'][index], 'Cor Res', 'Temp ( C )')
            # calculate R2C
            R2 = row['R2']
            data['Rc2'][index] = self.getMidPoint(corrected_resistance, R2, 'Res', 'Cor Res')
            # calculate T2
            data['T2'][index] = self.getMidPoint(temperature, data['Rc2'][index], 'Cor Res', 'Temp ( C )')
            # calculate Hf
            data['hf'][index] = self.getMidPoint(saturation_properties, data['T1'][index], 'T ( C )', 'h_f')
            # calculate Hg
            data['hg'][index] = self.getMidPoint(saturation_properties, data['T1'][index], 'T ( C )', 'h_g')
            # calculate Hfg
            data['hgf'][index] = self.getMidPoint(saturation_properties, data['T1'][index], 'T ( C )', 'h_gf')
            # calculate h
            data['h2'][index] = self.findH(enthalpy, data['T1'][index], data['P1'][index])
            # calculate x
            data['x'][index] = (data['h2'][index] - data['hf'][index]) / data['hgf'][index]

        print(data)



    def getMidPoint(self, df, value, col, col2):
        greaterThen = df[(df[col] >= value)]
        id = greaterThen[col].idxmin()
        if value == df[col][id]:
            return df[col2][id]
        if value == df[col][id-1]:
            return df[col2][id-1]
        val = (df[col2][id] + df[col2][id-1])/2
        return val

    def values2Float(self, df):
        for col in df.columns:
            df[col] = df[col].astype(float)
        return df
        
    def findH(self, enthalpy, T, P):
        newRow = pd.DataFrame([{'T ( C )': T}])
        enthalpy = pd.concat([enthalpy, newRow], ignore_index=True)
        enthalpy = enthalpy.sort_values(by='T ( C )')
        enthalpy = enthalpy.sort_values(by='T ( C )', ascending=False)
        enthalpy = enthalpy.interpolate()
        enthalpy = enthalpy.sort_values(by='T ( C )')
        # enthalpy = enthalpy.reset_index()

        
        for col in enthalpy.columns:
            if col == 'T ( C )':
                pass
            elif np.float64(col) >= P:
                break
            col1 = col
        if P == col1 or P == col:
            row = enthalpy[enthalpy['T ( C )'] == T]
            row = row.reset_index()
            outP = row[col1][0]


        elif P < 90:
            row = enthalpy[enthalpy['T ( C )'] == T]
            row = row.reset_index()
            outP = row[90][0]
            print(row)
        else:
            print('New')
            row = enthalpy[enthalpy['T ( C )'] == T]
            row = row.reset_index()
            P1 = row[col1][0]
            P2 = row[col][0]
            x = col - col1
            y = P - col1
            ra = y/x
            outP = (P2 - P1) * ra + P1
            print(f'{P1} < {outP} < {P2}')
        return outP
        # print(col)
        # print(col1)
        # print(P)
        # print(enthalpy)

