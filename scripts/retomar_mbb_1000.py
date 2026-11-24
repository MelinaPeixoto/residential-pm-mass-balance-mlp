"""Retoma réplicas do notebook arquivado, utilizando dados processados salvos."""
import ast, json, os, sys, time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent
os.chdir(ROOT)
NOTEBOOK=ROOT/'notebooks'/'Pipeline_R5_R7_3_sementes_600_MBB.ipynb'
OUT=ROOT/'resultados_3_sementes_600_MBB'
cases=[(r,f,'B') for r in ('R5','R6','R7') for f in ('PM1','PM2.5','PM10')]

def namespace():
    n=json.loads(NOTEBOOK.read_text()); ns={'__name__':'__main__'}
    # Configuração original; sem executar as células de treinamento e exportação.
    exec(compile(''.join(n['cells'][4]['source']),str(NOTEBOOK),'exec'),ns)
    ns['CFG'].n_mbb=1000
    for cell in (8,12):
        tree=ast.parse(''.join(n['cells'][cell]['source']))
        tree.body=[x for x in tree.body if isinstance(x,(ast.FunctionDef,ast.ClassDef))]
        exec(compile(tree,str(NOTEBOOK),'exec'),ns)
    return ns

def inputs(res,frac,protocol,ns):
    stem=f'{res}_{frac.replace(".","")}_{protocol}'
    data=pd.read_csv(OUT/'dados_processados'/f'{res}_{frac.replace(".","")}.csv')
    conf=json.loads((OUT/'optuna'/f'{stem}_selected.json').read_text())
    ex=ns['make_examples'](data,conf['features'])
    dev=ns['subset'](ex,('train','validation'));te=ns['subset'](ex,('test',))
    return stem,data,conf,ex,dev,te

def verify(case):
    res,frac,prot=case;ns=namespace();stem,_,conf,ex,dev,te=inputs(*case,ns)
    path=OUT/'replicas_mbb'/f'{stem}_paired.csv';d=pd.read_csv(path)
    ids=d['rep'].astype(int).tolist()
    if len(ids)!=len(set(ids)) or not set(range(1,601)).issubset(ids): raise RuntimeError(f'{stem}: as 600 réplicas iniciais não conferem')
    for rep in (1,):
        old=d.loc[d.rep==rep].iloc[0];new=ns['_one_bootstrap'](ex,res,frac,prot,conf,rep,1000,te,dev,path)
        fields=('Finf_MBM','kprime_MBM','Finf_MLP','kprime_MLP','RMSE_MBM','RMSE_MLP_ensemble','RMSE_MLP_mean_seeds','Finf_difference','RMSE_difference')
        errors={k:abs(float(old[k])-float(new[k])) for k in fields}
        print('VERIFICADO',stem,'max_abs',max(errors.values()),flush=True)
        if any(not np.isclose(float(old[k]),float(new[k]),rtol=1e-5,atol=1e-6) for k in fields):raise RuntimeError(f'{stem}: reprodução divergente: {errors}')
    return stem

def run(case):
    ns=namespace();stem,data,conf,ex,dev,te=inputs(*case,ns)
    path=OUT/'replicas_mbb'/f'{stem}_paired.csv';d=pd.read_csv(path);records=d.to_dict('records');done=set(d.rep.astype(int))
    if not set(range(1,601)).issubset(done) or len(done)!=len(records):raise RuntimeError(f'{stem}: checkpoint inválido')
    start=time.monotonic()
    for rep in range(601,1001):
        if rep in done:continue
        records.append(ns['_one_bootstrap'](ex,*case,conf,rep,1000,te,dev,path));done.add(rep)
        if rep%10==0 or rep==1000:
            tmp=path.with_suffix('.tmp');pd.DataFrame(records).sort_values('rep').to_csv(tmp,index=False);os.replace(tmp,path)
            print('PROGRESSO',stem,rep,'segundos',round(time.monotonic()-start,1),flush=True)
    print('CONCLUIDO',stem,len(done),flush=True)
    return stem

if __name__=='__main__':
    job=sys.argv[1] if len(sys.argv)>1 else 'verify'
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(verify if job=='verify' else run,c) for c in cases]
        for f in as_completed(futures):print('RESULTADO',f.result(),flush=True)
