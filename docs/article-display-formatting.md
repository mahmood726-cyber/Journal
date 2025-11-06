# Article Display & Formatting - Like NEJM & Lancet

## 🎯 What NEJM & Lancet Do Well

### **NEJM (New England Journal of Medicine):**
- Custom formatted tables with zebra striping
- "Key Points" panels at the beginning
- "Clinical Implications" boxes
- Beautiful figure captions
- References formatted inline
- Supplementary materials section
- Related articles sidebar

### **Lancet:**
- "Panel" boxes for key information
- "Research in Context" section
- Stunning data visualizations
- Author contributions section
- Funding acknowledgments
- Interactive figures
- Video abstracts

### **Both Have:**
- Clean typography
- Structured sections (IMRaD)
- Visual hierarchy
- PDF and HTML versions
- Citation tools
- Sharing options
- Metrics display

---

## 🚀 Our Article Display System (Better Than Both!)

### 1. **Article Reader Layout**

```
┌─────────────────────────────────────────────────────┐
│ STICKY HEADER                                        │
│ [Logo] Journal Name    [Download] [Cite] [Share]    │
└─────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────────────┐
│ SIDEBAR (Sticky)     │ MAIN ARTICLE                 │
│                      │                              │
│ Table of Contents    │  Article Title               │
│ • Abstract           │  Full Title of Research      │
│ • Introduction       │  Paper Goes Here             │
│ • Methods            │  ━━━━━━━━━━━━━━━━━━━━━━━━   │
│ • Results            │                              │
│ • Discussion         │  Authors:                    │
│ • References         │  John M. Smith¹*, Jane Doe²  │
│                      │                              │
│ Figures (Jump to)    │  ¹Harvard University         │
│ • Figure 1           │  ²MIT                        │
│ • Figure 2           │  *Corresponding author       │
│ • Table 1            │                              │
│                      │  ┌──────────────────────────┐│
│ Metrics              │  │ 📊 Key Points            ││
│ Views: 1,234         │  │                          ││
│ Downloads: 456       │  │ • Finding 1...           ││
│ Citations: 12        │  │ • Finding 2...           ││
│ Altmetric: 45        │  │ • Implication...         ││
│                      │  └──────────────────────────┘│
│ Actions              │                              │
│ [📥 Download PDF]    │  Abstract                    │
│ [📋 Cite Article]    │  ━━━━━━━━━━━━━━━━━━━━━━━━   │
│ [🔗 Share]           │  Background: This study...   │
│ [💾 Save]            │                              │
│ [📧 Email]           │  Methods: We conducted...    │
│                      │                              │
│ Related Articles     │  Results: Our findings...    │
│ • Similar paper 1    │                              │
│ • Similar paper 2    │  Conclusions: We conclude... │
│                      │                              │
└──────────────────────┴──────────────────────────────┘
```

---

### 2. **Custom Panels (Like NEJM/Lancet)**

#### **A. Key Points Panel** (Article Beginning)
```
┌─────────────────────────────────────────────────────┐
│ 📊 KEY POINTS                                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│ • We found that treatment A is 40% more effective   │
│   than treatment B in reducing symptoms.            │
│                                                      │
│ • Patients showed significant improvement within    │
│   the first 2 weeks of treatment.                   │
│                                                      │
│ • Side effects were minimal and well-tolerated.     │
│                                                      │
│ • This approach could change clinical practice for  │
│   managing this condition.                          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### **B. Research in Context Panel** (Like Lancet)
```
┌─────────────────────────────────────────────────────┐
│ 🔬 RESEARCH IN CONTEXT                               │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Evidence Before This Study                          │
│ Previous research has shown that...                 │
│                                                      │
│ Added Value of This Study                           │
│ Our study uniquely contributes by...                │
│                                                      │
│ Implications of All Available Evidence              │
│ These findings suggest that...                      │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### **C. Clinical Implications Panel** (Like NEJM)
```
┌─────────────────────────────────────────────────────┐
│ 🏥 CLINICAL IMPLICATIONS                             │
├─────────────────────────────────────────────────────┤
│                                                      │
│ What This Means for Clinicians:                     │
│ • Patients with X condition should be evaluated for │
│   Y before starting treatment.                      │
│                                                      │
│ • Monitoring Z levels weekly is recommended for the │
│   first month.                                      │
│                                                      │
│ What This Means for Patients:                       │
│ • This new treatment option may offer better        │
│   outcomes with fewer side effects.                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

#### **D. Quick Summary Box**
```
┌─────────────────────────────────────────────────────┐
│ ⚡ AT A GLANCE                                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Study Design:    Randomized Controlled Trial        │
│ Sample Size:     n = 500 patients                   │
│ Duration:        24 weeks                           │
│ Primary Outcome: Symptom reduction score            │
│ Result:          40% improvement (p < 0.001)        │
│ Conclusion:      Treatment A significantly better   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### 3. **Tables (NEJM-Style)**

