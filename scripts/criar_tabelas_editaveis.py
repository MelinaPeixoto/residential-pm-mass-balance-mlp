from pathlib import Path
import pandas as pd
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

root=Path(__file__).resolve().parent.parent;tab=root/'substituicoes_artigo'/'tabelas';doc=Document();sec=doc.sections[0];sec.orientation=WD_ORIENT.LANDSCAPE;sec.page_width=Inches(11);sec.page_height=Inches(8.5);sec.left_margin=Cm(2);sec.right_margin=Cm(2);sec.top_margin=Cm(2);sec.bottom_margin=Cm(2)
normal=doc.styles['Normal'];normal.font.name='Times New Roman';normal.font.size=Pt(10)
for name in ['Title','Heading 1']:
 s=doc.styles[name];s.font.name='Times New Roman';s.font.color.rgb=RGBColor(0,0,0)
title=doc.add_heading('Tables for the R5 to R7 three-seed analysis',0)
borders=OxmlElement('w:pBdr');bottom=OxmlElement('w:bottom');bottom.set(qn('w:val'),'nil');borders.append(bottom);title._p.get_or_add_pPr().append(borders)
doc.add_paragraph('Protocol B. Predictions and configurations are from the archived three-seed execution; bootstrap-based quantities were extended from 600 to 1,000 paired replicates.')
def table(title,headers,rows):
 doc.add_heading(title,level=1);t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER
 for c,s in zip(t.rows[0].cells,headers):c.text=str(s)
 for row in rows:
  for c,v in zip(t.add_row().cells,row):c.text=str(v)
 for rr in t.rows:
  for c in rr.cells:
   for p in c.paragraphs:
    p.paragraph_format.space_after=Pt(0)
    for run in p.runs:run.font.name='Times New Roman';run.font.size=Pt(10);run.font.color.rgb=RGBColor(0,0,0)
 for c in t.rows[0].cells:
  for p in c.paragraphs:
   for run in p.runs:run.bold=True
def f(v):return f'{float(v):.3f}'
b=pd.read_csv(tab/'Tabela03_Finf_artigo_1000.csv');rows=[]
for _,x in b.iterrows():
 mb=f"{f(x.Finf_MBM_original)} ± {f(x.Finf_MBM_SD)} [{f(x.Finf_MBM_CI95_lower)}, {f(x.Finf_MBM_CI95_upper)}]"
 hy=f"{f(x.Finf_MLP_original)} ± {f(x.Finf_MLP_SD)} [{f(x.Finf_MLP_CI95_lower)}, {f(x.Finf_MLP_CI95_upper)}]"
 rows.append((x.residence,x.fraction,mb,hy,f'{x.delta_original:+.3f}',f(x.p_holm_9)))
table('Table 3 Infiltration factor estimates and bootstrap uncertainty',['Residence','Fraction','MBM estimate ± SD [95% CI]','MBM + MLP estimate ± SD [95% CI]','MBM − hybrid','p Holm'],rows)
doc.add_paragraph('SD and percentile intervals refer to 1,000 moving-block bootstrap replicates, not to the temporal SD. Estimates are based on the development period. The hybrid point estimate averages the temporal means across three seeds. Inference is conditional on the event correction and selected configuration.')
doc.add_page_break();config=pd.read_csv(tab/'Tabela05_configuracoes_B.csv');rows=[]
for _,x in config.iterrows():rows.append((x.residence,x.fraction,f'{int(x.hidden)} / {int(x.hidden)}',f'{x.dropout:.2f}',f'{x.lr:.6f}',f'{x.weight_decay:.2g}',int(x.epochs)))
table('Table 5 Selected model configurations',['Residence','Fraction','Hidden layers','Dropout','Learning rate','Weight decay','Refit epochs'],rows)
doc.add_paragraph('The archived network has two hidden layers of the same width. The original training loss used one-step predictions; protocol B was used in validation. The values shown are the archived selected configurations, not the different architecture formerly described in the manuscript.')
doc.add_page_break();m=pd.read_csv(tab/'Tabela06_comparacao_modelos_B.csv');rows=[]
for _,x in m.iterrows():rows.append((x['residence'],x['fraction'],*[f(x[k]) for k in ('RMSE_MBM','RMSE_MBM+MLP','MAE_MBM','MAE_MBM+MLP','R2_MBM','R2_MBM+MLP')]))
table('Table 6 Test performance under protocol B',['Residence','Fraction','RMSE MBM','RMSE hybrid','MAE MBM','MAE hybrid','R² MBM','R² hybrid'],rows)
doc.add_paragraph('RMSE and MAE are expressed in µg m⁻³. Hybrid metrics are calculated after averaging the three predictions at each test observation. The reference concentration was corrected retrospectively; the test period had been inspected in earlier analyses.')
doc.save(tab/'Tabelas_03_05_06_editaveis.docx')
print(tab/'Tabelas_03_05_06_editaveis.docx')
