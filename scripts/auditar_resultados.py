"""Confere dados locais, 1000 réplicas e tabela de desempenho agregada."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'resultados_3_sementes_600_MBB'
TABLE=ROOT/'resultados'/'tabelas'/'Tabela06_metricas_teste_protocolo_B.csv'

def main():
    if not SOURCE.is_dir():
        raise FileNotFoundError('Dados locais ausentes: execute preparar_dados_locais.py com o checkpoint autorizado.')
    df=pd.read_csv(SOURCE/'tabelas'/'previsoes_todas.csv')
    df=df[(df.protocol=='B')&(df.period=='test')].copy()
    groups=['residence','fraction','row_index']
    if not df.groupby(groups).seed.nunique().eq(3).all():
        raise AssertionError('Há observações sem três sementes distintas.')
    if not df.groupby(groups).C_observed_corrected.nunique(dropna=False).eq(1).all():
        raise AssertionError('A referência difere entre as sementes.')
    if not df.groupby(groups).MBM.nunique(dropna=False).eq(1).all():
        raise AssertionError('As previsões MBM diferem entre as sementes.')
    points=df.groupby(groups,as_index=False).agg(y=('C_observed_corrected','first'),mbm=('MBM','first'),hybrid=('MBM_MLP','mean'))
    result=pd.read_csv(TABLE)
    if len(result)!=18 or result.duplicated(['residence','fraction','model']).any():
        raise AssertionError('Tabela de desempenho não contém 18 linhas únicas.')
    checked=0
    for (r,f),g in points.groupby(['residence','fraction']):
        for col,model in [('mbm','MBM'),('hybrid','MBM+MLP')]:
            row=result[(result.residence==r)&(result.fraction==f)&(result.model==model)]
            if len(row)!=1: raise AssertionError(f'Linha ausente: {r}/{f}/{model}')
            y=g.y.to_numpy();p=g[col].to_numpy();rmse=np.sqrt(np.mean((p-y)**2));mae=np.mean(np.abs(p-y));r2=1-np.sum((y-p)**2)/np.sum((y-y.mean())**2);nrmse=100*rmse/np.ptp(y)
            for k,value in [('RMSE',rmse),('MAE',mae),('R2',r2),('NRMSE_range_percent',nrmse)]:
                if not np.isclose(float(row.iloc[0][k]),value,rtol=1e-10,atol=1e-10):raise AssertionError(f'Diferença {r}/{f}/{model}: {k}')
            checked+=1
    if checked!=18:raise AssertionError(f'Esperadas 18 linhas; verificadas {checked}.')
    for r in ('R5','R6','R7'):
        for f in ('PM1','PM25','PM10'):
            path=SOURCE/'replicas_mbb'/f'{r}_{f}_B_paired.csv';b=pd.read_csv(path)
            if len(b)!=1000 or set(b.rep.astype(int))!=set(range(1,1001)):
                raise AssertionError(f'Réplicas inválidas: {path.name}')
    print('OK: 18 linhas de desempenho reproduzidas e 9 conjuntos de 1000 réplicas verificados.')
    print('Esta conferência não é uma nova validação independente do estudo.')

if __name__=='__main__':main()