#### **Standard Table:**
```
┌─────────────────────────────────────────────────────┐
│ Table 1. Baseline Characteristics of Study          │
│ Participants                                         │
├─────────────────────┬────────────┬──────────────────┤
│ Characteristic      │ Group A    │ Group B          │
│                     │ (n=250)    │ (n=250)          │
├─────────────────────┼────────────┼──────────────────┤
│ Age, years          │ 45.2 ±12.1 │ 44.8 ±11.9      │
│                     │            │                  │
│ Sex, no. (%)        │            │                  │
│   Male              │ 150 (60)   │ 145 (58)        │
│   Female            │ 100 (40)   │ 105 (42)        │
│                     │            │                  │
│ BMI, kg/m²          │ 27.3 ±4.2  │ 26.9 ±4.5       │
│                     │            │                  │
│ Comorbidities, %    │            │                  │
│   Diabetes          │ 35         │ 32              │
│   Hypertension      │ 48         │ 45              │
│   Smoking           │ 22         │ 25              │
└─────────────────────┴────────────┴──────────────────┘
Plus-minus values are means ±SD. There were no
significant differences between groups (P>0.05 for all).
```

#### **Results Table with Styling:**
```
┌─────────────────────────────────────────────────────┐
│ Table 2. Primary and Secondary Outcomes              │
├─────────────────┬──────────┬──────────┬─────────────┤
│ Outcome         │ Group A  │ Group B  │ P Value     │
├─────────────────┼──────────┼──────────┼─────────────┤
│ Primary Outcome │          │          │             │
│ Symptom Score   │ 18.2±4.1 │ 29.5±5.2 │ <0.001 ***  │ ← Highlighted
│                 │          │          │             │
│ Secondary       │          │          │             │
│ Quality of Life │ 78.3±9.2 │ 65.1±11.3│ <0.001 ***  │
│ Sleep Quality   │ 7.2±1.5  │ 5.8±1.8  │  0.002 **   │
│ Pain Level      │ 3.1±0.9  │ 4.8±1.2  │ <0.001 ***  │
│                 │          │          │             │
│ Adverse Events  │          │          │             │
│ Mild            │ 15 (6%)  │ 18 (7%)  │  0.52       │
│ Moderate        │ 5 (2%)   │ 8 (3%)   │  0.39       │
│ Severe          │ 1 (<1%)  │ 2 (<1%)  │  0.56       │
└─────────────────┴──────────┴──────────┴─────────────┘
*** P<0.001; ** P<0.01; * P<0.05
```

---

### 4. **Figures (Interactive & Beautiful)**

#### **Figure Display:**
```
┌─────────────────────────────────────────────────────┐
│ Figure 1. Treatment Response Over Time               │
│                                                      │
│ ┌──────────────────────────────────────────────────┐│
│ │                                                   ││
│ │     [Interactive Chart/Graph Here]               ││
│ │                                                   ││
│ │     📊 Hover for details                         ││
│ │     🔍 Click to enlarge                          ││
│ │     💾 Download (PNG, SVG, PDF)                  ││
│ │                                                   ││
│ └──────────────────────────────────────────────────┘│
│                                                      │
│ Panel A shows symptom scores at baseline, 4 weeks,  │
│ 12 weeks, and 24 weeks for both treatment groups.   │
│ Error bars indicate 95% confidence intervals. The   │
│ asterisks indicate significant differences between   │
│ groups (*P<0.05, **P<0.01, ***P<0.001).            │
│                                                      │
│ [View Full Size] [Download Data] [Cite Figure]      │
└─────────────────────────────────────────────────────┘
```

#### **Multi-Panel Figure:**
```
┌─────────────────────────────────────────────────────┐
│ Figure 2. Mechanistic Analysis                       │
│                                                      │
│ ┌──────────────────┬───────────────────────────────┐│
│ │                  │                               ││
│ │  Panel A         │  Panel B                      ││
│ │  [Western Blot]  │  [Cell Images]                ││
│ │                  │                               ││
│ ├──────────────────┴───────────────────────────────┤│
│ │                                                   ││
│ │  Panel C                                          ││
│ │  [Flow Cytometry Plot]                            ││
│ │                                                   ││
│ └───────────────────────────────────────────────────┘│
│                                                      │
│ (A) Protein expression levels... (B) Representative │
│ microscopy images... (C) Quantification of...       │
└─────────────────────────────────────────────────────┘
```

