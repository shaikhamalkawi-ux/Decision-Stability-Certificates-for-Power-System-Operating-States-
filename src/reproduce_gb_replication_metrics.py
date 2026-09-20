#!/usr/bin/env python3
"""Recompute DSC-Grid GB internal-generation metrics from returned PyPSA-GB dispatch tables."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

ROOT=Path(__file__).resolve().parents[1]/"results"/"gb_replication"
jan=pd.read_csv(ROOT/"january_generator_dispatch.csv",index_col=0)
jul=pd.read_csv(ROOT/"july_generator_dispatch.csv",index_col=0)
jm=pd.read_csv(ROOT/"january_generator_metadata.csv")
um=pd.read_csv(ROOT/"july_generator_metadata.csv")
carrier={}
for df in (jm,um):
    carrier.update(dict(zip(df["name"],df["carrier"])))
common=list(jan.columns.intersection(jul.columns))
cols=[c for c in common if carrier.get(c)!="EU_import"]

def metric(A_df,B_df):
    A=A_df.to_numpy(float); B=B_df.to_numpy(float)
    M=float(np.abs(B.mean(0)-A.mean(0)).sum())
    C=np.empty((len(A),len(B)))
    for i in range(len(A)):
        C[i]=np.abs(B-A[i]).sum(1)
    r,c=linear_sum_assignment(C)
    W=float(C[r,c].mean())
    return M,W,W-M,(W-M)/W

M,W,G,s=metric(jan[cols],jul[cols])
ta=pd.to_datetime(jan.index); tb=pd.to_datetime(jul.index)
total=0.0
for h in range(24):
    ia=np.flatnonzero(ta.hour==h); ib=np.flatnonzero(tb.hour==h)
    A=jan.iloc[ia][cols].to_numpy(float); B=jul.iloc[ib][cols].to_numpy(float)
    C=np.empty((len(A),len(B)))
    for i in range(len(A)):
        C[i]=np.abs(B-A[i]).sum(1)
    r,c=linear_sum_assignment(C); total+=float(C[r,c].sum())
Wh=total/len(jan)
print(json.dumps({"n":len(cols),"M":M,"W1":W,"G_shape":G,"shape_share":s,
                  "W1_hour_conditioned":Wh,"hour_premium":Wh-W},indent=2))
