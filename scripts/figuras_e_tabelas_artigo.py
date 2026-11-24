"""Figuras reproduzíveis a partir das previsões arquivadas das três sementes."""
from pathlib import Path
import json,os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT=Path(__file__).resolve().parent.parent;IN=ROOT/'resultados_3_sementes_600_MBB';OUT=ROOT/'substituicoes_artigo';FIG=OUT/'figuras';TAB=OUT/'tabelas'
FIG.mkdir(parents=True,exist_ok=True);TAB.mkdir(parents=True,exist_ok=True)
R=('R5','R6','R7');F=('PM1','PM2.5','PM10');pretty={'PM1':r'PM$_1$','PM2.5':r'PM$_{2.5}$','PM10':r'PM$_{10}$'}
BLUE='#176bb2';GREEN='#16935c';ORANGE='#e17d22';BLACK='#222222'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':9,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7})
raw=pd.read_csv(IN/'tabelas/previsoes_todas.csv');raw=raw[raw.protocol.eq('B')].copy()
keys=['residence','fraction','period','row_index']
d=raw.groupby(keys,as_index=False).agg(observed=('C_observed_corrected','first'),mbm=('MBM','first'),hybrid=('MBM_MLP','mean'),finf=('Finf_MLP','mean'),finf_sd=('Finf_MLP','std'),finf_mbm=('Finf_MBM','first'),n_seeds=('seed','nunique'))
assert d.n_seeds.eq(3).all()
assert not d[['observed','mbm','hybrid','finf']].isna().any().any()
frames=[]
for r in R:
 for f in F:
  src=pd.read_csv(IN/'dados_processados'/f'{r}_{f.replace(".","")}.csv',usecols=['row_index','timestamp']);src['residence']=r;src['fraction']=f;frames.append(src)
d=d.merge(pd.concat(frames),on=['residence','fraction','row_index'],how='left',validate='many_to_one');d['timestamp']=pd.to_datetime(d.timestamp)
def outfig(fig,name):
 only=os.environ.get('ONLY_FIGS','')
 if only and not any(name.startswith(prefix) for prefix in only.split(',')):
  plt.close(fig);return
 fig.savefig(FIG/(name+'.png'),dpi=1000,bbox_inches='tight',facecolor='white');fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight',facecolor='white');plt.close(fig);print('FIGURA',name,flush=True)
def panels():return plt.subplots(3,3,figsize=(8.1,6.2),squeeze=False)
def axes_label(ax,i,j):
 if i==2:ax.set_xlabel('Observation index')
 if j==0:ax.set_ylabel(r'Concentration ($\mu$g m$^{-3}$)')
def r2(y,p):return 1-np.sum((y-p)**2)/np.sum((y-np.mean(y))**2)

# Figura 2 foi rotulada como treinamento no artigo, embora os índices sejam de teste.
for period in ('train','test'):
 fig,axes=panels()
 for i,r in enumerate(R):
  for j,f in enumerate(F):
   a=axes[i,j];g=d[(d.residence==r)&(d.fraction==f)&(d.period==period)].sort_values('row_index');x=g.row_index.to_numpy();y=g.finf.to_numpy();sd=g.finf_sd.fillna(0).to_numpy()
   a.plot(x,g.finf_mbm,color=BLUE,ls='--',lw=1);a.fill_between(x,y-sd,y+sd,color=GREEN,alpha=.17);a.plot(x,y,color=GREEN,lw=1);a.set_title(f'{r} / {pretty[f]}')
   if i==2:a.set_xlabel('Observation index')
   if j==0:a.set_ylabel(r'$F_{inf}$')
 fig.legend([Line2D([0],[0],color=BLUE,ls='--'),Line2D([0],[0],color=GREEN),Patch(color=GREEN,alpha=.17)],['MBM','MBM + MLP','±1 SD across seeds'],loc='upper center',ncol=3,frameon=False);fig.tight_layout(rect=(0,0,1,.96));outfig(fig,'Fig02_Finf_'+period)

