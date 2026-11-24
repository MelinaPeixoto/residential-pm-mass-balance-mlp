"""Consolida as 1.000 réplicas seguindo o cálculo do notebook arquivado."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from retomar_mbb_1000 import namespace,OUT,cases

ns=namespace(); old=pd.read_csv(OUT/'tabelas'/'MBB_9casos_Finf_kprime_RMSE_Holm.csv');rows=[]
labels=[('Finf_MBM','Finf_MBM'),('Finf_MLP','Finf_MLP'),('kprime_MBM','kprime_MBM'),('kprime_MLP','kprime_MLP'),('delta_Finf','Finf_difference'),('RMSE_MBM','RMSE_MBM'),('RMSE_MLP','RMSE_MLP_mean_seeds'),('delta_RMSE','RMSE_difference')]
for res,frac,prot in cases:
 stem=f'{res}_{frac.replace(".","")}_{prot}';b=pd.read_csv(OUT/'replicas_mbb'/f'{stem}_paired.csv'); ids=b.rep.astype(int)
 if len(b)!=1000 or set(ids)!=set(range(1,1001)):raise ValueError(f'{stem}: réplicas incompletas/duplicadas')
 prior=old[(old.residence==res)&(old.fraction==frac)&(old.protocol==prot)]
 if len(prior)!=1:raise ValueError(f'{stem}: resumo original ausente')
 q=prior.iloc[0];base=b[b.rep<=600]
 for label,col in labels:
  s=ns['sample_summary'](base[col].values)
  for k,v in s.items():
   if not np.isclose(float(q[f'{label}_{k}']),float(v),rtol=1e-6,atol=1e-7):raise ValueError(f'{stem}: resumo inicial difere {label}_{k}')
 row={'residence':res,'fraction':frac,'protocol':prot,'Finf_MBM_original':q.Finf_MBM_original,'Finf_MLP_original':q.Finf_MLP_original,'delta_original':q.delta_original,'delta_k_original':q.delta_k_original}
 test=ns['centered_bootstrap_test'](b.Finf_difference.to_numpy(),q.delta_original); kt=ns['centered_bootstrap_test']((b.kprime_MBM-b.kprime_MLP).to_numpy(),q.delta_k_original)
 row.update(test);row.update({'k_'+k:v for k,v in kt.items()})
 for label,col in labels:
  row.update({f'{label}_{k}':v for k,v in ns['sample_summary'](b[col].values).items()})
 rows.append(row)
df=pd.DataFrame(rows)
for prot in df.protocol.unique():
 m=df.protocol.eq(prot)
 for col,name in [('p_bootstrap','p_holm_9'),('k_p_bootstrap','k_p_holm_9'),('MC_p_upper95','MC_p_upper_holm'),('k_MC_p_upper95','k_MC_p_upper_holm')]:df.loc[m,name]=ns['holm_adjust'](df.loc[m,col].values)
df['conclusao_MC']=np.where(df.MC_p_upper_holm<.05,'detecção estável ao limite MC',np.where(df.p_holm_9<.05,'nominal; precisão MC insuficiente','não detectado'))
df['conclusao_k_MC']=np.where(df.k_MC_p_upper_holm<.05,'detecção estável ao limite MC',np.where(df.k_p_holm_9<.05,'nominal; precisão MC insuficiente','não detectado'))
out=Path('substituicoes_artigo/tabelas');out.mkdir(parents=True,exist_ok=True)
df.to_csv(out/'Tabela03_bootstrap_Finf_kprime_1000.csv',index=False)
cols=['residence','fraction','Finf_MBM_original','Finf_MBM_SD','Finf_MBM_CI95_lower','Finf_MBM_CI95_upper','Finf_MLP_original','Finf_MLP_SD','Finf_MLP_CI95_lower','Finf_MLP_CI95_upper','delta_original','p_holm_9']
df[cols].to_csv(out/'Tabela03_Finf_artigo_1000.csv',index=False)
print('CONSOLIDADO',len(df),'casos; todos com 1000 réplicas. Primeiras 600 verificadas.',flush=True)
