import docx
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
import copy

def process_document(docx_path):
    print(f"Opening document: {docx_path}")
    doc = docx.Document(docx_path)
    
    # 1. Fix stretched lines by splitting paragraphs at w:br
    paras_to_split = []
    for p in doc.paragraphs:
        if p._element.xpath('.//w:br'):
            paras_to_split.append(p)
            
    print(f"Splitting {len(paras_to_split)} paragraphs with line breaks...")
    for p in paras_to_split:
        p_elem = p._element
        parent = p_elem.getparent()
        p_idx = parent.index(p_elem)
        pPr = p_elem.find(qn('w:pPr'))
        
        paragraphs_elems = []
        cur_p = OxmlElement('w:p')
        if pPr is not None:
            cur_p.append(copy.deepcopy(pPr))
        paragraphs_elems.append(cur_p)
        
        for child in list(p_elem):
            if child.tag == qn('w:pPr'):
                continue
            
            br_elems = child.xpath('.//w:br')
            if not br_elems:
                cur_p.append(child)
            else:
                for br in br_elems:
                    br.getparent().remove(br)
                new_p = OxmlElement('w:p')
                if pPr is not None:
                    new_p.append(copy.deepcopy(pPr))
                paragraphs_elems.append(new_p)
                cur_p = new_p
                cur_p.append(child)
                
        for new_p in paragraphs_elems:
            parent.insert(p_idx, new_p)
            p_idx += 1
        parent.remove(p_elem)
        
    # 2. Add dynamic page numbering to footer
    print("Configuring dynamic page numbers in footer...")
    section = doc.sections[0]
    footer = section.footer
    fp = footer.paragraphs[0]
    fp.clear()
    
    run_text = fp.add_run("Trang ")
    run_text.font.name = "Times New Roman"
    run_text.font.size = docx.shared.Pt(9)
    run_text.font.color.rgb = docx.shared.RGBColor(100, 100, 100)
    
    fld_xml = (
        r'<w:fldSimple %s w:instr="PAGE">'
        r'<w:r>'
        r'<w:rPr>'
        r'<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
        r'<w:sz w:val="18"/>'
        r'<w:color w:val="646464"/>'
        r'</w:rPr>'
        r'<w:t>1</w:t>'
        r'</w:r>'
        r'</w:fldSimple>'
    ) % nsdecls('w')
    fp._element.append(parse_xml(fld_xml))
    
    # 3. Enable updateFields in settings
    try:
        element = doc.settings.element
        update_fields = parse_xml(r'<w:updateFields %s w:val="true"/>' % nsdecls('w'))
        element.append(update_fields)
    except Exception as e:
        print("Note on settings:", e)
        
    doc.save(docx_path)
    print("Successfully saved updated document!")

if __name__ == '__main__':
    process_document('Bao_Cao_Khoa_Hoc_Springer_Nature.docx')