---

### 5. **Supplementary Materials**

```
┌─────────────────────────────────────────────────────┐
│ 📎 SUPPLEMENTARY MATERIALS                           │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Supplementary Appendix                               │
│ [📄 PDF] [📥 Download] (2.4 MB)                     │
│ Additional methods, results, and discussion.         │
│                                                      │
│ Supplementary Tables                                 │
│ [📊 Table S1] Demographics by site                  │
│ [📊 Table S2] Full regression analysis results      │
│ [📊 Table S3] Subgroup analyses                     │
│                                                      │
│ Supplementary Figures                                │
│ [📈 Figure S1] Individual patient trajectories      │
│ [📈 Figure S2] Sensitivity analyses                 │
│ [📈 Figure S3] Forest plot of effect sizes          │
│                                                      │
│ Data Sharing                                         │
│ [💾 Dataset] De-identified participant data         │
│ [📜 Code] Statistical analysis scripts (GitHub)     │
│ [📋 Protocol] Study protocol (PDF)                  │
│                                                      │
│ Video Abstract                                       │
│ [▶️ Watch] 3-minute summary by lead author          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### 6. **References Section (Interactive)**

```
┌─────────────────────────────────────────────────────┐
│ REFERENCES                                           │
├─────────────────────────────────────────────────────┤
│                                                      │
│ 1. Smith J, Doe J, Johnson R. Title of referenced   │
│    article. Journal Name. 2023;45(2):123-134.       │
│    doi:10.1234/journal.2023.123                     │
│    [PubMed] [Google Scholar] [Crossref]             │
│    📊 Cited by: 145                                  │
│                                                      │
│ 2. Brown A, Green B, White C, et al. Another        │
│    important study. Nature. 2022;500:456-467.       │
│    doi:10.1038/nature.2022.456                      │
│    [PubMed] [Google Scholar] [Crossref]             │
│    📊 Cited by: 892                                  │
│                                                      │
│ 3. Lee S, Park M, Kim H. Recent findings in the     │
│    field. Science. 2024;380:789-801.                │
│    doi:10.1126/science.2024.789                     │
│    [PubMed] [Google Scholar] [Crossref]             │
│    📊 Cited by: 23                                   │
│                                                      │
│ [Show All 45 References]                             │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### 7. **Author Contributions & Disclosures**

```
┌─────────────────────────────────────────────────────┐
│ 👥 AUTHOR CONTRIBUTIONS                              │
├─────────────────────────────────────────────────────┤
│                                                      │
│ J.M.S.: Conceptualization, methodology, writing -   │
│ original draft, supervision.                         │
│                                                      │
│ J.D.: Data curation, formal analysis, visualization.│
│                                                      │
│ R.K.J.: Investigation, resources, validation.       │
│                                                      │
│ All authors reviewed and approved the final version. │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ 💰 FUNDING                                           │
├─────────────────────────────────────────────────────┤
│                                                      │
│ This work was supported by the National Institutes  │
│ of Health (grants R01-HL123456 and P01-CA987654)    │
│ and the American Heart Association (grant 12345).   │
│                                                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│ ⚖️ DISCLOSURES                                       │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Dr. Smith reports consulting fees from PharmaCo and │
│ speaking fees from MedTech Inc., outside the        │
│ submitted work. Other authors declare no competing  │
│ interests.                                           │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### 8. **Metrics Dashboard (In Article)**

```
┌─────────────────────────────────────────────────────┐
│ 📊 ARTICLE METRICS                                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│ ┌──────────┬──────────┬──────────┬──────────┐      │
│ │ 👁 Views │ 📥 PDF   │ 📖 Cited │ 💬 Social│      │
│ │          │          │          │          │      │
│ │  1,234   │   456    │    12    │    45    │      │
│ └──────────┴──────────┴──────────┴──────────┘      │
│                                                      │
│ Altmetric Score: 45  [🔷 View Details]              │
│                                                      │
│ Published: January 15, 2025                          │
│ Accepted: December 1, 2024                           │
│ Received: October 10, 2024                           │
│                                                      │
│ Processing Time: 52 days                             │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

### 9. **Citation Tools**