# Gráficos de fator de infiltração por horário no treinamento.
tr=d[d.period.eq('train')].copy();tr['hour']=tr.timestamp.dt.hour;tr['bin3']=(tr.hour//3)*3
fig,axes=panels()
for i,r in enumerate(R):
 for j,f in enumerate(F):
  a=axes[i,j];g=tr[(tr.residence==r)&(tr.fraction==f)].groupby('bin3').finf.agg(['mean','std']).reindex(range(0,24,3));a.bar(np.arange(8),g['mean'],color=[BLUE,'#718ca0','#b97c50'][j]);a.errorbar(np.arange(8),g['mean'],yerr=g['std'],fmt='none',ecolor='#444',capsize=2,lw=.7);a.set_ylim(0,1.15);a.set_title(f'{r} / {pretty[f]}');a.set_xticks(range(8),[f'{h:02d}' for h in range(0,24,3)])
  if j==0:a.set_ylabel(r'Mean $F_{inf}$')
  if i==2:a.set_xlabel('Start of 3-hour interval')
fig.tight_layout();outfig(fig,'Fig03_Finf_3hour_training')
fig,axes=plt.subplots(1,3,figsize=(8.1,3.2),sharey=True)
for i,r in enumerate(R):
 a=axes[i]
 for j,f in enumerate(F):
  g=tr[(tr.residence==r)&(tr.fraction==f)]
  for z,day in enumerate((True,False)):
   q=g[(g.hour.ge(6)&g.hour.le(21))==day].finf;a.bar(j+(z-.5)*.36,q.mean(),width=.36,color=[BLUE,'#7190a4'][z],label=['Day','Night'][z] if j==0 else None);a.errorbar(j+(z-.5)*.36,q.mean(),yerr=q.std(),fmt='none',ecolor='#444',capsize=2,lw=.7)
 a.set_title(r);a.set_xticks(range(3),[pretty[f] for f in F]);a.set_ylim(0,1.15)
axes[0].set_ylabel(r'Mean $F_{inf}$');axes[0].legend(frameon=False);fig.tight_layout();outfig(fig,'Fig04_Finf_day_night_training')

fig,axes=panels()
for i,r in enumerate(R):
 for j,f in enumerate(F):
  a=axes[i,j];g=pd.read_csv(IN/'optuna'/f'{r}_{f.replace(".","")}_B_learning_curves.csv');
  for _,s in g.groupby('seed'):a.plot(s.epoch,s.train_RMSE_A,color=ORANGE,lw=.5,alpha=.3);a.plot(s.epoch,s.validation_RMSE,color=GREEN,lw=.5,alpha=.3)
  s=g.groupby('epoch')[['train_RMSE_A','validation_RMSE']].median();a.plot(s.index,s.train_RMSE_A,color=ORANGE,lw=1.4);a.plot(s.index,s.validation_RMSE,color=GREEN,lw=1.4);a.set_title(f'{r} / {pretty[f]}')
  if i==2:a.set_xlabel('Epoch')
  if j==0:a.set_ylabel(r'RMSE ($\mu$g m$^{-3}$)')
fig.legend([Line2D([0],[0],color=ORANGE),Line2D([0],[0],color=GREEN)],['Training (one step)','Validation'],loc='upper center',ncol=2,frameon=False);fig.tight_layout(rect=(0,0,1,.96));outfig(fig,'Fig05_learning_curves_3seeds')

for model,num in [('hybrid','06'),('mbm','07')]:
 for r in R:
  fig,axes=plt.subplots(1,3,figsize=(8.1,3.0))
  for j,f in enumerate(F):
   a=axes[j];ranges=[]
   for period,color in [('train',ORANGE),('test',GREEN if model=='hybrid' else BLUE)]:
    g=d[(d.residence==r)&(d.fraction==f)&(d.period==period)];x=g[model].to_numpy();y=g.observed.to_numpy();a.scatter(x,y,s=3,c=color,alpha=.45,rasterized=True);rr=r2(y,x);a.text(.04,.96-(0 if period=='train' else .10),f'$R^2_{{{period}}}$ = {rr:.3f}',transform=a.transAxes,va='top',fontsize=7)
    if np.ptp(x)>0:
     l=np.array([np.min(x),np.max(x)]);a.plot(l,np.polyval(np.polyfit(x,y,1),l),color=color,lw=1)
    ranges.extend([x.min(),x.max(),y.min(),y.max()])
   lo=min(0,min(ranges));hi=max(ranges)*1.04;a.plot([lo,hi],[lo,hi],'k--',lw=.8);a.set_xlim(lo,hi);a.set_ylim(lo,hi);a.set_aspect('equal');a.set_title(pretty[f]);a.set_xlabel(r'Modelled ($\mu$g m$^{-3}$)')
   if j==0:a.set_ylabel(r'Measured corrected ($\mu$g m$^{-3}$)')
  fig.suptitle(f'{r} | {"MBM + MLP" if model=="hybrid" else "MBM"} | Protocol B')
  test_color=GREEN if model=='hybrid' else BLUE
  fig.legend([Line2D([0],[0],marker='o',ls='',color=ORANGE),Line2D([0],[0],color=ORANGE),Line2D([0],[0],marker='o',ls='',color=test_color),Line2D([0],[0],color=test_color),Line2D([0],[0],color='black',ls='--')],['Training','Training regression','Test','Test regression','1:1'],loc='lower center',ncol=5,frameon=False,fontsize=7)
  fig.tight_layout(rect=(0,.09,1,.94));outfig(fig,f'Fig{num}_dispersao_{r}_{model}')

rows=[]
for r in R:
 for f in F:
  g=d[(d.residence==r)&(d.fraction==f)&(d.period=='test')];y=g.observed.to_numpy();span=np.ptp(y)
  for model in ('mbm','hybrid'):
   pred=g[model].to_numpy();rmse=np.sqrt(np.mean((pred-y)**2));rows.append({'residence':r,'fraction':f,'model':'MBM' if model=='mbm' else 'MBM+MLP','n':len(g),'RMSE':rmse,'MAE':np.mean(np.abs(pred-y)),'R2':r2(y,pred),'NRMSE_range_percent':100*rmse/span})
metrics=pd.DataFrame(rows);metrics.to_csv(TAB/'Tabela06_metricas_teste_protocolo_B.csv',index=False)
wide=metrics.pivot(index=['residence','fraction'],columns='model',values=['RMSE','MAE','R2']);wide.columns=[f'{metric}_{model}' for metric,model in wide.columns];wide=wide.reset_index();wide['fraction']=pd.Categorical(wide.fraction,categories=F,ordered=True);wide.sort_values(['residence','fraction']).to_csv(TAB/'Tabela06_comparacao_modelos_B.csv',index=False)
fig,ax=plt.subplots(figsize=(7.8,4.8));ix=np.arange(9)
for i,model in enumerate(('MBM','MBM+MLP')):
 a=metrics[metrics.model.eq(model)].reset_index(drop=True);ax.barh(ix+(i-.5)*.35,a.NRMSE_range_percent,height=.35,color=[BLUE,GREEN][i],label=model)
 for y,v in zip(ix+(i-.5)*.35,a.NRMSE_range_percent):ax.text(v+.06,y,f'{v:.2f}',va='center',fontsize=7)
ax.set_yticks(ix,[f'{r} / {pretty[f]}' for r in R for f in F]);ax.invert_yaxis();ax.set_xlabel('Range-normalized RMSE (%)');ax.set_xlim(0,metrics.NRMSE_range_percent.max()*1.2);ax.legend(frameon=False,loc='lower right');fig.tight_layout();outfig(fig,'Fig08_NRMSE_range_test_B')

fig,axes=panels()
for i,r in enumerate(R):
 for j,f in enumerate(F):
  a=axes[i,j];g=d[(d.residence==r)&(d.fraction==f)].sort_values('row_index')
  for period,color in [('validation','#f5dab2'),('test','#dedede')]:
   b=g[g.period.eq(period)];a.axvspan(b.row_index.min(),b.row_index.max(),color=color,alpha=.6,lw=0)
  for period in ('train','validation','test'):
   s=g[g.period.eq(period)]
   for col,color in [('observed',BLACK),('mbm',BLUE),('hybrid',GREEN)]:a.plot(s.row_index,s[col],color=color,lw=.6)
  a.set_title(f'{r} / {pretty[f]}');axes_label(a,i,j)
fig.legend([Line2D([0],[0],color=BLACK),Line2D([0],[0],color=BLUE),Line2D([0],[0],color=GREEN),Patch(color='#f5dab2'),Patch(color='#dedede')],['Measured (corrected)','MBM','MBM + MLP','Validation','Test'],loc='upper center',ncol=5,frameon=False);fig.tight_layout(rect=(0,0,1,.96));outfig(fig,'Fig09_serie_concentracao_B')
fig,axes=panels()
for i,r in enumerate(R):
 for j,f in enumerate(F):
  a=axes[i,j];g=d[(d.residence==r)&(d.fraction==f)&(d.period=='test')];e1=(g.mbm-g.observed).to_numpy();e2=(g.hybrid-g.observed).to_numpy();bins=np.histogram_bin_edges(np.r_[e1,e2],bins='fd');a.hist(e1,bins=bins,density=True,histtype='step',color=BLUE,lw=1);a.hist(e2,bins=bins,density=True,histtype='step',color=GREEN,lw=1);a.axvline(0,color='#555',lw=.5);a.set_title(f'{r} / {pretty[f]}')
  if i==2:a.set_xlabel(r'Residual ($\mu$g m$^{-3}$)')
  if j==0:a.set_ylabel('Density')
fig.legend([Line2D([0],[0],color=BLUE),Line2D([0],[0],color=GREEN)],['MBM','MBM + MLP'],loc='upper center',ncol=2,frameon=False);fig.tight_layout(rect=(0,0,1,.96));outfig(fig,'Fig10_residuos_teste_B')

config=pd.read_csv(IN/'tabelas/configuracoes_optuna.csv');config[config.protocol.eq('B')].to_csv(TAB/'Tabela05_configuracoes_B.csv',index=False)
ab=pd.read_csv(IN/'tabelas/ablacao_media_DP_IC95.csv');ab[ab.protocol.eq('B')].to_csv(TAB/'Ablacao_por_variavel_disponivel_B.csv',index=False)
print('CONCLUIDO',flush=True)