```
┌─────────────────────────────────────────────────────┐
│ 📋 CITE THIS ARTICLE                                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│ Format: [APA ▾] [MLA] [Chicago] [Harvard]          │
│                                                      │
│ Smith JM, Doe J, Johnson RK. Title of the article.  │
│ Journal of Advanced Science. 2025;5(2):123-134.     │
│ doi:10.1234/jas.2025.123                            │
│                                                      │
│ [📋 Copy Citation] [📥 Download RIS] [📚 EndNote]   │
│                                                      │
│ DOI: 10.1234/jas.2025.123                           │
│ [Copy DOI] [Generate QR Code]                       │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🎨 Styling Examples

### Typography System:
```css
/* Heading Hierarchy */
h1.article-title {
  font-family: 'Merriweather', serif;
  font-size: 32px;
  font-weight: 700;
  line-height: 1.3;
  color: #1a1a1a;
  margin-bottom: 24px;
}

h2.section-heading {
  font-family: 'Merriweather', serif;
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-top: 40px;
  margin-bottom: 16px;
  border-bottom: 2px solid #3498db;
  padding-bottom: 8px;
}

p.body-text {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  margin-bottom: 16px;
  text-align: justify;
}
```

### Panel Styles:
```css
.key-points-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 24px;
  border-radius: 12px;
  margin: 32px 0;
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.clinical-panel {
  background: #f0f9ff;
  border-left: 4px solid #3b82f6;
  padding: 20px;
  margin: 24px 0;
  border-radius: 8px;
}

.research-context-panel {
  background: #fef3c7;
  border: 2px solid #f59e0b;
  padding: 20px;
  border-radius: 8px;
  margin: 24px 0;
}
```

### Table Styles:
```css
.nejm-table {
  width: 100%;
  border-collapse: collapse;
  margin: 32px 0;
  font-family: 'Inter', sans-serif;
  font-size: 14px;
}

.nejm-table thead {
  background: #2c3e50;
  color: white;
}

.nejm-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
}

.nejm-table tbody tr:nth-child(even) {
  background: #f8f9fa;
}

.nejm-table td {
  padding: 10px 12px;
  border-bottom: 1px solid #dee2e6;
}

.nejm-table .significant {
  background: #fff3cd;
  font-weight: 600;
}
```

---

## 📱 Responsive Design

### Desktop (>1200px):
- Sidebar + main content
- Large figures
- Multi-column layouts
- Sticky TOC

### Tablet (768px - 1200px):
- Collapsible sidebar
- Single column
- Scaled figures
- Floating TOC button

### Mobile (<768px):
- Full-width content
- No sidebar
- Stacked figures
- Bottom navigation
- Simplified tables (horizontal scroll)

---

## 🎯 Interactive Features

### 1. **Live Citations**
Click reference number → Tooltip shows full citation
```
"Previous studies have shown[1,2]..."
         Click → ┌───────────────────────┐
                 │ Smith et al. Nature   │
                 │ 2023;500:123-134      │
                 │ [View] [Cite]        │
                 └───────────────────────┘
```

### 2. **Figure Zoom**
Click figure → Full-screen lightbox with annotations

### 3. **Table Sorting**
Click column header → Sort table data

### 4. **Highlight & Annotate**
Select text → Highlight, note, share

### 5. **Audio Abstract**
🔊 Listen to AI-generated audio summary

---

## 🆚 Comparison

| Feature | OJS | NEJM | Lancet | Our System |
|---------|-----|------|--------|------------|
| **Custom Panels** | ❌ | ✅ | ✅ | ✅ Better |
| **Table Formatting** | Basic | ✅ | ✅ | ✅ Interactive |
| **Figure Display** | Basic | ✅ | ✅ | ✅ + Zoom |
| **TOC Sidebar** | ❌ | ✅ | ✅ | ✅ Sticky |
| **Citation Tools** | Basic | ✅ | ✅ | ✅ + More |
| **Metrics** | Basic | ⚠️ | ⚠️ | ✅ Live |
| **Responsive** | Poor | ⚠️ | ⚠️ | ✅ Perfect |
| **Accessibility** | Poor | ⚠️ | ⚠️ | ✅ WCAG 2.1 |

---

## 💡 Bottom Line

**OJS Articles:** Basic HTML, looks like blog post
**NEJM/Lancet:** Professional, but static PDFs
**Our System:** Best of both + interactive + modern

We're taking the best from NEJM and Lancet, making it interactive and responsive, all rendered beautifully in HTML!
